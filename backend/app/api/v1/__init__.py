"""API v1 router"""
from fastapi import APIRouter

from app.api.v1 import auth, documents, categories, chat, permissions, root

api_router = APIRouter()
api_router.include_router(root.router, tags=["root"])
api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(categories.router)
api_router.include_router(chat.router)
api_router.include_router(permissions.router)

__all__ = ["api_router"]