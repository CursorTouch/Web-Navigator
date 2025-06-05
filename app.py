from src.agent.web.browser.config import BrowserConfig
from src.inference.gemini import ChatGemini
from src.agent.web import WebAgent
from pydantic import BaseModel,Field
from typing import Literal
from dotenv import load_dotenv
import os

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')
browser_instance_dir = os.getenv('BROWSER_INSTANCE_DIR')
user_data_dir = os.getenv('USER_DATA_DIR')

llm=ChatGemini(model='gemini-2.0-flash', api_key=google_api_key, temperature=0)
config=BrowserConfig(browser='edge',browser_instance_dir=browser_instance_dir,user_data_dir=user_data_dir,headless=False)
agent = WebAgent(config=config,llm=llm,verbose=True,use_vision=True,max_iteration=100,include_human_in_loop=False,token_usage=False)

class QuestionPaper(BaseModel):
    paper_link: str=Field(description="The link to the question paper")
    mode: Literal['FN','AN']=Field(description="The mode of the question paper")
    month: str=Field(description="The month of the question paper")
    year: int=Field(description="The year of the question paper")   

class QuestionPapers(BaseModel):
    subject_name: str=Field(description="The subject name of the question paper")
    question_papers: list[QuestionPaper]=Field(description="The question papers of the subject")

user_query = input('Enter your query: ')
agent_response = agent.invoke(user_query,structured_output=QuestionPapers)
print(agent_response.get('output'))