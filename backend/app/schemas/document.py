"""Document Schemas"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[int] = None


class DocumentVersionResponse(BaseModel):
    id: int
    version_number: int
    file_path: str
    chunk_count: int
    created_by: int
    created_at: datetime
    is_current: bool = False

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(DocumentBase):
    id: int
    file_type: str
    file_size: int
    status: str
    chunk_count: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    current_version: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int