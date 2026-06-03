"""Vector store using ChromaDB"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.rag.chunker import Chunk


@dataclass
class SearchResult:
    """Represents a search result from vector store"""
    chunk_id: str
    document_id: int
    text: str
    score: float
    metadata: Dict[str, Any]


class VectorStore:
    """ChromaDB vector store for document embeddings"""

    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.client = self._get_client()
        self.collection = None

    def _get_client(self) -> chromadb.PersistentClient:
        """Get or create ChromaDB client."""
        os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
        return chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )

    def get_or_create_collection(self) -> chromadb.Collection:
        """Get or create the collection."""
        if self.collection is None:
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"description": "Document embeddings for RAG"}
            )
        return self.collection

    def add_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]) -> None:
        """Add chunks with embeddings to the vector store."""
        collection = self.get_or_create_collection()

        ids = [f"doc_{chunk.document_id}_chunk_{chunk.chunk_index}" for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        metadatas = [
            {
                "document_id": chunk.document_id,
                "chunk_index": chunk.chunk_index,
                "start_char": chunk.start_char,
                "end_char": chunk.end_char
            }
            for chunk in chunks
        ]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding: List[float],
        document_id: Optional[int] = None,
        top_k: int = 5,
        min_score: float = 0.3
    ) -> List[SearchResult]:
        """Search for similar chunks."""
        collection = self.get_or_create_collection()

        where = {"document_id": document_id} if document_id else None

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"]
        )

        search_results = []
        if results and results["ids"] and len(results["ids"]) > 0:
            for i, (doc_id, doc_text, metadata, distance) in enumerate(
                zip(
                    results["ids"][0],
                    results["documents"][0],
                    results["metadatas"][0],
                    results["distances"][0]
                )
            ):
                score = 1 - distance
                if score >= min_score:
                    search_results.append(SearchResult(
                        chunk_id=doc_id,
                        document_id=metadata.get("document_id", 0),
                        text=doc_text,
                        score=score,
                        metadata=metadata
                    ))

        return search_results

    def delete_document(self, document_id: int) -> None:
        """Delete all chunks for a document."""
        collection = self.get_or_create_collection()

        try:
            result = collection.get(where={"document_id": document_id})
            if result and result["ids"]:
                collection.delete(ids=result["ids"])
        except Exception:
            pass

    def reset(self) -> None:
        """Reset the collection (delete all data)."""
        self.client.delete_collection(self.collection_name)
        self.collection = None

    def count(self) -> int:
        """Get the number of chunks in the collection."""
        collection = self.get_or_create_collection()
        return collection.count()

    def get_document_chunks(self, document_id: int) -> List[SearchResult]:
        """Get all chunks for a specific document."""
        collection = self.get_or_create_collection()

        try:
            result = collection.get(where={"document_id": document_id})
            if result and result["ids"]:
                return [
                    SearchResult(
                        chunk_id=doc_id,
                        document_id=metadata.get("document_id", 0),
                        text=doc_text,
                        score=1.0,
                        metadata=metadata
                    )
                    for doc_id, doc_text, metadata in zip(
                        result["ids"],
                        result["documents"],
                        result["metadatas"]
                    )
                ]
        except Exception:
            pass
        return []