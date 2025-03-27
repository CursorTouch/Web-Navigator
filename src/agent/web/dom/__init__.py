from src.agent.web.dom.views import DOMElementNode, DOMState, CenterCord, BoundingBox
from playwright.async_api import Frame
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
            frame=page.main_frame
            async def traverse_frame(frame:Frame):
                if frame.is_detached():
                    return []
                await self.context.execute_script(frame,script)
                elements=list(await self.context.execute_script(frame,'getInteractiveElements()'))
                for child_frame in frame.child_frames:
                    elements.extend(await traverse_frame(child_frame))
                return elements
            interactive_elements=await traverse_frame(frame)
            print(interactive_elements)
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
