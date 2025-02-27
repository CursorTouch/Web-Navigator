from dataclasses import dataclass
from typing import List, Literal
from getpass import getuser
from pathlib import Path
import os

@dataclass
class BrowserConfig:
    headless:bool=False
    wss_url:str=None
    browser_instance_path:str=None
    downloads_path:str=Path(os.getcwd()).joinpath('./downloads').as_posix()
    browser:Literal['chrome','firefox','edge']='edge'
    user_data_dir:str=Path(os.getcwd()).joinpath(f'./user_data/{browser}/{getuser()}').as_posix()
    timeout:int=60*1000
    slow_mo:int=300

SECURITY_ARGS = [
	'--disable-web-security',
	'--disable-site-isolation-trials',
	'--disable-features=IsolateOrigins,site-per-process',
]

BROWSER_ARGS=[
    '--disable-sandbox'
	'--enable-blink-features=IdleDetection',
	'--disable-blink-features=AutomationControlled',
	'--disable-infobars',
	'--disable-background-timer-throttling',
	'--disable-popup-blocking',
	'--disable-backgrounding-occluded-windows',
	'--disable-renderer-backgrounding',
	'--disable-window-activation',
	'--disable-focus-on-load',
	'--no-first-run',
	'--no-default-browser-check',
	'--no-startup-window',
	'--window-position=0,0',
    '--remote-debugging-port=9222'
]

IGNORE_DEFAULT_ARGS=['--enable-automation']