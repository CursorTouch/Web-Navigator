from pydantic import BaseModel,Field,ConfigDict
from typing import Callable,Type

class Function(BaseModel):
    name:str=Field(...,description="the name of the action")
    description:str=Field(...,description="the description of the action")
    params:Type[BaseModel]|None
    function:Callable|None
    model_config=ConfigDict(arbitrary_types_allowed=True)

class ToolResult(BaseModel):
    name: str = Field(...,description="the action taken")
    content: str = Field(...,description="the output of the action")