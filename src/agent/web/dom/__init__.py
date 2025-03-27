from src.agent.web.dom.views import DOMElementNode, DOMState, CenterCord, BoundingBox
from src.agent.web.context.config import IGNORED_URL_PATTERNS
from urllib.parse import urlparse
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
            await page.wait_for_load_state('domcontentloaded')
            # Loading the script
            await self.context.execute_script(page,script)
            elements=await self.context.execute_script(page,'getInteractiveElements()')
            interactive_elements.extend(elements)
            frames=page.frames
            # Delete the main frame
            frames.pop(0) 
            try:
                for frame in frames:
                    frame_element = await frame.frame_element()
                    bbox = await frame_element.bounding_box()
                    netloc=urlparse(frame.url).netloc # Deletes the about:blank & data: urls
                    if bbox is None or netloc=='':
                        continue
                    # print(netloc,bbox)
                    width,height=bbox['width'],bbox['height']
                    is_ad_url=any(netloc in pattern for pattern in IGNORED_URL_PATTERNS)
                    if (width<10 or height<10) or is_ad_url or frame.is_detached():
                        continue
                    await self.context.execute_script(frame,script)
                    elements=await self.context.execute_script(frame,'getInteractiveElements()')
                    interactive_elements.extend(elements)
            except Exception as e:
                print(f"Failed to get elements from frame: {frame.url}\nError: {e}")
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
            print(f"Failed to get elements from page: {page.url}\nError: {e}")
            nodes=[]
            screenshot=None
        # print(nodes)
        return (screenshot,DOMState(nodes=nodes))

