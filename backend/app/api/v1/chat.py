"""Chat API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from app.deps import DBSession, CurrentActiveUser
from app.models.user import User
from app.models.chat import ChatSession, ChatMessage, Feedback
from app.schemas.chat import (
    ChatSessionResponse, ChatSessionCreate,
    ChatMessageResponse, ChatRequest, ChatResponse,
    FeedbackCreate, FeedbackResponse
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.get("/sessions", response_model=List[ChatSessionResponse])
def list_sessions(
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Get chat sessions."""
    sessions = db.query(ChatSession).filter(
        ChatSession.user_id == user.id
    ).order_by(ChatSession.updated_at.desc()).all()
    return [ChatSessionResponse.model_validate(s) for s in sessions]


@router.post("/sessions", response_model=ChatSessionResponse, status_code=201)
def create_session(
    data: ChatSessionCreate,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Create a chat session."""
    session = ChatSession(
        title=data.title,
        user_id=user.id
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return ChatSessionResponse.model_validate(session)


@router.get("/sessions/{session_id}", response_model=List[ChatMessageResponse])
def get_session_messages(
    session_id: int,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Get session messages."""
    session = db.query(ChatSession).filter(
        ChatSession.id == session_id,
        ChatSession.user_id == user.id
    ).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages = db.query(ChatMessage).filter(
        ChatMessage.session_id == session_id
    ).order_by(ChatMessage.created_at.asc()).all()

    return [ChatMessageResponse.model_validate(m) for m in messages]


@router.post("/message", response_model=ChatResponse)
def send_message(
    data: ChatRequest,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Send a message and get AI response."""
    from app.config import settings

    session = None
    if data.session_id:
        session = db.query(ChatSession).filter(
            ChatSession.id == data.session_id,
            ChatSession.user_id == user.id
        ).first()
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = ChatSession(
            title=data.message[:50],
            user_id=user.id
        )
        db.add(session)
        db.commit()
        db.refresh(session)

    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=data.message,
        token_count=len(data.message)
    )
    db.add(user_message)
    db.commit()

    response_content = f"AI response to: {data.message}"

    ai_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=response_content,
        token_count=len(response_content)
    )
    db.add(ai_message)
    session.updated_at = None
    db.commit()

    return ChatResponse(
        message=response_content,
        session_id=session.id,
        token_count=ai_message.token_count
    )


@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
def create_feedback(
    data: FeedbackCreate,
    message_id: int,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Add feedback to a message."""
    message = db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    feedback = Feedback(
        message_id=message_id,
        is_helpful=data.is_helpful,
        comment=data.comment
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    return FeedbackResponse.model_validate(feedback)