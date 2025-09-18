from pydantic import BaseModel,Field
from typing import Literal

class SharedBaseModel(BaseModel):
    class Config:
        extra="allow"

class Done(SharedBaseModel):
    content:str = Field(...,description="Summary of the completed task in proper markdown format explaining what was accomplished",examples=["The task is completed successfully. User profile updated with new email address."])

class Click(SharedBaseModel):
    index:int = Field(...,description="The index/label of the interactive element to click (buttons, links, checkboxes, tabs, etc.)",examples=[0])

class Type(SharedBaseModel):
    index:int = Field(...,description="The index/label of the input element to type text into (text fields, search boxes, text areas)",examples=[0])
    text:str = Field(...,description="The text content to type into the input field",examples=["hello world","user@example.com","My search query"])
    clear:Literal['True','False']=Field(description="Whether to clear existing text before typing new content",default="False",examples=['True'])
    press_enter:Literal['True','False']=Field(description="Whether to press Enter after typing",default="False",examples=['True'])

class Wait(SharedBaseModel):
    time:int = Field(...,description="Number of seconds to wait for page loading, animations, or content to appear",examples=[1,3,5])

class Scroll(SharedBaseModel):
    direction: Literal['up','down'] = Field(description="The direction to scroll content", examples=['up','down'], default='up')
    index: int = Field(description="Index of specific scrollable element, if None then scrolls the entire page", examples=[0, 5, 12,None],default=None)
    amount: int = Field(description="Number of pixels to scroll, if None then scrolls by page/container height. Must required for scrollable container elements and the amount should be small", examples=[100, 25, 50],default=500)

class GoTo(SharedBaseModel):
    url:str = Field(...,description="The complete URL to navigate to including protocol (http/https)",examples=["https://www.example.com","https://google.com/search?q=test"])

class Back(SharedBaseModel):
    pass

class Forward(SharedBaseModel):
    pass

class Key(SharedBaseModel):
    keys:str = Field(...,description="Keyboard key or key combination to press (supports modifiers like Control, Alt, Shift)",examples=["Enter","Control+A","Escape","Tab","Control+C"])
    times:int = Field(description="Number of times to repeat the key press sequence",examples=[1,2,3],default=1)

class Download(SharedBaseModel):
    url:str = Field(...,description="Direct URL of the file to download (supports various file types: PDF, images, videos, documents)",examples=["https://www.example.com/document.pdf","https://site.com/image.jpg"])
    filename:str=Field(...,description="Local filename to save the downloaded file as (include file extension)",examples=["document.pdf","image.jpg","data.xlsx"])

class Scrape(SharedBaseModel):
    pass

class Tab(SharedBaseModel):
    mode:Literal['open','close','switch'] = Field(...,description="Tab operation: 'open' creates new tab, 'close' closes current tab, 'switch' changes to existing tab",examples=['open','close','switch'])
    tab_index:int = Field(description="Zero-based index of the tab to switch to (only required for 'switch' mode)",examples=[0,1,2],default=None)

class Upload(SharedBaseModel):
    index:int = Field(...,description="Index of the file input element to upload files to",examples=[0])
    filenames:list[str] = Field(...,description="List of filenames to upload from the ./uploads directory (supports single or multiple files)",examples=[["document.pdf"],["image1.jpg","image2.png"]])

class Menu(SharedBaseModel):
    index:int = Field(...,description="Index of the dropdown/select element to interact with",examples=[0])
    labels:list[str] = Field(...,description="List of visible option labels to select from the dropdown menu (supports single or multiple selection)",examples=[["BMW"],["Option 1","Option 2"]])

class Script(SharedBaseModel):
    script:str = Field(...,description="The JavaScript code to execute in the current webpage to scrape data. Make sure the script is well-formatted",examples=["console.log('Hello, world!')"])

class HumanInput(SharedBaseModel):
    prompt: str = Field(..., description="Clear question or instruction to ask the human user when assistance is needed", examples=["Please enter the OTP code sent to your phone", "What is your preferred payment method?", "Please solve this CAPTCHA"])