"""Root API Router"""
from fastapi import APIRouter


router = APIRouter()


@router.get("/health")
def api_health():
    """API 健康检查"""
    return {"status": "healthy"}