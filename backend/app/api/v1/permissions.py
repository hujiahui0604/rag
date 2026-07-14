"""Permission API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from sqlalchemy.orm import Session

from app.deps import DBSession, CurrentActiveUser
from app.models.user import User
from app.models.permission import DocumentPermission
from app.models.document import Document

router = APIRouter(prefix="/permissions", tags=["permissions"])


class PermissionGrantRequest:
    """Permission grant request schema"""
    def __init__(self, document_id: int, user_id: Optional[int] = None, permission_level: str = "read"):
        self.document_id = document_id
        self.user_id = user_id
        self.permission_level = permission_level


@router.post("", status_code=201)
def grant_permission(
    document_id: int,
    target_user_id: Optional[int] = None,
    permission_level: str = Query("read", pattern="^(read|write|admin)$"),
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Grant permission to a document."""
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    if user.role != "admin" and document.created_by != user.id:
        raise HTTPException(status_code=403, detail="Only document owner or admin can grant permissions")

    if target_user_id:
        existing = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == target_user_id
        ).first()
        if existing:
            existing.permission_level = permission_level
            db.commit()
            return {"message": "Permission updated", "permission": existing.id}

        permission = DocumentPermission(
            document_id=document_id,
            user_id=target_user_id,
            permission_level=permission_level,
            granted_by=user.id
        )
        db.add(permission)
        db.commit()
        return {"message": "Permission granted", "permission": permission.id}

    return {"message": "Public access permission not implemented"}


@router.delete("/{permission_id}", status_code=204)
def revoke_permission(
    permission_id: int,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """Revoke a permission."""
    permission = db.query(DocumentPermission).filter(DocumentPermission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    document = db.query(Document).filter(Document.id == permission.document_id).first()
    if user.role != "admin" and document.created_by != user.id:
        raise HTTPException(status_code=403, detail="Only document owner or admin can revoke permissions")

    db.delete(permission)
    db.commit()
    return None


@router.get("")
def list_permissions(
    document_id: Optional[int] = None,
    user: User = CurrentActiveUser,
    db: Session = DBSession
):
    """List permissions for documents."""
    if document_id:
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        if user.role != "admin" and document.created_by != user.id:
            raise HTTPException(status_code=403, detail="Access denied")

        permissions = db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id
        ).all()
    else:
        if user.role != "admin":
            documents = db.query(Document).filter(Document.created_by == user.id).all()
            doc_ids = [d.id for d in documents]
            permissions = db.query(DocumentPermission).filter(
                DocumentPermission.document_id.in_(doc_ids)
            ).all()
        else:
            permissions = db.query(DocumentPermission).all()

    return [
        {
            "id": p.id,
            "document_id": p.document_id,
            "user_id": p.user_id,
            "permission_level": p.permission_level,
            "granted_by": p.granted_by,
            "created_at": p.created_at.isoformat() if p.created_at else None
        }
        for p in permissions
    ]