"""ChromaDB client for vector storage"""
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from ..config import CHROMA_PATH, EMBEDDING_MODEL, OPENAI_API_KEY


class ChromaClient:
    """ChromaDB client wrapper"""

    def __init__(self, collection_name: str = "documents"):
        self.client = chromadb.PersistentClient(path=CHROMA_PATH)
        self.collection_name = collection_name
        self.collection = self._get_or_create_collection()

    def _get_or_create_collection(self):
        """Get or create the documents collection"""
        return self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "RAG document embeddings"}
        )

    def add_documents(self, documents: List[str], metadatas: Optional[List[Dict]] = None, ids: Optional[List[str]] = None):
        """Add documents to the collection"""
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        if metadatas is None:
            metadatas = [{} for _ in documents]

        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )

    def query(self, query_text: str, n_results: int = 4) -> Dict[str, Any]:
        """Query the vector store"""
        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )
        return results

    def delete_collection(self):
        """Delete the collection"""
        self.client.delete_collection(self.collection_name)

    def get_count(self) -> int:
        """Get the number of documents in the collection"""
        return self.collection.count()


def get_embedding_function():
    """Get the OpenAI embedding function"""
    try:
        from langchain_openai import OpenAIEmbeddings
    except ImportError:
        from langchain.embeddings import OpenAIEmbeddings

    return OpenAIEmbeddings(
        model=EMBEDDING_MODEL,
        api_key=OPENAI_API_KEY
    )