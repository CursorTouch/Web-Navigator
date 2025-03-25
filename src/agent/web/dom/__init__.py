from src.agent.web.dom.views import DOMElementNode, DOMState, CenterCord, BoundingBox
from playwright.async_api import ElementHandle
from typing import TYPE_CHECKING
import asyncio

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
            # Loading the script
            await self.context.execute_script(script)
            # Get interactive elements
            nodes=await self.context.execute_script('getInteractiveElements()')
            # Add bounding boxes to the interactive elements
            if use_vision:
                await self.context.execute_script('nodes=>{mark_page(nodes)}',nodes)
                screenshot=await self.context.get_screenshot(save_screenshot=False)
                await self.context.execute_script('unmark_page()')
            else:
                screenshot=None
            selector_map=await self.build_selector_map(nodes)
        except Exception as e:
            print(e)
            nodes=[]
            screenshot=None
            selector_map={}
        return (screenshot,DOMState(nodes=list(selector_map.values()),selector_map=selector_map))


    async def build_selector_map(self, nodes: list[dict]) -> dict[int, tuple[DOMElementNode, ElementHandle]]:
        """Build a map from element index to node."""
        async def process_node(index: int, node: dict):
            handle = await self.context.execute_script(
                'index => getElementByIndex(index)', 
                index, 
                enable_handle=True
            )
            box:dict=node.get('box')
            center:dict=node.get('center')
            element_handle = handle.as_element()
            element_node = DOMElementNode(
                tag=node.get('tag'),
                role=node.get('role'),
                name=node.get('name'),
                attributes=node.get('attributes'),
                center=CenterCord(**{
                    'x':center.get('x'),
                    'y':center.get('y')
                }),
                bounding_box=BoundingBox(**{
                    'left': box.get('left'),
                    'top': box.get('top'),
                    'right': box.get('right'),
                    'bottom': box.get('bottom')
                })
            )
            return index, (element_node, element_handle)

        tasks = [process_node(index, node) for index, node in enumerate(nodes)]
        results = await asyncio.gather(*tasks)
        return dict(results)