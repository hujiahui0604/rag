"""Retriever utilities"""
from typing import List, Dict, Any

from .chroma_client import ChromaClient


class Retriever:
    """Document retriever using Chroma"""

    def __init__(self, chroma_client: ChromaClient):
        self.client = chroma_client

    def get_relevant_docs(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        results = self.client.query(query, n_results=k)

        documents = []
        if results["documents"]:
            for i, doc in enumerate(results["documents"][0]):
                documents.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results.get("distances") else None
                })

        return documents