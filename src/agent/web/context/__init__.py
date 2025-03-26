from playwright.async_api import Page,Browser as PlaywrightBrowser, Frame,ElementHandle,BrowserContext as PlaywrightBrowserContext
from src.agent.web.browser.config import BROWSER_ARGS,SECURITY_ARGS,IGNORE_DEFAULT_ARGS
from src.agent.web.context.views import BrowserSession,BrowserState,Tab
from src.agent.web.context.config import ContextConfig
from src.agent.web.dom.views import DOMElementNode
from src.agent.web.browser import Browser
from src.agent.web.dom import DOM
from datetime import datetime
from pathlib import Path
from uuid import uuid4
from os import getcwd

class Context:
    def __init__(self,browser:Browser,config:ContextConfig=ContextConfig()):
        self.browser=browser
        self.config=config
        self.context_id=str(uuid4())
        self.session:BrowserSession=None

    async def __aenter__(self):
        await self.init_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close_session()

    async def close_session(self):
        try:
            await self.session.context.close()
        except Exception as e:
            print('Context failed to close',e)
        finally:
            self.browser_context=None

    async def init_session(self):
        browser=await self.browser.get_playwright_browser()
        context=await self.setup_context(browser)
        if browser is not None: # The case whether is no user_data provided
            page=await context.new_page()
        else: # The case where the user_data is provided
            pages=context.pages
            if len(pages):
                page=pages[0]
            else:
                page=await context.new_page()
        state=await self.initial_state(page)
        self.session=BrowserSession(context,page,state)
        
    async def initial_state(self,page:Page):
        dom_state=[]
        tabs=[]
        screenshot=None
        state=BrowserState(url=page.url,title=await page.title(),tabs=tabs,screenshot=screenshot,dom_state=dom_state)
        return state
    
    async def update_state(self,use_vision:bool=False):
        page=await self.get_current_page()
        dom=DOM(self)
        screenshot,dom_state=await dom.get_state(use_vision=use_vision)
        # print(dom_state.elements_to_string())
        tabs=await self.get_tabs()
        state=BrowserState(url=page.url,title=await page.title(),tabs=tabs,screenshot=screenshot,dom_state=dom_state)
        return state
    
    async def get_state(self,use_vision=False)->BrowserState:
        session=await self.get_session()
        state=await self.update_state(use_vision=use_vision)
        session.state=state
        return session.state
    
    async def get_session(self)->BrowserSession:
        if self.session is None:
            await self.init_session()
        return self.session
    
    async def get_current_page(self)->Page:
        session=await self.get_session()
        if session.current_page is None:
            raise ValueError("No current page found")
        return session.current_page
        
    async def setup_context(self,browser:PlaywrightBrowser|None=None)->PlaywrightBrowserContext:
        parameters={
            'ignore_https_errors':self.config.disable_security,
            'user_agent':self.config.user_agent,
            'bypass_csp':self.config.disable_security,
            'java_script_enabled':True,
            'accept_downloads':True,
            'no_viewport':True
        }
        if browser is not None:
            context=await browser.new_context(**parameters)
            with open('./src/agent/web/context/script.js') as f:
                script=f.read()
            await context.add_init_script(script)
        else:
            args=['--no-sandbox','--disable-blink-features=AutomationControlled','--disable-blink-features=IdleDetection','--no-infobars']
            parameters=parameters|{
                'headless':self.browser.config.headless,
                'slow_mo':self.browser.config.slow_mo,
                'ignore_default_args': IGNORE_DEFAULT_ARGS,
                'args': args+SECURITY_ARGS,
                'user_data_dir': self.browser.config.user_data_dir,
                'downloads_path': self.browser.config.downloads_dir,
                'executable_path': self.browser.config.browser_instance_dir,
            }
            # browser is None if the user_data_dir is not None in the Browser class
            browser=self.browser.config.browser
            if browser=='chrome':
                context=await self.browser.playwright.chromium.launch_persistent_context(channel='chrome',**parameters)
            elif browser=='firefox':
                context=await self.browser.playwright.firefox.launch_persistent_context(**parameters)
            elif browser=='edge':
                context=await self.browser.playwright.chromium.launch_persistent_context(channel='msedge',**parameters)
            else:
                raise Exception('Invalid Browser Type')
        return context
    
    async def get_tabs(self)->list[Tab]:
        session=await self.get_session()
        pages=session.context.pages
        return [Tab(index,page.url,await page.title()) for index,page in enumerate(pages)]

    
    async def execute_script(self,obj:Frame|Page,script:str,args:list=None,enable_handle:bool=False):
        if enable_handle:
            return await obj.evaluate_handle(script,args)
        return await obj.evaluate(script,args)
    
    async def get_element_from_point(self,x:int,y:int)->ElementHandle:
        page=await self.get_current_page()
        return await self.execute_script(page,f"document.elementFromPoint({x},{y})",enable_handle=True)
    
    async def get_screenshot(self,save_screenshot:bool=False,full_page:bool=False):
        page=await self.get_current_page()
        if save_screenshot:
            date_time=datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
            folder_path=Path(getcwd()).joinpath('./screenshots')
            folder_path.mkdir(parents=True,exist_ok=True)
            path=folder_path.joinpath(f'screenshot_{date_time}.jpeg')
        else:
            path=None
        await page.wait_for_timeout(2*1000)
        screenshot=await page.screenshot(path=path,full_page=full_page,animations='disabled',type='jpeg')
        return screenshot