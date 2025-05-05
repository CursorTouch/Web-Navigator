from playwright.async_api import Page,Browser as PlaywrightBrowser,Frame,ElementHandle,BrowserContext as PlaywrightContext
from src.agent.web.context.config import IGNORED_URL_PATTERNS,RELEVANT_FILE_EXTENSIONS,RELEVANT_CONTEXT_TYPES
from src.agent.web.browser.config import BROWSER_ARGS,SECURITY_ARGS,IGNORE_DEFAULT_ARGS
from src.agent.web.context.views import BrowserSession,BrowserState,Tab
from src.agent.web.context.config import ContextConfig
from src.agent.web.dom.views import DOMElementNode
from src.agent.web.browser import Browser
from src.agent.web.dom import DOM
from urllib.parse import urlparse
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
        if self.session is None:
            return None
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
        screenshot,dom_state=None,[]
        current_tab=Tab(0,page.url,await page.title(),page)
        tabs=[]
        state=BrowserState(current_tab=current_tab,tabs=tabs,screenshot=screenshot,dom_state=dom_state)
        return state
    
    async def update_state(self,use_vision:bool=False):
        dom=DOM(self)
        screenshot,dom_state=await dom.get_state(use_vision=use_vision)
        current_tab=await self.get_current_tab()
        tabs=await self.get_all_tabs()
        state=BrowserState(current_tab=current_tab,tabs=tabs,screenshot=screenshot,dom_state=dom_state)
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
        
    async def setup_context(self,browser:PlaywrightBrowser|None=None)->PlaywrightContext:
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
            args=['--disable-blink-features=AutomationControlled','--disable-blink-features=IdleDetection','--no-infobars']
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
    
    async def get_all_tabs(self)->list[Tab]:
        session=await self.get_session()
        pages=session.context.pages
        return [Tab(index,page.url,await page.title(),page) for index,page in enumerate(pages)]
    
    async def get_current_tab(self)->Tab:
        tabs=await self.get_all_tabs()
        current_page=await self.get_current_page()
        return next((tab for tab in tabs if tab.page==current_page),None)
    
    async def get_selector_map(self)->dict[int,DOMElementNode]:
        session=await self.get_session()
        return session.state.dom_state.selector_map
    
    async def get_element_by_index(self,index:int)->DOMElementNode:
        selector_map=await self.get_selector_map()
        if index not in selector_map.keys():
            raise Exception(f'Element under index {index} not found')
        element=selector_map.get(index)
        return element
    
    async def get_handle_by_xpath(self,xpath:dict[str,str])->ElementHandle:
        page=await self.get_current_page()
        frame_xpath,element_xpath=xpath.values()
        if frame_xpath: # handle elements from iframe
            frame=page.frame_locator(f'xpath={frame_xpath}')
            element=await frame.locator(f'xpath={element_xpath}').element_handle()
        else: #handle elements from main frame
            element=await page.locator(f'xpath={element_xpath}').element_handle()
        return element

    async def execute_script(self,obj:Frame|Page,script:str,args:list=None,enable_handle:bool=False):
        if enable_handle:
            handle=await obj.evaluate_handle(script,args)
            return handle.as_element()
        return await obj.evaluate(script,args)
    
    def is_ad_url(self,url:str)->bool:
        url_pattern=urlparse(url).netloc
        if not url_pattern:
            return True
        return any(pattern in url_pattern for pattern in IGNORED_URL_PATTERNS)
    
    async def is_frame_visible(self,frame:Frame)->bool:
        if frame.is_detached() or self.is_ad_url(frame.url):
            return False
        frame_element=await frame.frame_element()
        if frame_element is None: 
            return False
        style=await frame_element.get_attribute('style')
        if style is not None:
            css:dict=self.inline_style_parser(style)
            if any([css.get('display')=='none',css.get('visibility')=='hidden']):
                return False
        bbox=await frame_element.bounding_box()
        if bbox is None:
            return False
        area=bbox.get('width')*bbox.get('height')
        if any([bbox.get('x')<0,bbox.get('y')<0,area<10]):
            return False
        return True
    
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
    
    async def is_page_blank(self):
        page=await self.get_current_page()
        return page.url=='about:blank'
    
    def inline_style_parser(self,style:str)->dict[str,str]:
        styles = {}
        if not style:
            return styles
        for rule in style.split(";"):
            if ":" in rule:
                prop, val = rule.split(":", 1)
                styles[prop.strip()] = val.strip()
        return styles