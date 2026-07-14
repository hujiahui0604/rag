"""User Model"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    documents = relationship("Document", back_populates="creator", foreign_keys="Document.created_by")
    chat_sessions = relationship("ChatSession", back_populates="user")
    permissions_granted = relationship("DocumentPermission", back_populates="granter", foreign_keys="DocumentPermission.granted_by")

    def __repr__(self):
        return f"<User {self.username}>"