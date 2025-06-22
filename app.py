from src.agent.web.browser.config import BrowserConfig
from src.inference.gemini import ChatGemini
from src.inference.nvidia import ChatNvidia
from rich.markdown import Markdown
from src.agent.web import WebAgent
from rich.console import Console
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('NVIDIA_API_KEY')
browser_instance_dir = os.getenv('BROWSER_INSTANCE_DIR')
user_data_dir = os.getenv('USER_DATA_DIR')

console=Console()
llm=ChatNvidia(model="qwen/qwen3-235b-a22b", api_key=api_key, temperature=0)
# llm=ChatGroq(model='meta-llama/llama-4-maverick-17b-128e-instruct',api_key=api_key,temperature=0)
config=BrowserConfig(device=None,browser='chrome',browser_instance_dir=browser_instance_dir,user_data_dir=user_data_dir,headless=False)
agent = WebAgent(config=config,additional_tools=[],llm=llm,verbose=True,use_vision=False,max_iteration=100,include_human_in_loop=False,token_usage=False)

user_query = input('Enter your query: ')
agent_response = agent.invoke(user_query)
console.print(Markdown(agent_response.get('output')))