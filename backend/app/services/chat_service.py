"""Chat service for managing conversations with RAG"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.chat import ChatSession, ChatMessage
from app.rag.rag_service import RAGService


class ChatService:
    """Service for managing chat sessions and RAG queries"""

    def __init__(self):
        self.rag_service = RAGService()

    def create_session(
        self,
        db: Session,
        user_id: int,
        title: Optional[str] = None
    ) -> ChatSession:
        """Create a new chat session."""
        session = ChatSession(
            title=title or "New Chat",
            user_id=user_id
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    def get_session(
        self,
        db: Session,
        session_id: int,
        user_id: int
    ) -> ChatSession:
        """Get a chat session."""
        session = db.query(ChatSession).filter(
            ChatSession.id == session_id,
            ChatSession.user_id == user_id
        ).first()
        if not session:
            raise ValueError("Session not found")
        return session

    def list_sessions(
        self,
        db: Session,
        user_id: int,
        limit: int = 50
    ) -> List[ChatSession]:
        """List user's chat sessions."""
        return db.query(ChatSession).filter(
            ChatSession.user_id == user_id
        ).order_by(ChatSession.updated_at.desc()).limit(limit).all()

    def send_message(
        self,
        db: Session,
        user_id: int,
        message: str,
        session_id: Optional[int] = None,
        document_id: Optional[int] = None,
        use_history: bool = True
    ) -> Dict[str, Any]:
        """Send a message and get RAG response."""
        session = None

        if session_id:
            session = self.get_session(db, session_id, user_id)
        else:
            session = self.create_session(db, user_id, message[:50])

        user_msg = ChatMessage(
            session_id=session.id,
            role="user",
            content=message,
            token_count=len(message)
        )
        db.add(user_msg)
        db.commit()

        history_context = ""
        if use_history:
            history_context = self._get_context_from_history(db, session.id)

        if history_context:
            full_query = f"{history_context}\n\nCurrent question: {message}"
        else:
            full_query = message

        try:
            response = self.rag_service.query(
                db,
                full_query,
                user_id,
                document_id=document_id
            )
            answer = response.answer
            sources = response.sources
        except Exception as e:
            answer = f"I encountered an error: {str(e)}"
            sources = []

        ai_msg = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=answer,
            token_count=len(answer)
        )
        db.add(ai_msg)
        db.commit()

        if not session.title or session.title == "New Chat":
            session.title = message[:50]
            db.commit()

        return {
            "session_id": session.id,
            "message": answer,
            "sources": [
                {
                    "text": s.text[:200] + "..." if len(s.text) > 200 else s.text,
                    "score": s.score,
                    "document_id": s.document_id
                }
                for s in sources
            ]
        }

    def _get_context_from_history(
        self,
        db: Session,
        session_id: int,
        max_messages: int = 10
    ) -> str:
        """Get context from conversation history."""
        messages = db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.desc()).limit(max_messages).all()

        if not messages:
            return ""

        history_parts = []
        for msg in reversed(messages):
            role = "User" if msg.role == "user" else "Assistant"
            history_parts.append(f"{role}: {msg.content}")

        return "\n".join(history_parts)

    def get_session_messages(
        self,
        db: Session,
        session_id: int,
        user_id: int
    ) -> List[ChatMessage]:
        """Get messages for a session."""
        session = self.get_session(db, session_id, user_id)
        return db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).order_by(ChatMessage.created_at.asc()).all()

    def delete_session(
        self,
        db: Session,
        session_id: int,
        user_id: int
    ) -> None:
        """Delete a chat session."""
        session = self.get_session(db, session_id, user_id)
        db.query(ChatMessage).filter(
            ChatMessage.session_id == session_id
        ).delete()
        db.delete(session)
        db.commit()

    def index_document(
        self,
        db: Session,
        document_id: int,
        user_id: int
    ) -> int:
        """Index a document for RAG."""
        return self.rag_service.index_document(db, document_id)

    def get_index_stats(self) -> Dict[str, Any]:
        """Get RAG index statistics."""
        return self.rag_service.get_index_stats()