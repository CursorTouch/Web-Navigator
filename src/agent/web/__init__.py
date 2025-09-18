from src.agent.web.tools import click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool,scrape_tool,tab_tool,forward_tool,done_tool,download_tool,human_tool,script_tool
from src.message import SystemMessage,HumanMessage,ImageMessage,AIMessage
from src.agent.web.utils import read_markdown_file,extract_agent_data
from src.agent.web.browser import Browser,BrowserConfig
from langgraph.graph import StateGraph,END,START
from src.agent.web.state import AgentState
from src.agent.web.context import Context
from src.inference import BaseInference
from src.tool.registry import Registry
from rich.markdown import Markdown
from src.memory import BaseMemory
from rich.console import Console
from src.agent import BaseAgent
from pydantic import BaseModel
from datetime import datetime
from termcolor import colored
from textwrap import dedent
from src.tool import Tool
from pathlib import Path
import textwrap
import platform
import asyncio
import json

main_tools=[
    click_tool,goto_tool,key_tool,scrape_tool,
    type_tool,scroll_tool,wait_tool,back_tool,
    tab_tool,done_tool,forward_tool,download_tool,
    script_tool
]

class Agent(BaseAgent):
    def __init__(self,config:BrowserConfig=None,additional_tools:list[Tool]=[],
    instructions:list=[],memory:BaseMemory=None,llm:BaseInference=None,max_iteration:int=10,
    use_vision:bool=False,include_human_in_loop:bool=False,verbose:bool=False,token_usage:bool=False) -> None:
        """
        Initializes the WebAgent object.

        Args:
            config (BrowserConfig, optional): Browser configuration. Defaults to None.
            additional_tools (list[Tool], optional): Additional tools to be used. Defaults to [].
            instructions (list, optional): Instructions for the agent. Defaults to [].
            memory (BaseMemory, optional): Memory object for the agent. Defaults to None.
            llm (BaseInference, optional): Large Language Model object. Defaults to None.
            max_iteration (int, optional): Maximum number of iterations. Defaults to 10.
            use_vision (bool, optional): Whether to use vision or not. Defaults to False.
            include_human_in_loop (bool, optional): Whether to include human in the loop or not. Defaults to False.
            verbose (bool, optional): Whether to print verbose output or not. Defaults to False.
            token_usage (bool, optional): Whether to track token usage or not. Defaults to False.

        Returns:
            None
        """
        self.name='Web Agent'
        self.description='The Web Agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.'
        self.observation_prompt=read_markdown_file('./src/agent/web/prompt/observation.md')
        self.system_prompt=read_markdown_file('./src/agent/web/prompt/system.md')
        self.action_prompt=read_markdown_file('./src/agent/web/prompt/action.md')
        self.answer_prompt=read_markdown_file('./src/agent/web/prompt/answer.md')
        self.instructions=self.format_instructions(instructions)
        self.registry=Registry(main_tools+additional_tools+([human_tool] if include_human_in_loop else []))
        self.include_human_in_loop=include_human_in_loop
        self.browser=Browser(config=config)
        self.context=Context(browser=self.browser)
        self.max_iteration=max_iteration
        self.token_usage=token_usage
        self.structured_output=None
        self.use_vision=use_vision
        self.verbose=verbose
        self.start_time=None
        self.memory=memory
        self.end_time=None
        self.iteration=0
        self.llm=llm
        self.graph=self.create_graph()

    def format_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    async def reason(self,state:AgentState):
        "Call LLM to make decision based on the current state of the browser"
        system_prompt=self.system_prompt.format(**{
            'os':platform.system(),
            'instructions':self.instructions,
            'home_dir':Path.home().as_posix(),
            'max_iteration':self.max_iteration,
            'human_in_loop':self.include_human_in_loop,
            'tools_prompt':self.registry.tools_prompt(),
            'browser':self.browser.config.browser.capitalize(),
            'downloads_dir':self.browser.config.downloads_dir,
            'current_datetime':datetime.now().strftime('%A, %B %d, %Y')
        })
        messages=[SystemMessage(system_prompt)]+state.get('messages')
        ai_message=await self.llm.async_invoke(messages=messages)
        agent_data=extract_agent_data(ai_message.content)
        memory=agent_data.get('Memory')
        evaluate=agent_data.get("Evaluate")
        thought=agent_data.get('Thought')
        if self.verbose:
            print(colored(f'Evaluate: {evaluate}',color='light_yellow',attrs=['bold']))
            print(colored(f'Memory: {memory}',color='light_green',attrs=['bold']))
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        last_message=state.get('messages').pop() # ImageMessage/HumanMessage. To remove the past browser state
        if isinstance(last_message,(ImageMessage,HumanMessage)):
            message=HumanMessage(dedent(f'''
            <Input>
                <AgentState>
                    Current Step: {self.iteration}

                    Max. Steps: {self.max_iteration}

                    Action Response: {state.get('prev_observation')}                
                </AgentState>
            </Input>                       
            '''))
            return {**state,'agent_data': agent_data,'messages':[message]}

    async def action(self,state:AgentState):
        "Execute the provided action"
        agent_data=state.get('agent_data')
        memory=agent_data.get('Memory')
        evaluate=agent_data.get("Evaluate")
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input:dict=agent_data.get('Action Input')
        if self.verbose:
            print(colored(f'Action: {action_name}({','.join([f'{k}={v}' for k,v in action_input.items()])})',color='blue',attrs=['bold']))
        action_result=await self.registry.async_execute(action_name,action_input,context=self.context)
        observation=action_result.content
        if self.verbose:
            print(colored(f'Observation: {textwrap.shorten(observation,width=1000,placeholder='...')}',color='green',attrs=['bold']))
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
        # Get the current screenshot,browser state and dom state
        browser_state=await self.context.get_state(use_vision=self.use_vision)
        current_tab=browser_state.current_tab
        dom_state=browser_state.dom_state
        image_obj=browser_state.screenshot
        # Redefining the AIMessage and adding the new observation
        action_prompt=self.action_prompt.format(**{
            'memory':memory,
            'evaluate':evaluate,
            'thought':thought,
            'action_name':action_name,
            'action_input':json.dumps(action_input,indent=2)
        })
        observation_prompt=self.observation_prompt.format(**{
            'iteration':self.iteration,
            'max_iteration':self.max_iteration,
            'observation':observation,
            'current_tab':current_tab.to_string(),
            'tabs':browser_state.tabs_to_string(),
            'interactive_elements':dom_state.interactive_elements_to_string(),
            'informative_elements':dom_state.informative_elements_to_string(),
            'scrollable_elements':dom_state.scrollable_elements_to_string(),
            'query':state.get('input')
        })
        messages=[AIMessage(action_prompt),ImageMessage(text=observation_prompt,image_obj=image_obj) if self.use_vision and image_obj is not None else HumanMessage(observation_prompt)]
        return {**state,'messages':messages,'browser_state':browser_state,'dom_state':dom_state,'prev_observation':observation}

    async def answer(self,state:AgentState):
        "Give the final answer"
        if self.iteration<self.max_iteration:
            agent_data=state.get('agent_data')
            evaluate=agent_data.get("Evaluate")
            memory=agent_data.get('Memory')
            thought=agent_data.get('Thought')
            action_name=agent_data.get('Action Name')
            action_input=agent_data.get('Action Input')
            action_result=await self.registry.async_execute(action_name,action_input,context=None)
            final_answer=action_result.content
        else:
            evaluate='I have reached the maximum iteration limit.'
            memory='I have reached the maximum iteration limit. Cannot procced further.'
            thought='Looks like I have reached the maximum iteration limit reached.',
            action_name='Done Tool'
            action_input='{"answer":"Maximum Iteration reached."}'
            final_answer='Maximum Iteration reached.'
        answer_prompt=self.answer_prompt.format(**{
            'memory':memory,
            'evaluate':evaluate,
            'thought':thought,
            'final_answer':final_answer
        })
        message=AIMessage(answer_prompt)
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        await self.close()
        return {**state,'browser_state':None,'dom_state':None,'output':final_answer,'messages':[message],'prev_observation':'','agent_data':{}}

    def main_controller(self,state:AgentState):
        "Route to the next node"
        if self.iteration<self.max_iteration:
            self.iteration+=1
            agent_data=state.get('agent_data')
            action_name=agent_data.get('Action Name')
            if action_name!='Done Tool':
                return 'action'
        return 'answer'

    def create_graph(self):
        "Create the graph"
        graph=StateGraph(AgentState)
        graph.add_node('reason',self.reason)
        graph.add_node('action',self.action)
        graph.add_node('answer',self.answer)

        graph.add_edge(START,'reason')
        graph.add_conditional_edges('reason',self.main_controller)
        graph.add_edge('action','reason')
        graph.add_edge('answer',END)

        return graph.compile(debug=False)
    
    async def async_invoke(self, input: str)->dict|BaseModel:
        self.iteration=0
        observation_prompt=self.observation_prompt.format(**{
            'iteration':self.iteration,
            'max_iteration':self.max_iteration,
            'memory':'Nothing to remember',
            'evaluate':'Nothing to evaluate',
            'thought':'Nothing to think',
            'action':'No Action',
            'observation':'No Observation',
            'current_tab':'No tabs open',
            'tabs':'No tabs open',
            'interactive_elements':'No interactive elements found',
            'informative_elements':'No informative elements found',
            'scrollable_elements':'No scrollable elements found',
            'query':input
        })
        state={
            'input':input,
            'agent_data':{},
            'prev_observation':'No Observation',
            'browser_state':None,
            'dom_state':None,
            'output':'',
            'messages':[HumanMessage(observation_prompt)]
        }
        self.start_time=datetime.now()
        response=await self.graph.ainvoke(state,config={'recursion_limit':self.max_iteration})
        self.end_time=datetime.now()
        total_seconds=(self.end_time-self.start_time).total_seconds()
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
            print(f'Total Time Taken: {total_seconds} seconds Number of Steps: {self.iteration}')
        # Extract and store the key takeaways of the task performed by the agent
        if self.memory:
            self.memory.store(response.get('messages'))
        return response
        
    def invoke(self, input: str)->dict|BaseModel:
        if self.verbose:
            print('Entering '+colored(self.name,'black','on_white'))
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        response = loop.run_until_complete(self.async_invoke(input=input))
        return response
    
    async def invoke_history(self, input: str)->dict|BaseModel:
        pass
    
    def print_response(self,input: str):
        console=Console()
        response=self.invoke(input)
        console.print(Markdown(response.get('output')))

    async def close(self):
        '''Close the browser and context followed by clean up'''
        try:
            await self.context.close_session()
            await self.browser.close_browser()
        except Exception:
            print('Failed to finish clean up')
        finally:
            self.context=None
            self.browser=None

    def stream(self, input:str):
        pass
