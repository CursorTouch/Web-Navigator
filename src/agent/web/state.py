from typing import TypedDict,Annotated
from src.message import BaseMessage
from pydantic import BaseModel
from operator import add

class AgentState(TypedDict):
    input:str
    output:str|BaseModel
    agent_data:dict
    prev_observation:str
    messages: Annotated[list[BaseMessage],add]