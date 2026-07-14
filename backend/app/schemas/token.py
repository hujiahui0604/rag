"""Token Schemas"""
from pydantic import BaseModel


class Token(BaseModel):
    """Token 响应"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token 数据"""
    user_id: int
    username: str
    role: str