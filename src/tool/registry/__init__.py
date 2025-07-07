# src/tool/registry/__init__.py
from src.tool.registry.views import Function,ToolResult
from src.tool import Tool

class Registry:
    def __init__(self,tools:list[Tool]):
        self.tools=tools
        self.tools_registry=self.registry()

    def tools_prompt(self,excluded_tools:list[str]=[])->str:
        prompts=[]
        for tool in self.tools:
            if tool.name in excluded_tools:
                continue
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
            # Check if name is None or empty, which indicates an LLM failure
            if not name:
                raise ValueError('Action Name was None or empty. The LLM failed to choose a valid action.')

            if tool is None:
                raise ValueError(f'Tool "{name}" not found. Please choose from the available tools.')

            if tool.params:
                # Ensure input is a dictionary before validation
                if not isinstance(input, dict):
                     raise TypeError(f"Action Input for tool '{name}' must be a dictionary, but got {type(input)}: {input}")
                tool_params=tool.params.model_validate(input)
                params=tool_params.model_dump()|kwargs
            else:
                params=input|kwargs

            content=await tool.function(**params)
            return ToolResult(name=name,content=content)
        except Exception as e:
            # If 'name' was the issue, use a placeholder 'Invalid Action'
            # Otherwise, use the provided 'name'.
            error_name = name if name else "Invalid Action"
            error_content = f"Error executing tool '{error_name}': {str(e)}"
            print(f"DEBUG: Tool execution failed. Name: {name}, Input: {input}, Error: {e}")
            return ToolResult(name=error_name, content=error_content)

    def execute(self,name:str,input:dict,**kwargs)->ToolResult:
        tool=self.tools_registry.get(name)
        try:
            # Check if name is None or empty
            if not name:
                raise ValueError('Action Name was None or empty. The LLM failed to choose a valid action.')

            if tool is None:
                raise ValueError(f'Tool "{name}" not found. Please choose from the available tools.')

            if tool.params:
                # Ensure input is a dictionary before validation
                if not isinstance(input, dict):
                    raise TypeError(f"Action Input for tool '{name}' must be a dictionary, but got {type(input)}: {input}")
                tool_params=tool.params.model_validate(input)
                params=tool_params.model_dump()|kwargs
            else:
                params=input|kwargs

            content=tool.function(**params)
            return ToolResult(name=name,content=content)
        except Exception as e:
            error_name = name if name else "Invalid Action"
            error_content = f"Error executing tool '{error_name}': {str(e)}"
            print(f"DEBUG: Tool execution failed. Name: {name}, Input: {input}, Error: {e}")
            return ToolResult(name=error_name,content=error_content)