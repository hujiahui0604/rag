"""Permission Service"""
from typing import Optional, List
from sqlalchemy.orm import Session

from app.models.permission import DocumentPermission
from app.models.document import Document


class PermissionService:
    """Service for document permission operations"""

    def __init__(self, db: Session):
        self.db = db

    def grant_permission(
        self,
        document_id: int,
        user_id: int,
        granted_by: int,
        permission_level: str = "read"
    ) -> DocumentPermission:
        """Grant permission to a user for a document."""
        existing = self.db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id
        ).first()

        if existing:
            existing.permission_level = permission_level
            self.db.commit()
            self.db.refresh(existing)
            return existing

        permission = DocumentPermission(
            document_id=document_id,
            user_id=user_id,
            permission_level=permission_level,
            granted_by=granted_by
        )
        self.db.add(permission)
        self.db.commit()
        self.db.refresh(permission)
        return permission

    def revoke_permission(self, permission_id: int) -> bool:
        """Revoke a permission."""
        permission = self.db.query(DocumentPermission).filter(
            DocumentPermission.id == permission_id
        ).first()

        if not permission:
            return False

        self.db.delete(permission)
        self.db.commit()
        return True

    def get_document_permissions(self, document_id: int) -> List[DocumentPermission]:
        """Get all permissions for a document."""
        return self.db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id
        ).all()

    def get_user_permissions(self, user_id: int) -> List[DocumentPermission]:
        """Get all permissions for a user."""
        return self.db.query(DocumentPermission).filter(
            DocumentPermission.user_id == user_id
        ).all()

    def check_permission(
        self,
        document_id: int,
        user_id: int,
        required_level: str = "read"
    ) -> bool:
        """Check if user has required permission for a document."""
        from app.models.document import Document
        from app.models.user import User

        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        if document.created_by == user_id:
            return True

        permission = self.db.query(DocumentPermission).filter(
            DocumentPermission.document_id == document_id,
            DocumentPermission.user_id == user_id
        ).first()

        if not permission:
            return False

        level_hierarchy = {"read": 1, "write": 2, "admin": 3}
        user_level = level_hierarchy.get(permission.permission_level, 0)
        required = level_hierarchy.get(required_level, 0)

        return user_level >= required

    def get_accessible_document_ids(self, user_id: int) -> List[int]:
        """Get all document IDs accessible by a user."""
        from app.models.document import Document
        from app.constants import DOC_STATUS_PENDING

        owned = self.db.query(Document.id).filter(
            Document.created_by == user_id,
            Document.status != DOC_STATUS_PENDING
        )

        permitted = self.db.query(DocumentPermission.document_id).filter(
            DocumentPermission.user_id == user_id
        )

        from sqlalchemy import union
        result = owned.union(permitted).all()
        return [r[0] for r in result]