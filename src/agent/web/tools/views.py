from pydantic import BaseModel,Field
from typing import Literal

class SharedBaseModel(BaseModel):
    class Config:
        extra="allow"

class Clipboard(SharedBaseModel):
    mode:Literal['copy','paste'] = Field(...,description="the mode of the clipboard",examples=['copy'])
    text:str = Field(...,description="the text to copy to clipboard",examples=["hello world"])

class Click(SharedBaseModel):
    x:int = Field(...,description="the x coordinate of the element to click",examples=[0])
    y:int = Field(...,description="the y coordinate of the element to click",examples=[0])
    mode:Literal['navigate','click'] = Field(description="navigates to url if needed, otherwise just clicks.",examples=['navigate'],default='navigate')

class Type(SharedBaseModel):
    x:int = Field(...,description="the x coordinate of the element to type in",examples=[0])
    y:int = Field(...,description="the y coordinate of the element to type in",examples=[0])
    text:str = Field(...,description="the text to type",examples=["hello world"])
    clear:Literal['True','False']=Field(description="whether to clear the text before typing",default="False",examples=['True'])

class Wait(SharedBaseModel):
    time:int = Field(...,description="the time to wait for the element to be visible in seconds",examples=[1])

class Scroll(SharedBaseModel):
    direction:Literal['up','down'] = Field(...,description="the direction to scroll",examples=['up'])
    amount:int = Field(description="the amount to scroll, if None then page up or down",examples=[100],default=None)

class GoTo(SharedBaseModel):
    url:str = Field(...,description="the url to navigate to",examples=["https://www.example.com"])

class Back(SharedBaseModel):
    pass

class Key(SharedBaseModel):
    keys:str = Field(...,description="the key or combination of keys to press",examples=["Enter","Control+A","Backspace"])
    times:int = Field(description="the number of times to press the key or combination of keys",examples=[2],default=1)

class Download(SharedBaseModel):
    index:int = Field(...,description="the index of the element to download file",examples=[0])
    url:str = Field(...,description="url of the file to download",examples=["https://www.example.com/file.txt","https://abc.org/pdf/54655"])
    filename:str=Field(...,description="the name of the file to download",examples=["file.txt","xy4rs.pdf"])

class Scrape(SharedBaseModel):
    format:Literal['markdown','text'] = Field(description="the format of content to be like",examples=['text'],default='markdown')

class Tab(SharedBaseModel):
    mode:Literal['open','close','switch'] = Field(...,description="the mode of the tab",examples=['open'])
    tab_index:int = Field(description="mention the index of the exisiting tab to switch, if mode is switch",examples=[0],default=None)

class Upload(SharedBaseModel):
    index:int = Field(...,description="the index of the element to upload file",examples=[0])
    filenames:list[str] = Field(...,description="list of filenames of the files to upload",examples=[["file.txt"]])

class Menu(SharedBaseModel):
    index:int = Field(...,description="the index of the element having the dropdown menu",examples=[0])
    labels:list[str] = Field(...,description="list of labels to select from the dropdown menu",examples=["BMW"])

class Form(SharedBaseModel):
    tool_names:list[Literal['Click Tool','Type Tool','Upload Tool','Menu Tool']]=Field(...,description="list of tool names",examples=[['Type Tool','Type Tool','Type Tool','Menu Tool'],['Click Tool','Type Tool','Click Tool','Upload Tool']])
    tool_inputs:list[dict]=Field(...,description="list of tool inputs",examples=[[{'index':2,'text':'John'},{'index':3,'text':'Doe'},{'index':5,'text':'hello world'},{'index':6,'labels':['BMW']}],[{'index':0},{'index':0,'text':'hello world'},{'index':0},{'index':0,'filenames':['file.txt']}]])