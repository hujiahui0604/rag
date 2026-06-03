"""Query engine for RAG"""
from typing import Dict, Any, List
import json

from ..vectorstore.chroma_client import ChromaClient
from ..vectorstore.retriever import Retriever
from ..llm.openai_adapter import OpenAILLM


class QueryEngine:
    """Main query engine for RAG"""

    def __init__(self, chroma_client: ChromaClient, llm_provider: str = "openai"):
        self.retriever = Retriever(chroma_client)
        self.llm = self._get_llm(llm_provider)

    def _get_llm(self, provider: str):
        """Get LLM adapter based on provider"""
        if provider == "openai":
            return OpenAILLM()
        # Add other providers as needed
        return OpenAILLM()

    def query(self, question: str) -> Dict[str, Any]:
        """Process a query and return answer with sources"""
        # Retrieve relevant documents
        docs = self.retriever.get_relevant_docs(question, k=4)

        if not docs:
            return {
                "answer": "No relevant documents found. Please add documents to the data/documents folder and rebuild the index.",
                "sources": []
            }

        # Build context from retrieved documents
        context = "\n\n".join([doc["content"] for doc in docs])

        # Generate answer using LLM
        answer = self.llm.generate_answer(question, context)

        # Extract sources
        sources = list(set([doc["metadata"].get("source", "Unknown") for doc in docs if doc["metadata"]]))

        return {
            "answer": answer,
            "sources": sources,
            "context": context
        }

    def get_relevant_documents(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Get relevant documents without generating answer"""
        return self.retriever.get_relevant_docs(query, k=k)