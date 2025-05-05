from src.agent.web.tools import click_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool,scrape_tool,download_tool,tab_tool,forward_tool,menu_tool,done_tool,transcript_tool
from src.message import SystemMessage,HumanMessage,ImageMessage,AIMessage
from src.agent.web.utils import read_markdown_file,extract_agent_data
from src.agent.web.browser import Browser,BrowserConfig
from src.agent.web.context import Context,ContextConfig
from langgraph.graph import StateGraph,END,START
from src.agent.web.state import AgentState
from src.inference import BaseInference
from src.tool.registry import Registry
from src.memory import BaseMemory
from src.agent import BaseAgent
from pydantic import BaseModel
from datetime import datetime
from termcolor import colored
from src.tool import Tool
from pathlib import Path
import platform
import asyncio
import json

main_tools=[
    click_tool,goto_tool,key_tool,download_tool,
    type_tool,scroll_tool,wait_tool,menu_tool,
    back_tool,tab_tool,done_tool,forward_tool,
    transcript_tool
]

class WebAgent(BaseAgent):
    def __init__(self,config:BrowserConfig=None,additional_tools:list[Tool]=[],instructions:list=[],memory:BaseMemory=None,llm:BaseInference=None,max_iteration:int=10,use_vision:bool=False,verbose:bool=False,token_usage:bool=False) -> None:
        self.name='Web Agent'
        self.description='The Web Agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.'
        self.observation_prompt=read_markdown_file('./src/agent/web/prompt/observation.md')
        self.system_prompt=read_markdown_file('./src/agent/web/prompt/system.md')
        self.action_prompt=read_markdown_file('./src/agent/web/prompt/action.md')
        self.answer_prompt=read_markdown_file('./src/agent/web/prompt/answer.md')
        self.instructions=self.format_instructions(instructions)
        self.registry=Registry(main_tools+additional_tools)
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
        "Call LLM to make decision"
        ai_message=await self.llm.async_invoke(state.get('messages'))
        # print(ai_message.content)
        agent_data=extract_agent_data(ai_message.content)
        memory=agent_data.get('Memory')
        evaluate=agent_data.get("Evaluate")
        thought=agent_data.get('Thought')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Evaluate: {evaluate}',color='light_yellow',attrs=['bold']))
            print(colored(f'Memory: {memory}',color='light_green',attrs=['bold']))
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data,'messages':[ai_message],'route':route}

    async def action(self,state:AgentState):
        "Execute the provided action"
        agent_data=state.get('agent_data')
        memory=agent_data.get('Memory')
        evaluate=agent_data.get("Evaluate")
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input=agent_data.get('Action Input')
        if self.verbose:
            print(colored(f'Action Name: {action_name}',color='blue',attrs=['bold']))
            print(colored(f'Action Input: {action_input}',color='blue',attrs=['bold']))
        action_result=await self.registry.async_execute(action_name,action_input,context=self.context)
        observation=action_result.content
        if self.verbose:
            print(colored(f'Observation: {observation}',color='green',attrs=['bold']))
        state['messages'].pop() # Remove the last message for modification
        last_message=state['messages'][-1] # ImageMessage/HumanMessage
        if isinstance(last_message,(ImageMessage,HumanMessage)):
            state['messages'][-1]=HumanMessage(f'<Observation>{state.get('prev_observation')}</Observation>')
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
        # Get the current browser state
        browser_state=await self.context.get_state(use_vision=self.use_vision)
        image_obj=browser_state.screenshot
        current_tab=browser_state.current_tab
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
            'interactive_elements':browser_state.dom_state.interactive_elements_to_string(),
            'informative_elements':browser_state.dom_state.informative_elements_to_string()
        })
        messages=[AIMessage(action_prompt),ImageMessage(text=observation_prompt,image_obj=image_obj) if self.use_vision else HumanMessage(observation_prompt)]
        return {**state,'messages':messages,'prev_observation':observation}

    async def answer(self,state:AgentState):
        "Give the final answer"
        state['messages'].pop() # Remove the last message for modification
        last_message=state['messages'][-1] # ImageMessage/HumanMessage
        if isinstance(last_message,(ImageMessage,HumanMessage)):
            state['messages'][-1]=HumanMessage(f'<Observation>{state.get('prev_observation')}</Observation>')
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
        messages=[AIMessage(answer_prompt)]
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer,'messages':messages}
    
    def structured(self,state:AgentState):
        "Give the structured output"
        messages=[SystemMessage('## Structured Output'),HumanMessage(state.get('output'))]
        structured_output=self.llm.invoke(messages=messages,model=self.structured_output)
        return {**state,'output':structured_output}

    def main_controller(self,state:AgentState):
        "Route to the next node"
        if self.iteration<self.max_iteration:
            self.iteration+=1
            agent_data=state.get('agent_data')
            action_name=agent_data.get('Action Name')
            if action_name!='Done Tool':
                return 'action'
        return 'answer'
        
    def output_controller(self,state:AgentState):
        if self.structured_output:
            return 'structured'
        else:
            return END

    def create_graph(self):
        "Create the graph"
        graph=StateGraph(AgentState)
        graph.add_node('reason',self.reason)
        graph.add_node('action',self.action)
        graph.add_node('answer',self.answer)
        graph.add_node('structured',self.structured)

        graph.add_edge(START,'reason')
        graph.add_conditional_edges('reason',self.main_controller)
        graph.add_edge('action','reason')
        graph.add_conditional_edges('answer',self.output_controller)
        graph.add_edge('structured',END)

        return graph.compile(debug=False)
    
    async def async_invoke(self, input: str, structured_output:BaseModel=None)->dict|BaseModel:
        self.iteration=0
        self.structured_output=structured_output
        tools_prompt=self.registry.tools_prompt()
        current_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_prompt=self.system_prompt.format(**{
            'instructions':self.instructions,
            'current_datetime':current_datetime,
            'tools_prompt':tools_prompt,
            'max_iteration':self.max_iteration,
            'os':platform.system(),
            'browser':self.browser.config.browser.capitalize(),
            'home_dir':Path.home().as_posix(),
            'downloads_dir':self.browser.config.downloads_dir
        })
        # Attach memory layer to the system prompt
        if self.memory and self.memory.retrieve(input):
            system_prompt=self.memory.attach_memory(system_prompt)
        human_prompt=f'Task: {input}'
        messages=[SystemMessage(system_prompt),HumanMessage(human_prompt)]
        state={
            'input':input,
            'agent_data':{},
            'output':'',
            'messages':messages
        }
        self.start_time=datetime.now()
        response=await self.graph.ainvoke(state,config={'recursion_limit':self.max_iteration})
        await self.close()
        self.end_time=datetime.now()
        total_seconds=(self.end_time-self.start_time).total_seconds()
        if self.verbose and self.token_usage:
            print(f'Input Tokens: {self.llm.tokens.input} Output Tokens: {self.llm.tokens.output} Total Tokens: {self.llm.tokens.total}')
            print(f'Total Time Taken: {total_seconds} seconds Number of Steps: {self.iteration}')
        # Extract and store the key takeaways of the task performed by the agent
        if self.memory:
            self.memory.store(response.get('messages'))
        return response
        
    def invoke(self, input: str,structured_output:BaseModel=None)->dict|BaseModel:
        if self.verbose:
            print(f'Entering '+colored(self.name,'black','on_white'))
        try:
            loop=asyncio.get_event_loop()
            response=loop.run_until_complete(self.async_invoke(input=input,structured_output=structured_output))
        except RuntimeError as e:
            print('RuntimeError:',e)
            response={'input':input,
            'agent_data':{},
            'output':f'Error: {e}',
            'messages':[]}
        return response
    
    async def close(self):
        '''Close the browser and context followed by clean up'''
        try:
            await self.context.close_session()
            await self.browser.close_browser()
        except Exception as e:
            print('Failed to finish clean up')
        finally:
            self.context=None
            self.browser=None

    def stream(self, input:str):
        pass

