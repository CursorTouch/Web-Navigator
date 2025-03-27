from src.agent.web.dom.views import DOMElementNode, DOMState, CenterCord, BoundingBox
from playwright.async_api import Frame,Page
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.agent.web.context import Context

class DOM:
    def __init__(self, context:'Context'):
        self.context=context

    async def get_state(self,use_vision:bool=False)->tuple[str|None,DOMState]:
        '''Get the state of the webpage.'''
        with open('./src/agent/web/dom/script.js') as f:
                script=f.read()
        try:
            nodes=[]
            interactive_elements=[]
            page=await self.context.get_current_page()
            # Loading the script
            await self.context.execute_script(page,script)
            interactive_elements.extend(await self.context.execute_script(page,'getInteractiveElements()'))
            frames=page.frames
            frames.pop(0)
            try:
                for frame in frames:
                    width,height=await self.get_dimensions(frame)
                    frame_area=width*height
                    if frame_area<100 or frame.is_detached():
                        continue
                    await self.context.execute_script(frame,script)
                    interactive_elements.extend(await self.context.execute_script(frame,'getInteractiveElements()'))
            except Exception as e:
                print(e)
            if use_vision:
                # Add bounding boxes to the interactive elements
                await self.context.execute_script(page,'interactive_elements=>{mark_page(interactive_elements)}',interactive_elements)
                screenshot=await self.context.get_screenshot(save_screenshot=False)
                # Remove bounding boxes from the interactive elements
                await self.context.execute_script(page,'unmark_page()')
            else:
                screenshot=None
            for element in interactive_elements:
                node=DOMElementNode(**{
                    'tag':element.get('tag'),
                    'role':element.get('role'),
                    'name':element.get('name'),
                    'attributes':element.get('attributes'),
                    'center':CenterCord(**element.get('center')),
                    'bounding_box':BoundingBox(**element.get('box')),
                })
                nodes.append(node)
        except Exception as e:
            print(e)
            nodes=[]
            screenshot=None
        # print(nodes)
        return (screenshot,DOMState(nodes=nodes))
    
    async def get_dimensions(self,obj:Frame|Page)->tuple[int,int]:
        if isinstance(obj,Frame):
            width=await self.context.execute_script(obj,'window.frameElement?.offsetWidth')
            height=await self.context.execute_script(obj,'window.frameElement?.offsetHeight')
        elif isinstance(obj,Page):
            width=await self.context.execute_script(obj,'window.innerWidth')
            height=await self.context.execute_script(obj,'window.innerHeight')
        else:
            raise Exception('Object is not a Frame or Page')
        return (width,height)

