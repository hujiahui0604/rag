"""RAG service - combines retrieval and generation"""
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import os

from sqlalchemy.orm import Session

from app.models.document import Document
from app.rag.document_processor import DocumentProcessor, DocumentChunk
from app.rag.chunker import TextChunker
from app.rag.vector_store import VectorStore, SearchResult
from app.rag.embedding import EmbeddingService, MockEmbeddingService
from app.rag.llm import LLMService
from app.config import settings
from app.constants import DEFAULT_TOP_K, DOC_STATUS_COMPLETED


@dataclass
class RAGResponse:
    """Response from RAG query"""
    answer: str
    sources: List[SearchResult]
    query: str


class RAGService:
    """Main RAG service for document retrieval and answer generation"""

    def __init__(self):
        self.chunker = TextChunker()
        self.vector_store = VectorStore()
        self.embedding_service = None
        self.llm_service = None
        self._initialize_services()

    def _initialize_services(self):
        """Initialize embedding and LLM services."""
        try:
            self.embedding_service = EmbeddingService()
            self.llm_service = LLMService()
        except Exception:
            self.embedding_service = MockEmbeddingService()
            self.llm_service = None

    def index_document(
        self,
        db: Session,
        document_id: int,
        force: bool = False
    ) -> int:
        """Index a document for search."""
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise ValueError(f"Document {document_id} not found")

        if not os.path.exists(document.file_path):
            raise FileNotFoundError(f"File not found: {document.file_path}")

        existing_chunks = self.vector_store.get_document_chunks(document_id)
        if existing_chunks and not force:
            return len(existing_chunks)

        if existing_chunks:
            self.vector_store.delete_document(document_id)

        chunks = DocumentProcessor.process(document.file_path, document.file_type)
        text_chunks = []
        for chunk in chunks:
            text_chunks.extend(
                self.chunker.chunk_text(chunk.content, document_id)
            )

        if not text_chunks:
            return 0

        texts = [c.text for c in text_chunks]
        embeddings = self.embedding_service.embed_texts(texts)

        valid_chunks = []
        valid_embeddings = []
        for chunk, embedding in zip(text_chunks, embeddings):
            if embedding:
                valid_chunks.append(chunk)
                valid_embeddings.append(embedding)

        if valid_chunks:
            self.vector_store.add_chunks(valid_chunks, valid_embeddings)

        document.chunk_count = len(valid_chunks)
        document.status = DOC_STATUS_COMPLETED
        db.commit()

        return len(valid_chunks)

    def query(
        self,
        db: Session,
        query: str,
        user_id: int,
        top_k: int = DEFAULT_TOP_K,
        document_id: Optional[int] = None
    ) -> RAGResponse:
        """Query the RAG system."""
        query_embedding = self.embedding_service.embed_text(query)

        user_doc_ids = self._get_user_document_ids(db, user_id)
        if document_id:
            if document_id not in user_doc_ids:
                raise ValueError("Access denied to document")
            search_docs = [document_id]
        else:
            search_docs = user_doc_ids

        if not search_docs:
            return RAGResponse(
                answer="No documents available. Please upload and index some documents first.",
                sources=[],
                query=query
            )

        all_results = []
        for doc_id in search_docs:
            results = self.vector_store.search(
                query_embedding,
                document_id=doc_id,
                top_k=top_k
            )
            all_results.extend(results)

        all_results.sort(key=lambda x: x.score, reverse=True)
        top_results = all_results[:top_k]

        if not top_results:
            return RAGResponse(
                answer="No relevant information found in the documents.",
                sources=[],
                query=query
            )

        if self.llm_service:
            try:
                response = self.llm_service.generate_with_sources(
                    query, top_results, self._get_system_prompt()
                )
                return RAGResponse(
                    answer=response["answer"],
                    sources=top_results,
                    query=query
                )
            except Exception as e:
                return RAGResponse(
                    answer=self._generate_simple_response(query, top_results),
                    sources=top_results,
                    query=query
                )
        else:
            return RAGResponse(
                answer=self._generate_simple_response(query, top_results),
                sources=top_results,
                query=query
            )

    def _get_user_document_ids(self, db: Session, user_id: int) -> List[int]:
        """Get document IDs the user has access to."""
        from app.models.user import User
        from app.models.permission import DocumentPermission

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return []

        if user.role == "admin":
            docs = db.query(Document.id).filter(
                Document.status == DOC_STATUS_COMPLETED
            ).all()
            return [d[0] for d in docs]

        docs = db.query(Document.id).filter(
            Document.created_by == user_id,
            Document.status == DOC_STATUS_COMPLETED
        ).all()
        user_doc_ids = [d[0] for d in docs]

        perms = db.query(DocumentPermission.document_id).filter(
            DocumentPermission.user_id == user_id
        ).all()
        perm_doc_ids = [p[0] for p in perms]

        return list(set(user_doc_ids + perm_doc_ids))

    def _get_system_prompt(self) -> str:
        """Get the system prompt for the LLM."""
        return """You are a helpful AI assistant that answers questions based on the provided documents.
Be accurate and cite the sources when possible. If you cannot find the answer in the context, say so honestly."""

    def _generate_simple_response(
        self,
        query: str,
        sources: List[SearchResult]
    ) -> str:
        """Generate a simple response without LLM."""
        if not sources:
            return "No relevant information found."

        response = "Based on the retrieved documents:\n\n"
        for i, source in enumerate(sources[:3], 1):
            text = source.text[:300] + "..." if len(source.text) > 300 else source.text
            response += f"Source {i} (relevance: {source.score:.2f}):\n{text}\n\n"

        return response

    def delete_document_index(self, document_id: int) -> None:
        """Delete document from vector store."""
        self.vector_store.delete_document(document_id)

    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the vector store."""
        return {
            "total_chunks": self.vector_store.count(),
            "embedding_model": settings.EMBEDDING_MODEL,
            "llm_model": settings.OLLAMA_MODEL if self.llm_service else None
        }