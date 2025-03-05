from dataclasses import dataclass,field
from playwright.async_api import ElementHandle

@dataclass
class BoundingBox:
    left:int
    top:int
    right:int
    bottom:int

    def to_string(self):
        return f'({self.left},{self.top},{self.right},{self.bottom})'
    
    def to_dict(self):
        return {'left':self.left,'top':self.top,'right':self.right,'bottom':self.bottom}

@dataclass
class CenterCord:
    x:int
    y:int

    def to_string(self)->str:
        return f'({self.x},{self.y})'
    
    def to_dict(self):
        return {'x':self.x,'y':self.y}

@dataclass
class DOMElementNode:
    tag: str
    role: str
    name: str
    bounding_box: BoundingBox
    center: CenterCord
    attributes: dict[str,str] = field(default_factory=dict)

    def __repr__(self):
        return f"DOMElementNode(tag='{self.tag}', role='{self.role}', name='{self.name}', attributes={self.attributes}, cordinates={self.center}, bounding_box={self.bounding_box})"
    
    def to_dict(self)->dict[str,str]:
        return {'tag':self.tag,'role':self.role,'name':self.name,'bounding_box':self.bounding_box.to_dict(),'attributes':self.attributes, 'cordinates':self.center.to_dict()}
    
@dataclass
class DOMState:
    nodes: list[tuple[DOMElementNode,ElementHandle]]=field(default_factory=list)
    selector_map:dict[int,tuple[DOMElementNode,ElementHandle]]=field(default_factory=dict)

    def elements_to_string(self)->str:
        return '\n'.join([f'{index} - Tag: {node.tag} Role: {node.role} Name: {node.name} Attributes: {node.attributes} Cordinates: {node.center.to_string()}' for index,(node,_) in enumerate(self.nodes)])