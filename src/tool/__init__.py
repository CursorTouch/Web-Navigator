from pydantic import BaseModel
from typing import Optional,Callable
from inspect import getdoc
from json import dumps

class Tool:
    def __init__(self, name: str='',description: Optional[str]=None, params: Optional[BaseModel]=None,schema:Optional[dict]=None,func:Optional[Callable]=None):
        self.name = name
        self.params = params
        self.func = func
        self.description = description
        self.schema = schema

    def __call__(self, func):
        if self.params:
            # Store the decorated function and its metadata
            self.description = self.description or getdoc(func)
            skip_keys=['title']
            if self.params is not None:
                self.schema = {k:{term:content for term,content in v.items() if term not in skip_keys} for k,v in self.params.model_json_schema().get('properties').items() if k not in skip_keys}
            elif self.schema is not None:
                self.schema = {k:{term:content for term,content in v.items() if term not in skip_keys} for k,v in self.schema.get('properties').items() if k not in skip_keys}
        self.func = func
        return self  # Return the Tool Instance

    def invoke(self, **kwargs):
        # Validate inputs using the schema and invoke the wrapped function
        try:
            if self.params:
                args = self.params(**kwargs)  # Validate arguments
                return self.func(**args.dict())  # Call the function with validated arg
            else:
                return self.func(**kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
    
    async def async_invoke(self, **kwargs):
        # Validate inputs using the schema and invoke the wrapped function
        try:
            if self.params:
                args = self.params(**kwargs)  # Validate arguments
                return await self.func(**args.dict())  # Call the function with validated arg
            else:
                return await self.func(**kwargs)
        except Exception as e:
            return f"Error: {str(e)}"
        
    def __repr__(self):
        if self.params is not None:
            params=list(self.params.model_fields.keys())
        elif self.schema is not None:
            params=list(self.schema.get('properties').keys())
        return f"Tool(name={self.name}, description={self.description}, params={params})"
    
    def get_prompt(self):
        return f'''Tool Name: {self.name}\nTool Description: {self.description}\nTool Input: {dumps(self.schema,indent=2)}'''