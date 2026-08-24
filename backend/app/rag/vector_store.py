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

    # 类级别缓存，多个实例共享
    _clients: Dict[str, chromadb.PersistentClient] = {}
    _collections: Dict[str, chromadb.Collection] = {}

    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name
        self.client = self._get_client()
        self._collection = None

    def _get_client(self) -> chromadb.PersistentClient:
        """Get or create ChromaDB client (with caching)."""
        cache_key = f"{settings.CHROMA_PERSIST_DIR}:{self.collection_name}"
        if cache_key not in VectorStore._clients:
            os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
            VectorStore._clients[cache_key] = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
        return VectorStore._clients[cache_key]

    def get_or_create_collection(self) -> chromadb.Collection:
        """Get or create the collection (cached)."""
        if self._collection is None:
            cache_key = f"{self.collection_name}"
            if cache_key not in VectorStore._collections:
                VectorStore._collections[cache_key] = self.client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"description": "Document embeddings for RAG", "hnsw:space": "cosine"}
                )
            self._collection = VectorStore._collections[cache_key]
        return self._collection

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
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
        min_score: float = 0.3
    ) -> List[SearchResult]:
        """Search for similar chunks.

        Args:
            query_embedding: The query embedding vector
            document_ids: Optional list of document IDs to filter by (NEW: supports multiple)
            top_k: Number of results to return
            min_score: Minimum similarity score
        """
        collection = self.get_or_create_collection()

        # 优化：支持多文档一次查询
        where: Optional[Dict[str, Any]] = None
        n_results = top_k

        if document_ids:
            if len(document_ids) == 1:
                where = {"document_id": document_ids[0]}
            else:
                # ChromaDB 支持 $in 操作符进行多值过滤
                where = {"document_id": {"$in": document_ids}}
                # 多文档需要更多结果以保证召回
                n_results = top_k * len(document_ids)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
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

        # 如果是多文档搜索，按分数排序后截取 top_k
        if document_ids and len(document_ids) > 1:
            search_results.sort(key=lambda x: x.score, reverse=True)
            search_results = search_results[:top_k]

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
        self._collection = None
        VectorStore._collections.pop(self.collection_name, None)

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