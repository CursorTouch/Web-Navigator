from src.vectorstore.base import BaseVectorStore,Document
from src.embedding import BaseEmbedding
from chromadb.config import Settings
from chromadb import Client
from pathlib import Path

class ChromaDBVectorStore(BaseVectorStore):
    def __init__(self,collection_name:str,embedding:BaseEmbedding,path:Path=Path.cwd()/'.chroma'):
        self.settings=Settings(anonymized_telemetry=False,is_persistent=True,persist_directory=path.as_posix())
        self.client=Client(settings=self.settings)
        self.db=self.create_collection(collection_name=collection_name,embedding=embedding)

    def create_collection(self,collection_name:str,embedding:BaseEmbedding=None):
        return self.client.get_or_create_collection(name=collection_name,embedding_function=embedding)

    def insert(self,documents:list[Document]):
        ids=[doc.id for doc in documents]
        contents=[doc.content for doc in documents]
        metadatas=[doc.metadata for doc in documents]
        self.db.add(ids=ids,documents=contents,metadatas=metadatas)

    def search(self, query:str, k=5):
        return self.db.query(query_texts=[query],n_results=k)
    
    def update(self, id:str, content:str, metadata:dict):
        self.db.update(ids=[id],documents=[content],metadatas=[metadata])
    
    def delete(self, id):
        self.db.delete(ids=[id])

    def get(self, id):
        response = self.db.get(ids=[id])
        return self.parse_db_response(response)

    def delete_collection(self, collection_name):
        self.client.delete_collection(name=collection_name)

    def all_collections(self):
        return self.client.list_collections()

    def all(self):
        response=self.db.get()
        return self.parse_db_response(response)
    
    def parse_db_response(self, response: dict) -> list[Document]:
        ids = response.get('ids', [])
        documents = response.get('documents', [])
        metadatas = response.get('metadatas', [])
        result = []
        for i in range(len(ids)):
            doc = Document(
                id=ids[i],
                content=documents[i] if i < len(documents) else '',
                metadata=metadatas[i] if i < len(metadatas) else {}
            )
            result.append(doc)
        return result
        