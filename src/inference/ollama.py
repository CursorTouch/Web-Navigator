from tenacity import retry,stop_after_attempt,retry_if_exception_type
from src.message import AIMessage,BaseMessage,ToolMessage
from requests import get,RequestException,ConnectionError
from httpx import Client,AsyncClient,HTTPError
from ratelimit import limits,sleep_and_retry
from src.inference import BaseInference,Token
from pydantic import BaseModel
from typing import Generator
from json import loads
from uuid import uuid4

class ChatOllama(BaseInference):
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self,messages: list[BaseMessage],json=False,model:BaseModel=None)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "stream":False
        }
        if json:
            payload['format']='json'
        if model:
            payload['format']=model.model_json_schema()
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
            response.raise_for_status()
            json_object=response.json()
            message=json_object['message']
            input,output,total=json_object['prompt_eval_count'],json_object['eval_count'],json_object['prompt_eval_count']+json_object['eval_count']
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
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    async def async_invoke(self,messages: list[BaseMessage],json=False,model:BaseModel=None)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "stream":False
        }
        if json:
            payload['format']='json'
        if model:
            payload['format']=model.model_json_schema()
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
            response.raise_for_status()
            json_object=response.json()
            message=json_object['message']
            input,output,total=json_object['prompt_eval_count'],json_object['eval_count'],json_object['prompt_eval_count']+json_object['eval_count']
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
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
    
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def stream(self,messages: list[BaseMessage],json=False)->Generator[str,None,None]:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/chat"
        payload={
            "model": self.model,
            "messages": [message.to_dict() for message in messages],
            "options":{
                "temperature": temperature,
            },
            "stream":True
        }
        if json:
            payload['format']='json'
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,stream=True,timeout=None)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            return (loads(chunk)['message']['content'] for chunk in chunks)
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    def available_models(self):
        url='http://localhost:11434/api/tags'
        headers=self.headers
        response=get(url=url,headers=headers)
        response.raise_for_status()
        models=response.json()
        return [model['name'] for model in models['models']]
        
class Ollama(BaseInference):
    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def invoke(self, query:str,json=False,model:BaseModel=None)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":False
        }
        if json:
            payload['format']='json'
        if model:
            payload['format']=model.model_json_schema()
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            json_object=response.json()
            input,output,total=json_object['prompt_eval_count'],json_object['eval_count'],json_object['prompt_eval_count']+json_object['eval_count']
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(json_object.get('response'))
            if json:
                return AIMessage(loads(json_object.get('response')))
            return AIMessage(json_object.get('response'))
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    async def async_invoke(self, query:str,json=False,model:BaseModel=None)->AIMessage:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":False
        }
        if json:
            payload['format']='json'
        if model:
            payload['format']=model.model_json_schema()
        try:
            async with AsyncClient() as client:
                response=await client.post(url=url,json=payload,headers=headers)
            response.raise_for_status()
            json_object=response.json()
            input,output,total=json_object['prompt_eval_count'],json_object['eval_count'],json_object['prompt_eval_count']+json_object['eval_count']
            self.tokens=Token(input=input,output=output,total=total)
            if model:
                return model.model_validate_json(json_object.get('response'))
            if json:
                return AIMessage(loads(json_object.get('response')))
            return AIMessage(json_object.get('response'))
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')

    @sleep_and_retry
    @limits(calls=15,period=60)
    @retry(stop=stop_after_attempt(3),retry=retry_if_exception_type(RequestException))
    def stream(self,query:str,json=False)->Generator[str,None,None]:
        headers=self.headers
        temperature=self.temperature
        url=self.base_url or "http://localhost:11434/api/generate"
        payload={
            "model": self.model,
            "prompt": query,
            "options":{
                "temperature": temperature,
            },
            "format":'json' if json else '',
            "stream":True
        }
        try:
            with Client() as client:
                response=client.post(url=url,json=payload,headers=headers,stream=True)
            response.raise_for_status()
            chunks=response.iter_lines(decode_unicode=True)
            return (loads(chunk)['response'] for chunk in chunks)
        except HTTPError as err:
            print(f'Error: {err.response.text}, Status Code: {err.response.status_code}')
        except ConnectionError as err:
            print(err)
        exit()
    
    def available_models(self):
        url='http://localhost:11434/api/tags'
        headers=self.headers
        response=get(url=url,headers=headers)
        response.raise_for_status()
        models=response.json()
        return [model['name'] for model in models['models']]
