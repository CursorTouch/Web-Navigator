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

class ChatOpenAI(BaseInference):
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self, messages: list[BaseMessage],json:bool=False,model:BaseModel=None)->AIMessage|ToolMessage|BaseModel:
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "https://api.openai.com/v1/chat/completions"
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
        url=self.base_url or "https://api.openai.com/v1/chat/completions"
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
        url=self.base_url or "https://api.openai.com/v1/chat/completions"
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
    
    def available_models(self):
        url='https://api.openai.com/v1/models'
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        response=requests.get(url=url,headers=headers)
        response.raise_for_status()
        models=response.json()
        return [model['id'] for model in models['data'] if model['active']]

class AudioOpenAI(BaseInference):
    def __init__(self,mode:Literal['transcriptions','translations']='transcriptions', model: str = '', api_key: str = '', base_url: str = '', temperature: float = 0.5):
        self.mode=mode
        super().__init__(model, api_key, base_url, temperature)

    def invoke(self,file_path:str='', language:str='en', json:bool=False)->AIMessage:
        path=Path(file_path)
        headers={'Authorization': f'Bearer {self.api_key}'}
        url=self.base_url or f"https://api.openai.com/v1/audio/{self.mode}"
        data={
            "model": self.model,
            "temperature": self.temperature,
            "response_format": "json_object" if json else "text"
        }
        if self.mode=='transcriptions':
            data['language']=language
        # Get the MIME type for the file
        mime_type, _ = mimetypes.guess_type(path.name)
        files={
            'file': (path.name,self.__read_audio(path),mime_type)
        }
        try:
            with Client() as client:
                response=client.post(url=url,data=data,files=files,headers=headers,timeout=None)
            response.raise_for_status()
            if json:
                content=loads(response.text)['text']
            else:
                content=response.text
            return AIMessage(content)
        except HTTPError as err:
            err_object=loads(err.response.text)
            print(f'\nError: {err_object["error"]["message"]}\nStatus Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    def __read_audio(self,file_path:str):
        with open(file_path,'rb') as f:
            audio_data=f.read()
        return audio_data
    
    def async_invoke(self, messages:BaseMessage=[]):
        pass
    
    def stream(self, messages:BaseMessage=[]):
        pass
    
    def available_models(self):
        url='https://api.groq.com/openai/v1/models'
        self.headers.update({'Authorization': f'Bearer {self.api_key}'})
        headers=self.headers
        response=requests.get(url=url,headers=headers)
        response.raise_for_status()
        models=response.json()
        return [model['id'] for model in models['data'] if model['active']]
