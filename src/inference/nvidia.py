from src.message import AIMessage,BaseMessage,SystemMessage,ImageMessage,HumanMessage,ToolMessage
from tenacity import retry,stop_after_attempt,retry_if_exception_type
from requests import RequestException,HTTPError,ConnectionError
from ratelimit import limits,sleep_and_retry
from httpx import Client,AsyncClient
from src.inference import BaseInference,Token
from pydantic import BaseModel
from typing import Generator
from json import loads
from uuid import uuid4
import requests

class ChatNvidia(BaseInference):
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self, messages: list[BaseMessage],json:bool=False,model:BaseModel=None)->AIMessage|ToolMessage|BaseModel:
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://integrate.api.nvidia.com/v1/chat/completions"
        contents=[]
        for message in messages:
            if isinstance(message,SystemMessage):
                if model:
                    message.content=self.structured(message,model) 
                contents.append(message.to_dict())
            if isinstance(message,(HumanMessage,AIMessage)):
                contents.append(message.to_dict())
            if isinstance(message,ImageMessage):
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
                                'type':'image_url',
                                'image_url':{
                                    'url':image
                                }
                            }
                        ]
                    }
                ])

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
                    'parameters':tool.schema
                }
            } for tool in self.tools]
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,timeout=None)
            json_object=response.json()
            # print(json_object)
            if json_object.get('error'):
                raise HTTPError(json_object['error']['message'])
            message=json_object['choices'][0]['message']
            usage_metadata=json_object['usage']
            input,output,total=usage_metadata['prompt_tokens'],usage_metadata['completion_tokens'],usage_metadata['total_tokens']
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(message.get('content'))
            if json:
                return AIMessage(loads(message.get('content')))
            if message.get('content'):
                return AIMessage(message.get('content'))
            else:
                tool_call=message.get('tool_calls')[0]['function']
                return ToolMessage(id=str(uuid4()),name=tool_call['name'],args=tool_call['arguments']) 
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    async def async_invoke(self, messages: list[BaseMessage],json=False,model:BaseModel=None) -> AIMessage|ToolMessage|BaseModel:
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://integrate.api.nvidia.com/v1/chat/completions"
        contents=[]
        for message in messages:
            if isinstance(message,SystemMessage):
                if model:
                    message.content=self.structured(message,model) 
                contents.append(message.to_dict())
            if isinstance(message,(HumanMessage,AIMessage)):
                contents.append(message.to_dict())
            if isinstance(message,ImageMessage):
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
                                'type':'image_url',
                                'image_url':{
                                    'url':image
                                }
                            }
                        ]
                    }
                ])

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
                    'parameters':tool.schema
                }
            } for tool in self.tools]
        try:
            async with AsyncClient() as client:
                response=await client.post(url=url,json=payload,headers=headers,timeout=None)
            json_object=response.json()
            # print(json_object)
            if json_object.get('error'):
                raise HTTPError(json_object['error']['message'])
            message=json_object['choices'][0]['message']
            usage_metadata=json_object['usage']
            input,output,total=usage_metadata['prompt_tokens'],usage_metadata['completion_tokens'],usage_metadata['total_tokens']
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(message.get('content'))
            if json:
                return AIMessage(loads(message.get('content')))
            if message.get('content'):
                return AIMessage(message.get('content'))
            else:
                tool_call=message.get('tool_calls')[0]['function']
                return ToolMessage(id=str(uuid4()),name=tool_call['name'],args=tool_call['arguments']) 
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def stream(self, messages: list[BaseMessage],json=False)->Generator[str,None,None]:
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://integrate.api.nvidia.com/v1/chat/completions"
        messages=[message.to_dict() for message in messages]
        payload={
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "response_format": {
                "type": "json_object" if json else "text"
            },
            "stream":True,
        }
        try:
            response=requests.post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            for chunk in chunks:
                chunk=chunk.replace('data: ','')
                if chunk and chunk!='[DONE]':
                    delta=loads(chunk)['choices'][0]['delta']
                    yield delta.get('content','')
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()