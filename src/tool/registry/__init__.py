from src.tool.registry.views import Function,ToolResult
from src.tool import Tool

class Registry:
    def __init__(self,tools:list[Tool]):
        self.tools=tools
        self.tools_registry=self.registry()
    
    def tools_prompt(self):
        prompts=[]
        for tool in self.tools:
            prompts.append(tool.get_prompt())
        return '\n\n'.join(prompts)
    
    def registry(self)->dict[str,Function]:
        tools_registry={}
        for tool in self.tools:
            tools_registry.update({tool.name : Function(name=tool.name,description=tool.description,params=tool.params,function=tool.func)})
        return tools_registry

    async def async_execute(self,name:str,input:dict,**kwargs)->ToolResult:
        tool=self.tools_registry.get(name)
        try:
            if tool is None:
                raise ValueError('Tool not found')
            if tool.params:
                tool_params=tool.params.model_validate(input)
                params=tool_params.model_dump()|kwargs
            else:
                params=input|kwargs
            content=await tool.function(**params)
            return ToolResult(name=name,content=content)
        except Exception as e:
            return ToolResult(name=name,content=str(e))

    def execute(self,name:str,input:dict,**kwargs)->ToolResult:
        tool=self.tools_registry.get(name)
        try:
            if tool is None:
                raise ValueError('Tool not found')
            if tool.params:
                tool_params=tool.params.model_validate(input)
                params=tool_params.model_dump()|kwargs
            else:
                params=input|kwargs
            content=tool.function(**params)
            return ToolResult(name=name,content=content)
        except Exception as e:
            return ToolResult(name=name,content=str(e))
    
