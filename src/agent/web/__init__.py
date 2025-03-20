from src.agent.web.tools import click_tool,clipboard_tool,goto_tool,type_tool,scroll_tool,wait_tool,back_tool,key_tool,extract_tool,download_tool,tab_tool,upload_tool,menu_tool,form_tool
from src.message import SystemMessage,HumanMessage,ImageMessage,AIMessage
from src.agent.web.utils import read_markdown_file,extract_agent_data
from src.agent.web.browser import Browser,BrowserConfig
from src.agent.web.context import Context,ContextConfig
from langgraph.graph import StateGraph,END,START
from src.memory.episodic import EpisodicMemory
from src.agent.web.registry import Registry
from src.agent.web.state import AgentState
from src.inference import BaseInference
from src.agent import BaseAgent
from datetime import datetime
from termcolor import colored
from src.tool import Tool
from pathlib import Path
import platform
import asyncio
import json

main_tools=[
    download_tool,click_tool,goto_tool,extract_tool,type_tool,menu_tool,scroll_tool,
    wait_tool,clipboard_tool,back_tool,key_tool,tab_tool,upload_tool
]

class WebAgent(BaseAgent):
    def __init__(self,config:BrowserConfig=None,additional_tools:list[Tool]=[],instructions:list=[],episodic_memory:EpisodicMemory=None,llm:BaseInference=None,max_iteration:int=10,use_vision:bool=False,verbose:bool=False,token_usage:bool=False) -> None:
        self.name='Web Agent'
        self.description='The web agent is designed to automate the process of gathering information from the internet, such as to navigate websites, perform searches, and retrieve data.'
        self.observation_prompt=read_markdown_file('./src/agent/web/prompt/observation.md')
        self.system_prompt=read_markdown_file('./src/agent/web/prompt/system.md')
        self.action_prompt=read_markdown_file('./src/agent/web/prompt/action.md')
        self.answer_prompt=read_markdown_file('./src/agent/web/prompt/answer.md')
        self.instructions=self.format_instructions(instructions)
        self.registry=Registry(main_tools+additional_tools)
        self.browser=Browser(config=config)
        self.context=Context(self.browser)
        self.episodic_memory=episodic_memory
        self.max_iteration=max_iteration
        self.token_usage=token_usage
        self.use_vision=use_vision
        self.verbose=verbose
        self.iteration=0
        self.llm=llm
        self.graph=self.create_graph()

    def format_instructions(self,instructions):
        return '\n'.join([f'{i+1}. {instruction}' for (i,instruction) in enumerate(instructions)])

    async def reason(self,state:AgentState):
        "Call LLM to make decision"
        ai_message=await self.llm.async_invoke(state.get('messages'))
        print(ai_message.content)
        agent_data=extract_agent_data(ai_message.content)
        evaluate=agent_data.get("Evaluate")
        thought=agent_data.get('Thought')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Evaluate: {evaluate}',color='light_yellow',attrs=['bold']))
            print(colored(f'Thought: {thought}',color='light_magenta',attrs=['bold']))
        return {**state,'agent_data': agent_data,'messages':[ai_message],'route':route}

    async def action(self,state:AgentState):
        "Execute the provided action"
        agent_data=state.get('agent_data')
        evaluate=agent_data.get("Evaluate")
        thought=agent_data.get('Thought')
        action_name=agent_data.get('Action Name')
        action_input=agent_data.get('Action Input')
        route=agent_data.get('Route')
        if self.verbose:
            print(colored(f'Action Name: {action_name}',color='blue',attrs=['bold']))
            print(colored(f'Action Input: {action_input}',color='blue',attrs=['bold']))
        action_result=await self.registry.execute(action_name,action_input,self.context)
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
        # print('Tabs',browser_state.tabs_to_string())
        # print(browser_state.dom_state.elements_to_string())
        # Redefining the AIMessage and adding the new observation
        action_prompt=self.action_prompt.format(evaluate=evaluate,thought=thought,action_name=action_name,action_input=json.dumps(action_input,indent=2),route=route)
        observation_prompt=self.observation_prompt.format(iteration=self.iteration,max_iteration=self.max_iteration,observation=observation,current_url=browser_state.url,tabs=browser_state.tabs_to_string(),interactive_elements=browser_state.dom_state.elements_to_string())
        messages=[AIMessage(action_prompt),ImageMessage(text=observation_prompt,image_obj=image_obj) if self.use_vision else HumanMessage(observation_prompt)]
        return {**state,'agent_data':agent_data,'messages':messages,'prev_observation':observation}

    def final(self,state:AgentState):
        "Give the final answer"
        state['messages'].pop() # Remove the last message for modification
        last_message=state['messages'][-1] # ImageMessage/HumanMessage
        if isinstance(last_message,(ImageMessage,HumanMessage)):
            state['messages'][-1]=HumanMessage(f'<Observation>{state.get('prev_observation')}</Observation>')
        if self.iteration<self.max_iteration:
            agent_data=state.get('agent_data')
            evaluate=agent_data.get("Evaluate")
            thought=agent_data.get('Thought')
            final_answer=agent_data.get('Final Answer')
        else:
            thought='Looks like I have reached the maximum iteration limit reached.',
            final_answer='Maximum Iteration reached.'
        answer_prompt=self.answer_prompt.format(evaluate=evaluate,thought=thought,final_answer=final_answer)
        messages=[AIMessage(answer_prompt)]
        if self.verbose:
            print(colored(f'Final Answer: {final_answer}',color='cyan',attrs=['bold']))
        return {**state,'output':final_answer,'messages':messages}
    
    def controller(self,state:AgentState):
        "Route to the next node"
        if self.iteration<self.max_iteration:
            self.iteration+=1
            return state.get('route').lower()
        else:
            return 'final'

    def create_graph(self):
        "Create the graph"
        graph=StateGraph(AgentState)
        graph.add_node('reason',self.reason)
        graph.add_node('action',self.action)
        graph.add_node('final',self.final)

        graph.add_edge(START,'reason')
        graph.add_conditional_edges('reason',self.controller)
        graph.add_edge('action','reason')
        graph.add_edge('final',END)

        return graph.compile(debug=False)
    
    async def async_invoke(self, input: str):
        self.iteration=0
        actions_prompt=self.registry.actions_prompt()
        current_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        system_prompt=self.system_prompt.format(**{
            'instructions':self.instructions,
            'current_datetime':current_datetime,
            'actions_prompt':actions_prompt,
            'max_iteration':self.max_iteration,
            'os':platform.system(),
            'browser':self.browser.config.browser.capitalize(),
            'home_dir':Path.home().as_posix(),
            'downloads_dir':self.browser.config.downloads_dir
        })
        # Attach episodic memory to the system prompt 
        if self.episodic_memory and self.episodic_memory.retrieve(input):
            system_prompt=self.episodic_memory.attach_memory(system_prompt)
        human_prompt=f'Task: {input}'
        print(human_prompt)
        messages=[SystemMessage(system_prompt),HumanMessage(human_prompt)]
        state={
            'input':input,
            'agent_data':{},
            'output':'',
            'route':'',
            'messages':messages
        }
        response=await self.graph.ainvoke(state,config={'recursion_limit':self.max_iteration})
        await self.close()
        # Extract and store the key takeaways of the task performed by the agent
        if self.episodic_memory:
            self.episodic_memory.store(response.get('messages'))
        return response.get('output')
        
    def invoke(self, input: str)->str:
        if self.verbose:
            print(f'Entering '+colored(self.name,'black','on_white'))
        output=asyncio.run(self.async_invoke(input=input))       
        return output

    def stream(self, input:str):
        pass

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

