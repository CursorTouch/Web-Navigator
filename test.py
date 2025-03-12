from src.agent.web.browser import Browser,BrowserConfig
from src.agent.web.context import Context
from src.agent.web.tools import goto_tool
from src.agent.web.dom import DOM
from time import sleep
import asyncio

async def main():
    browser=Browser(config=BrowserConfig(headless=False,browser='chrome'))
    context=Context(browser=browser)
    page=await context.get_current_page()
    dom=DOM(context=context)
    await goto_tool.async_invoke(url='https://google.com/',context=context)
    await dom.get_state(use_vision=True)
    sleep(5)
    await context.close_session()
    await browser.close_browser()
    print(page)

if __name__=='__main__':
    asyncio.run(main())