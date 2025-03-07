from src.message import AIMessage,BaseMessage,SystemMessage,ImageMessage,HumanMessage,ToolMessage
from tenacity import retry,stop_after_attempt,retry_if_exception_type
from requests import RequestException,HTTPError,ConnectionError
from ratelimit import limits,sleep_and_retry
from httpx import Client,AsyncClient
from src.inference import BaseInference,Token
from pydantic import BaseModel
from typing import Generator
from typing import Literal
from pathlib import Path
from json import loads
from uuid import uuid4
import mimetypes
import requests

class ChatAnthropic(BaseInference):
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self, messages: list[BaseMessage],json:bool=False,model:BaseModel=None)->AIMessage|ToolMessage|BaseModel:
        self.headers.update({
            'x-api-key': self.api_key,
            "anthropic-version": "2023-06-01",
            })
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://api.anthropic.com/v1/messages"
        contents=[]
        system_instruct=None
        for message in messages:
            if isinstance(message,(HumanMessage,AIMessage)):
                contents.append(message.to_dict())
            elif isinstance(message,ImageMessage):
                text,image=message.content
                contents.append([
                    {
                        'role':'user',
                        'content':[
                            {
                                'type':'text',
                                'text':text
                            },
                            {
                                'type':'image',
                                'source':{
                                    'type':'base64',
                                    'media_type':'image/png',
                                    'data':image
                                }
                            }
                        ]
                    }
                ])
            elif isinstance(message,SystemMessage):
                system_instruct=self.structured(message,model) if model else message.content
            else:
                raise Exception("Invalid Message")

        payload={
            "model": self.model,
            "messages": contents,
            "temperature": temperature,
            "response_format": {
                "type": "json_object" if json or model else "text"
            },
            "stream":False,
        }
        if self.tools:
            payload["tools"]=[{
                'type':'function',
                'function':{
                    'name':tool.name,
                    'description':tool.description,
                    'input_schema':tool.schema
                }
            } for tool in self.tools]
        if system_instruct:
            payload['system']=system_instruct
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,timeout=None)
            json_object=response.json()
            # print(json_object)
            if json_object.get('error'):
                raise HTTPError(json_object['error']['message'])
            message = json_object['content'][0]
            usage_metadata=json_object['usage']
            input,output,total=usage_metadata['input_tokens'],usage_metadata['output_tokens']
            total=input+output
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(message.get('text'))
            if json:
                return AIMessage(loads(message.get('text')))
            if message.get('content'):
                return AIMessage(message.get('text'))
            else:
                tool_call=message
                return ToolMessage(id= tool_call['id'] or str(uuid4()),name=tool_call['name'],args=tool_call['input']) 
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    async def async_invoke(self, messages: list[BaseMessage], json: bool = False, model: BaseModel = None) -> AIMessage | ToolMessage | BaseModel:
        self.headers.update({
            'x-api-key': self.api_key,
            "anthropic-version": "2023-06-01",
        })
        headers = self.headers
        temperature = self.temperature
        url = self.base_url or "https://api.anthropic.com/v1/messages"
        contents = []
        system_instruct = None

        for message in messages:
            if isinstance(message, (HumanMessage, AIMessage)):
                contents.append(message.to_dict())
            elif isinstance(message, ImageMessage):
                text, image = message.content
                contents.append([
                    {
                        'role': 'user',
                        'content': [
                            {
                                'type': 'text',
                                'text': text
                            },
                            {
                                'type': 'image',
                                'source': {
                                    'type': 'base64',
                                    'media_type': 'image/png',
                                    'data': image
                                }
                            }
                        ]
                    }
                ])
            elif isinstance(message, SystemMessage):
                system_instruct = self.structured(message, model) if model else message.content
            else:
                raise Exception("Invalid Message")

        payload = {
            "model": self.model,
            "messages": contents,
            "temperature": temperature,
            "response_format": {
                "type": "json_object" if json or model else "text"
            },
            "stream": False,
        }
        if self.tools:
            payload["tools"] = [{
                'type': 'function',
                'function': {
                    'name': tool.name,
                    'description': tool.description,
                    'input_schema': tool.schema
                }
            } for tool in self.tools]
        if system_instruct:
            payload['system'] = system_instruct

        try:
            async with AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                json_object = response.json()
                if json_object.get('error'):
                    raise HTTPError(json_object['error']['message'])
                message = json_object['content'][0]
                usage_metadata = json_object['usage']
                input, output= usage_metadata['input_tokens'], usage_metadata['output_tokens']
                total=input+output
                self.tokens = Token(input=input, output=output, total=total)
                if model:
                    return model.model_validate_json(message.get('text'))
                if json:
                    return AIMessage(loads(message.get('text')))
                if message.get('content'):
                    return AIMessage(message.get('text'))
                else:
                    tool_call = message
                    return ToolMessage(id=tool_call['id'] or str(uuid4()), name=tool_call['name'], args=tool_call['input'])
        except HTTPError as err:
            err_object = loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except Exception as err:
            print(err)
    
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def stream(self, messages: list[BaseMessage],json=False)->Generator[str,None,None]:
        pass
    
    def available_models(self):
        url='https://api.groq.com/openai/v1/models'
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        response=requests.get(url=url,headers=headers)
        response.raise_for_status()
        models=response.json()
        return [model['id'] for model in models['data'] if model['active']]