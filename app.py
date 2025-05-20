from src.agent.web.browser.config import BrowserConfig
from src.inference.gemini import ChatGemini
from src.inference.groq import AudioGroq
from src.agent.web import WebAgent
from dotenv import load_dotenv
from src.speech import Speech
import os

load_dotenv()
google_api_key=os.getenv('GOOGLE_API_KEY')
groq_api_key=os.getenv('GROQ_API_KEY')
browser_instance_dir=os.getenv('BROWSER_INSTANCE_DIR')
user_data_dir=os.getenv('USER_DATA_DIR')

# LLMs used
llm=ChatGemini(model='gemini-2.0-flash',api_key=google_api_key,temperature=0)
speech_llm=AudioGroq(model='whisper-large-v3',mode='translations',api_key=groq_api_key,temperature=0)

config=BrowserConfig(browser='chrome',browser_instance_dir=None,user_data_dir=None,headless=False)
agent=WebAgent(config=config,instructions=[],llm=llm,verbose=True,use_vision=True,max_iteration=100,token_usage=False)

mode=input('Enter the mode of input (text/voice): ')
if mode=='text':
    user_query=input('Enter your query: ')
elif mode=='voice':
    speech=Speech(llm=speech_llm)
    user_query=speech.invoke()
    print(f'Enter your query: {user_query.content}')
else:
    raise Exception('Invalid mode of input. Use "text" or "voice"')
agent_response=agent.invoke(user_query)
print(agent_response.get('output'))
