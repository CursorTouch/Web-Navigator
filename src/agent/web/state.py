from src.agent.web.context import BrowserState
from src.agent.web.dom.views import DOMState
from typing import TypedDict,Annotated
from src.message import BaseMessage
from operator import add

class AgentState(TypedDict):
    input:str
    output:str
    agent_data:dict
    prev_observation:str
    browser_state:BrowserState|None
    dom_state:DOMState|None
    messages: Annotated[list[BaseMessage],add]