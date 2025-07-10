from src.agent.web.dom.views import BoundingBox,CenterCord
from pydantic import BaseModel,Field
from dataclasses import dataclass

class DOMHistoryElementNode(BaseModel):
    tag:str
    role:str
    name:str
    center:CenterCord
    bounding_box:BoundingBox
    xpath:dict[str,str]=Field(default_factory=dict)
    attributes:dict[str,str]=Field(default_factory=dict)
    viewport:tuple[int,int]=Field(default_factory=tuple)

    def to_dict(self)->dict[str,str]:
        return {'tag':self.tag,'role':self.role,'xpath':self.xpath,'attributes':self.attributes,'bounding_box':self.bounding_box.to_dict()}
    
@dataclass
class HashElement:
    attributes:str
    xpath:str