from src.agent.web.browser import Browser,BrowserConfig
from src.agent.web.context import Context
from src.agent.web.tools import goto_tool
from src.agent.web.dom import DOM
from dotenv import load_dotenv
from time import sleep
import asyncio
import os

load_dotenv()
browser_instance_dir=os.environ.get('BROWSER_INSTANCE_DIR')
user_data_dir=os.environ.get('USER_DATA_DIR')
downloads_dir=os.environ.get('DOWNLOADS_DIR')

async def main():
    browser=Browser(config=BrowserConfig(headless=False,browser='chrome',browser_instance_dir=browser_instance_dir,user_data_dir=user_data_dir,downloads_dir=None))
    context=Context(browser=browser)
    await context.init_session()
    page=await context.get_current_page()
    dom=DOM(context=context)
    await goto_tool.async_invoke(url='https://google.com',context=context)
    sleep(5)
    screenshot,dom_state=await dom.get_state(use_vision=True)
    print(dom_state.elements_to_string())
    await context.close_session()
    await browser.close_browser()

if __name__=='__main__':
    asyncio.run(main())