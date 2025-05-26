from src.agent.web.browser.config import BrowserConfig
from src.inference.gemini import ChatGemini
from src.agent.web import WebAgent
from dotenv import load_dotenv
import os
import re

# Load environment variables from .env file
load_dotenv()
google_api_key = os.getenv('GOOGLE_API_KEY')
browser_instance_dir = os.getenv('BROWSER_INSTANCE_DIR')
user_data_dir = os.getenv('USER_DATA_DIR')

# Check if the Google API key is set
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the .env file.")

llm = ChatGemini(model='gemini-2.5-flash-preview-04-17', api_key=google_api_key, temperature=0)

config=BrowserConfig(browser='chrome',browser_instance_dir=None,user_data_dir=None,headless=False)

# Initialize the Web Agent
agent = WebAgent(
    config=config,
    instructions=[], # Add any specific instructions for the agent here
    llm=llm,
    verbose=True, # Set to True to see detailed agent logs
    use_vision=True, # Set to True if your LLM supports vision and you want to use screenshots
    max_iteration=100,
    token_usage=True # Set to True to see token usage logs
)

user_query = input('Enter your query: ')
print("\n🚀 Starting Web Agent...")
agent_response = agent.invoke(user_query)
print("\n✅ Agent Finished. Final Output:")
print(agent_response.get('output'))