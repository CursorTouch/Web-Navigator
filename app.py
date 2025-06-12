from src.agent.web.browser.config import BrowserConfig
from src.inference.gemini import ChatGemini
from src.agent.web import WebAgent
from dotenv import load_dotenv
import os

load_dotenv()

google_api_key = os.getenv('GOOGLE_API_KEY')
browser_instance_dir = os.getenv('BROWSER_INSTANCE_DIR')
user_data_dir = os.getenv('USER_DATA_DIR')

llm=ChatGemini(model='gemini-2.0-flash', api_key=google_api_key, temperature=0)
config=BrowserConfig(device='iPhone 13',browser='edge',browser_instance_dir=browser_instance_dir,user_data_dir=user_data_dir,headless=False)
agent = WebAgent(config=config,llm=llm,verbose=True,use_vision=True,max_iteration=100,include_human_in_loop=True,token_usage=False)

user_query = input('Enter your query: ')
agent_response = agent.invoke(user_query)
print(agent_response.get('output'))