"""Database Session Management"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator


# Get database URL from environment - evaluated at module load time
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/db/rag.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    from app.db.base import Base
    from app.models import user, document, category, permission, chat, config
    Base.metadata.create_all(bind=engine)