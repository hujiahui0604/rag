"""Chat Schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any
from datetime import datetime


class ChatMessageBase(BaseModel):
    role: str
    content: str
    sources: Optional[List[Any]] = None


class ChatMessageCreate(ChatMessageBase):
    session_id: Optional[int] = None


class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    token_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSessionBase(BaseModel):
    title: Optional[str] = None


class ChatSessionCreate(ChatSessionBase):
    pass


class ChatSessionResponse(ChatSessionBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FeedbackCreate(BaseModel):
    is_helpful: Optional[bool] = None
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    message_id: int
    is_helpful: Optional[bool] = None
    comment: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[int] = None
    use_history: bool = True


class ChatResponse(BaseModel):
    message: str
    sources: Optional[List[Any]] = None
    session_id: int
    token_count: int = 0