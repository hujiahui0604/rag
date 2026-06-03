"""Document API endpoints"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from typing import Optional, List

from app.deps import DBSession, CurrentActiveUser
from app.models.user import User
from app.schemas.document import DocumentResponse, DocumentCreate, DocumentUpdate, DocumentListResponse, DocumentVersionResponse

router = APIRouter(prefix="/documents", tags=["documents"])


@router.get("", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Get document list."""
    from app.models.document import Document
    from app.models.permission import DocumentPermission
    from app.constants import DOC_STATUS_PENDING

    query = db.query(Document).filter(Document.status != DOC_STATUS_PENDING)

    if user.role != "admin":
        query = query.filter(
            (Document.created_by == user.id) |
            (Document.id.in_(
                db.query(DocumentPermission.document_id).filter(
                    DocumentPermission.user_id == user.id
                )
            ))
        )

    if search:
        query = query.filter(Document.title.contains(search))

    if category_id:
        query = query.filter(Document.category_id == category_id)

    if status:
        query = query.filter(Document.status == status)

    query = query.order_by(Document.created_at.desc())

    total = query.count()
    offset = (page - 1) * page_size
    documents = query.offset(offset).limit(page_size).all()

    return DocumentListResponse(
        items=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=DocumentResponse, status_code=201)
async def create_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Upload a document."""
    from app.models.document import Document, DocumentVersion
    from app.constants import DOC_STATUS_PENDING
    import hashlib
    from pathlib import Path

    content = await file.read()

    file_ext = file.filename.split('.')[-1].lower() if '.' in file.filename else ''
    file_size = len(content)

    import uuid
    safe_filename = f"{uuid.uuid4()}.{file_ext}"
    storage_path = Path(f"./data/uploads/{user.id}")
    storage_path.mkdir(parents=True, exist_ok=True)
    file_location = storage_path / safe_filename

    with open(file_location, 'wb') as f:
        f.write(content)

    sha256 = hashlib.sha256()
    sha256.update(content)
    file_hash = sha256.hexdigest()

    document = Document(
        title=title,
        description=description,
        file_type=file_ext,
        file_path=str(file_location),
        file_size=file_size,
        file_hash=file_hash,
        category_id=category_id,
        created_by=user.id,
        status=DOC_STATUS_PENDING,
        chunk_count=0
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        file_path=str(file_location),
        file_hash=file_hash,
        created_by=user.id
    )
    db.add(version)
    db.commit()

    document.current_version_id = version.id
    db.commit()

    return DocumentResponse.model_validate(document)


@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Get document detail."""
    from app.models.document import Document
    from app.models.permission import DocumentPermission
    from app.exceptions import NotFoundError

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if user.role != "admin" and document.created_by != user.id:
        perm = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user.id
        ).first()
        if not perm:
            raise HTTPException(status_code=403, detail="Access denied")

    return DocumentResponse.model_validate(document)


@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    data: DocumentUpdate,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Update document."""
    from app.models.document import Document

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if user.role != "admin" and document.created_by != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    if data.title is not None:
        document.title = data.title
    if data.description is not None:
        document.description = data.description
    if data.category_id is not None:
        document.category_id = data.category_id

    db.commit()
    db.refresh(document)

    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Delete document (soft delete)."""
    from app.models.document import Document
    from app.constants import DOC_STATUS_FAILED

    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if user.role != "admin" and document.created_by != user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    document.status = DOC_STATUS_FAILED
    db.commit()

    return None