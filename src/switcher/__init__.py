from src.inference import BaseInference
from src.message import BaseMessage,AIMessage

class Switcher:
    def __init__(self,llms:list[BaseInference],max_retries:int=3,max_iterations:int=10):
        self.llms = llms
        self.max_retries = max_retries
        self.current_index = 0
        self.max_iterations = max_iterations

    def add_llm(self,llm:BaseInference):
        self.llms.append(llm)

    def remove_llm(self,llm:BaseInference):
        self.llms.remove(llm)

    def switch_llm(self):
        self.current_index = (self.current_index + 1) % len(self.llms)

    def invoke(self,messages:list[BaseMessage],**kwargs)->AIMessage:
        iterations = 0
        while iterations < self.max_iterations:
            llm = self.llms[self.current_index]
            retries = 0
            while retries < self.max_retries:
                try:
                    return llm.invoke(messages, **kwargs)
                except Exception as e:
                    print(f"Error with {llm.__class__.__name__}: {e}. Retrying attempt {retries + 1}...")
                    retries += 1
            self.switch_llm()
            iterations += 1
            print(f"Switching to {self.llms[self.current_index].__class__.__name__}")
        raise Exception("All LLMs failed after maximum retries and iterations.")
    
    async def async_invoke(self,messages:list[BaseMessage],**kwargs)->AIMessage:
        iterations = 0
        while iterations < self.max_iterations:
            llm = self.llms[self.current_index]
            retries = 0
            while retries < self.max_retries:
                try:
                    return await llm.async_invoke(messages, **kwargs)
                except Exception as e:
                    print(f"Error with {llm.__class__.__name__}: {e}. Retrying attempt {retries + 1}...")
                    retries += 1
            self.switch_llm()
            iterations += 1
            print(f"Switching to {self.llms[self.current_index].__class__.__name__}")
        raise Exception("All LLMs failed after maximum retries and iterations.")