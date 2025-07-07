from typing import TypedDict,Annotated
from src.message import BaseMessage
from operator import add

class AgentState(TypedDict):
    input:str
    output:str
    agent_data:dict
    prev_observation:str
    messages: Annotated[list[BaseMessage],add]