from dataclasses import dataclass,field
from playwright.async_api import Page,BrowserContext as PlaywrightBrowserContext
from src.agent.web.dom.views import DOMState
from typing import Optional

@dataclass 
class Tab:
	id:int
	url:str
	title:str
	page:Page
	
	def to_string(self)->str:
		return f'{self.id} - Title: {self.title} - URL: {self.url}'

@dataclass
class BrowserState:
	current_tab:Optional[Tab]=None
	tabs:list[Tab]=field(default_factory=list)
	screenshot:Optional[str]=None
	dom_state:DOMState=field(default_factory=DOMState([]))
	
	def tabs_to_string(self)->str:
		return '\n'.join([tab.to_string() for tab in self.tabs])

@dataclass
class BrowserSession:
	context: PlaywrightBrowserContext
	current_page: Page
	state: BrowserState