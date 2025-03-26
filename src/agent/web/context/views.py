from dataclasses import dataclass,field
from playwright.async_api import Page,BrowserContext as PlaywrightBrowserContext
from src.agent.web.dom.views import DOMState
from typing import Optional

@dataclass 
class Tab:
	id:int
	url:str
	title:str

@dataclass
class BrowserState:
	url:str=''
	title:str=''
	tabs:list[Tab]=field(default_factory=list)
	screenshot:Optional[str]=None
	dom_state:DOMState=field(default_factory=DOMState([]))
	
	def tabs_to_string(self)->str:
		return '\n'.join([f'{tab.id} - Title: {tab.title} - URL: {tab.url}' for tab in self.tabs])

@dataclass
class BrowserSession:
	context: PlaywrightBrowserContext
	current_page: Page
	state: BrowserState