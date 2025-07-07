from src.vectorstore.views import Document
from abc import ABC,abstractmethod
from typing import Sequence

class BaseVectorStore(ABC):
    @abstractmethod
    def create_collection(self,collection_name:str)->None:
        pass

    @abstractmethod
    def insert(self,documents:list[Document])->None:
        pass

    @abstractmethod
    def search(self,query:str,k:int)->list[Document]:
        pass

    @abstractmethod
    def delete(self,collection_name:str)->None:
        pass

    @abstractmethod
    def update(self,id:str,content:str,metadata:dict)->None:
        pass

    @abstractmethod
    def delete_collection(self,collection_name:str)->None:
        pass

    @abstractmethod
    def get(self,id:str)->Document:
        pass

    @abstractmethod
    def all(self)->list[Document]:
        pass

    @abstractmethod
    def all_collections(self)->Sequence:
        pass

