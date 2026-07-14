"""Document Models"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base


class Document(Base):
    """文档模型"""
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=True)

    current_version_id = Column(Integer, ForeignKey("document_versions.id", use_alter=True), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

    status = Column(String(20), default="processing")
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关系
    versions = relationship(
        "DocumentVersion",
        back_populates="document",
        order_by="desc(DocumentVersion.version_number)",
        foreign_keys="DocumentVersion.document_id"
    )
    category = relationship("Category", back_populates="documents")
    creator = relationship("User", back_populates="documents", foreign_keys=[created_by])
    permissions = relationship("DocumentPermission", back_populates="document")


class DocumentVersion(Base):
    """文档版本模型"""
    __tablename__ = "document_versions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    chunk_count = Column(Integer, default=0)
    vector_dimension = Column(Integer, default=1536)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    # 关系
    document = relationship("Document", back_populates="versions", foreign_keys=[document_id])