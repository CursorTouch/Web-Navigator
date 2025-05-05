from pydantic import BaseModel,Field
from typing import Literal

class SharedBaseModel(BaseModel):
    class Config:
        extra="allow"

class Done(SharedBaseModel):
    content:str = Field(...,description="deliver the content for the user's query in proper markdown format",examples=["The task is completed successfully."])

class Click(SharedBaseModel):
    index:int = Field(...,description="the index of the element to click",examples=[0])

class Type(SharedBaseModel):
    index:int = Field(...,description="the index of the element to type in the text",examples=[0])
    text:str = Field(...,description="the text to type",examples=["hello world"])
    clear:Literal['True','False']=Field(description="whether to clear the text before typing",default="False",examples=['True'])

class Wait(SharedBaseModel):
    time:int = Field(...,description="the time to wait for the element to be visible in seconds",examples=[1])

class Scroll(SharedBaseModel):
    direction:Literal['up','down'] = Field(description="the direction to scroll",examples=['up'],default='up')
    amount:int = Field(description="the amount to scroll, if None then page up or down",examples=[100,250],default=None)

class GoTo(SharedBaseModel):
    url:str = Field(...,description="the url to navigate to",examples=["https://www.example.com"])

class Transcript(SharedBaseModel):
    url:str = Field(...,description="the url of the YouTube video to get the transcript",examples=["https://www.youtube.com/watch?v=dQw4w9WgXcQ"])


class Back(SharedBaseModel):
    pass

class Forward(SharedBaseModel):
    pass

class Key(SharedBaseModel):
    keys:str = Field(...,description="the key or combination of keys to press",examples=["Enter","Control+A","Backspace"])
    times:int = Field(description="the number of times to press the key or combination of keys",examples=[2],default=1)

class Download(SharedBaseModel):
    url:str = Field(...,description="url of the file to download",examples=["https://www.example.com/file.txt","https://abc.org/pdf/54655"])
    filename:str=Field(...,description="the name of the file to download",examples=["file.txt","xy4rs.pdf"])

class Scrape(SharedBaseModel):
    format:Literal['markdown','text'] = Field(description="the format of content to be like",examples=['text'],default='markdown')

class Tab(SharedBaseModel):
    mode:Literal['open','close','switch'] = Field(...,description="the mode of the tab",examples=['open'])
    tab_index:int = Field(description="the index of the tab to switch to, if the mode is 'switch'",examples=[0],default=None)

class Upload(SharedBaseModel):
    index:int = Field(...,description="the index of the element to upload file to",examples=[0])
    filenames:list[str] = Field(...,description="list of filenames of the files to upload",examples=[["file.txt"]])

class Menu(SharedBaseModel):
    index:int = Field(...,description="the index of the element to select from the dropdown menu",examples=[0])
    labels:list[str] = Field(...,description="list of labels to select from the dropdown menu",examples=["BMW"])