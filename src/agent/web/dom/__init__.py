from src.agent.web.dom.views import DOMElementNode, DOMTextualNode, ScrollElementNode, DOMState, CenterCord, BoundingBox
from playwright.async_api import Page, Frame
from typing import TYPE_CHECKING
from asyncio import sleep

if TYPE_CHECKING:
    from src.agent.web.context import Context

class DOM:
    def __init__(self, context:'Context'):
        self.context=context

    async def get_state(self,use_vision:bool=False,freeze:bool=False)->tuple[str|None,DOMState]:
        '''Get the state of the webpage.'''
        try:
            if freeze:
                await sleep(5)
            with open('./src/agent/web/dom/script.js') as f:
                script=f.read()
            page=await self.context.get_current_page()
            await page.wait_for_load_state('domcontentloaded',timeout=10*1000)
            await self.context.execute_script(page,script)
            #Access from frames
            frames=page.frames
            interactive_nodes,informative_nodes,scrollable_nodes=await self.get_elements(frames=frames)
            if use_vision:
                # Add bounding boxes to the interactive elements
                boxes=map(lambda node:node.bounding_box.to_dict(),interactive_nodes)
                await self.context.execute_script(page,'boxes=>{mark_page(boxes)}',list(boxes))
                screenshot=await self.context.get_screenshot(save_screenshot=False)
                # Remove bounding boxes from the interactive elements
                if freeze:
                    await sleep(10)
                await sleep(0.1)
                await self.context.execute_script(page,'unmark_page()')
            else:
                screenshot=None
        except Exception as e:
            print(f"Failed to get elements from page: {page.url}\nError: {e}")
            interactive_nodes,informative_nodes,scrollable_nodes=[],[],[]
            screenshot=None
        selector_map=dict(enumerate(interactive_nodes+scrollable_nodes))
        return (screenshot,DOMState(interactive_nodes=interactive_nodes,informative_nodes=informative_nodes,scrollable_nodes=scrollable_nodes,selector_map=selector_map))
    
    async def get_elements(self,frames:list[Frame|Page])->tuple[list[DOMElementNode],list[DOMTextualNode],list[ScrollElementNode]]:
        '''Get the interactive elements of the webpage.'''
        interactive_elements,informative_elements,scrollable_elements=[],[],[]
        with open('./src/agent/web/dom/script.js') as f:
            script=f.read()
        try:
            for index,frame in enumerate(frames):
                if frame.is_detached() or frame.url=='about:blank':
                    continue
                # print(f"Getting elements from frame: {frame.url}")
                await self.context.execute_script(frame,script)  # Inject JS
                #index=0 means Main Frame
                if index>0 and not await self.context.is_frame_visible(frame=frame):
                    continue
                # print(f"Getting elements from frame: {frame.url}")
                await self.context.execute_script(frame,script)
                nodes:dict=await self.context.execute_script(frame,'getElements()')
                element_nodes,textual_nodes,scrollable_nodes=nodes.values()
                if index>0:
                    frame_element =await frame.frame_element()
                    frame_xpath=await self.context.execute_script(frame,'(frame_element)=>getXPath(frame_element)',frame_element)
                else:
                    frame_xpath=''
                viewport =await self.context.get_viewport()
                for element in element_nodes:
                    element_xpath=element.get('xpath')
                    node=DOMElementNode(**{
                        'tag':element.get('tag'),
                        'role':element.get('role'),
                        'name':element.get('name'),
                        'attributes':element.get('attributes'),
                        'center':CenterCord(**element.get('center')),
                        'bounding_box':BoundingBox(**element.get('box')),
                        'xpath':{'frame':frame_xpath,'element':element_xpath},
                        'viewport':viewport
                    })
                    interactive_elements.append(node)

                for element in scrollable_nodes:
                    element_xpath=element.get('xpath')
                    node=ScrollElementNode(**{
                        'tag':element.get('tag'),
                        'role':element.get('role'),
                        'name':element.get('name'),
                        'attributes':element.get('attributes'),
                        'xpath':{'frame':frame_xpath,'element':element_xpath},
                        'viewport':viewport
                    })
                    scrollable_elements.append(node)
                
                for element in textual_nodes:
                    element_xpath=element.get('xpath')
                    node=DOMTextualNode(**{
                        'tag':element.get('tag'),
                        'role':element.get('role'),
                        'content':element.get('content'),
                        'center':CenterCord(**element.get('center')),
                        'xpath':{'frame':frame_xpath,'element':element_xpath},
                        'viewport':viewport
                    })
                    informative_elements.append(node)

        except Exception as e:
            print(f"Failed to get elements from frame: {frame.url}\nError: {e}")
        return interactive_elements,informative_elements,scrollable_elements
