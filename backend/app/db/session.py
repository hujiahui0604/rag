"""Database Session Management"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator


# 默认使用 SQLite
DATABASE_URL = "sqlite:///./data/db/rag.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """初始化数据库表"""
    from app.db.base import Base
    from app.models import user, document, category, permission, chat, config
    Base.metadata.create_all(bind=engine)