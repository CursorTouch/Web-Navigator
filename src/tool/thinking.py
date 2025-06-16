from src.tool import Tool
from pydantic import BaseModel,Field

class Thinking(BaseModel):
    thought: str=Field(...,description="Your extended thinking goes here")

@Tool('Thinking Tool',params=Thinking)
async def thinking_tool(thought:str,context=None):
    '''
    To think about something. It will not obtain new information or make any changes, but just log the thought.
    Use it when complex reasoning or brainstorming is needed.
    '''
    return thought