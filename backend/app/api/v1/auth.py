"""Authentication API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.deps import DBSession, CurrentActiveUser
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse
from app.schemas.token import Token
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = DBSession
):
    """Login with username and password."""
    return AuthService.login(db, form_data.username, form_data.password)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    user_data: UserCreate,
    db: Session = DBSession
):
    """Register a new user."""
    user = AuthService.create_user(db, user_data)
    return user


@router.get("/me", response_model=UserResponse)
def get_current_user(
    user: User = CurrentActiveUser
):
    """Get current authenticated user."""
    return user