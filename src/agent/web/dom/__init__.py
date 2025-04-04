from src.agent.web.dom.views import DOMElementNode, DOMState, CenterCord, BoundingBox
from typing import TYPE_CHECKING
from asyncio import sleep

if TYPE_CHECKING:
    from src.agent.web.context import Context

class DOM:
    def __init__(self, context:'Context'):
        self.context=context

    async def get_state(self,use_vision:bool=False)->tuple[str|None,DOMState]:
        '''Get the state of the webpage.'''
        try:
            nodes:list[DOMElementNode]=[]
            selector_map={}
            with open('./src/agent/web/dom/script.js') as f:
                script=f.read()
            await sleep(5)
            page=await self.context.get_current_page()
            await page.wait_for_load_state('load')
            frames=page.frames
            try:
                for index,frame in enumerate(frames):
                    # print(f"Getting elements from frame: {frame.url}")
                    #index=0 means Main Frame
                    if index>0 and not await self.context.is_frame_visible(frame=frame):
                        continue
                    # print(f"Getting elements from frame: {frame.url}")
                    await self.context.execute_script(frame,script)
                    # await self.context.execute_script(frame,'injectAllCSS()')
                    # classes=await self.context.execute_script(frame,"""
                    #     (function () {
                    #         function getInteractiveClasses() {
                    #             const interactiveClasses = new Set();
                    #             for (const sheet of document.styleSheets) {
                    #                 try {
                    #                     for (const rule of sheet.cssRules) {
                    #                         if (!rule.selectorText) continue;
                    #                         // Check for cursor styles or pseudo-classes
                    #                         if (
                    #                             rule.cssText.includes("cursor:") ||
                    #                             rule.selectorText.includes(":hover") ||
                    #                             rule.selectorText.includes(":focus") ||
                    #                             rule.selectorText.includes(":active") ||
                    #                             rule.cssText.includes("animation") ||
                    #                             rule.cssText.includes("transition")
                    #                         ) {
                    #                             const classes = rule.selectorText.match(/\.[\w-]+/g); // Extract class names
                    #                             if (classes) {
                    #                                 classes.forEach(cls => interactiveClasses.add(cls.replace(".", ""))); // Store without '.'
                    #                             }
                    #                         }
                    #                     }
                    #                 } catch (e) {
                    #                     console.warn("Couldn't access stylesheet:", sheet.href);
                    #                 }
                    #             }
                    #             return [...interactiveClasses];
                    #         }

                    #         return getInteractiveClasses();
                    #     })();
                    # """)
                    elements=await self.context.execute_script(frame,'getInteractiveElements()')
                    if index>0:
                        frame_element =await frame.frame_element()
                        frame_xpath=await self.context.execute_script(page,'(frame_element)=>getXPath(frame_element)',frame_element)
                    else:
                        frame_xpath=''
                    for element in elements:
                        element_xpath=element.get('xpath')
                        node=DOMElementNode(**{
                            'tag':element.get('tag'),
                            'role':element.get('role'),
                            'name':element.get('name'),
                            'attributes':element.get('attributes'),
                            'center':CenterCord(**element.get('center')),
                            'bounding_box':BoundingBox(**element.get('box')),
                            'xpath':{'frame':frame_xpath,'element':element_xpath}
                        })
                        nodes.append(node)
            except Exception as e:
                print(f"Failed to get elements from frame: {frame.url}\nError: {e}")
            if use_vision:
                # Add bounding boxes to the interactive elements
                boxes=map(lambda node:node.bounding_box.to_dict(),nodes)
                await self.context.execute_script(page,'boxes=>{mark_page(boxes)}',list(boxes))
                screenshot=await self.context.get_screenshot(save_screenshot=False)
                # Remove bounding boxes from the interactive elements
                await sleep(2)
                await self.context.execute_script(page,'unmark_page()')
            else:
                screenshot=None
        except Exception as e:
            print(f"Failed to get elements from page: {page.url}\nError: {e}")
            nodes=[]
            screenshot=None
        selector_map=dict(enumerate(nodes))
        return (screenshot,DOMState(nodes=nodes,selector_map=selector_map))

