# Phase 2: 数据模型实现计划

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** 创建所有数据库模型、Schemas、基础服务

**Architecture:** SQLAlchemy ORM + Pydantic v2，分层架构

**Tech Stack:** Python 3.12 + SQLAlchemy 2.0 + Pydantic v2

---

## 文件结构

```
backend/app/
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── document.py
│   ├── category.py
│   ├── permission.py
│   ├── chat.py
│   └── config.py
├── schemas/
│   ├── __init__.py
│   ├── user.py
│   ├── document.py
│   ├── category.py
│   ├── chat.py
│   └── token.py
├── services/
│   ├── __init__.py
│   └── auth_service.py
├── db/
│   ├── __init__.py
│   ├── base.py
│   └── session.py
└── core/
    ├── __init__.py
    ├── security.py
    └── logging.py
```

---

## Task 1: 数据库基础

**Files:**
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/__init__.py`

```python
# backend/app/db/base.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData

class Base(DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s"
        }
    )
```

```python
# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- [ ] **提交**
```bash
git add backend/app/db/
git commit -m "feat(db): add database session management"
```

---

## Task 2: 用户模型

**Files:**
- Create: `backend/app/models/user.py`

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user", nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    documents = relationship("Document", back_populates="creator", foreign_keys="Document.created_by")
    chat_sessions = relationship("ChatSession", back_populates="user")
```

- [ ] **提交**
```bash
git add backend/app/models/user.py
git commit -m "feat(models): add User model"
```

---

## Task 3: 文档模型

**Files:**
- Create: `backend/app/models/document.py`

```python
# backend/app/models/document.py
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    file_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=True)
    current_version_id = Column(Integer, ForeignKey("document_versions.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    status = Column(String(20), default="processing")
    error_message = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    versions = relationship("DocumentVersion", back_populates="document")
    category = relationship("Category", back_populates="documents")
    creator = relationship("User", back_populates="documents", foreign_keys=[created_by])
    permissions = relationship("DocumentPermission", back_populates="document")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False)
    chunk_count = Column(Integer, default=0)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    document = relationship("Document", back_populates="versions")
```

- [ ] **提交**
```bash
git add backend/app/models/document.py
git commit -m "feat(models): add Document and DocumentVersion models"
```

---

## Task 4: 分类和权限模型

**Files:**
- Create: `backend/app/models/category.py`
- Create: `backend/app/models/permission.py`

```python
# backend/app/models/category.py
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    documents = relationship("Document", back_populates="category")
    children = relationship("Category", backref="parent", remote_side=[id])
```

```python
# backend/app/models/permission.py
class DocumentPermission(Base):
    __tablename__ = "document_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    permission_level = Column(String(20), nullable=False, default="read")
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    document = relationship("Document", back_populates="permissions")
    user = relationship("User", foreign_keys=[user_id])
    granter = relationship("User", foreign_keys=[granted_by])
```

- [ ] **提交**
```bash
git add backend/app/models/category.py backend/app/models/permission.py
git commit -m "feat(models): add Category and Permission models"
```

---

## Task 5: 聊天模型

**Files:**
- Create: `backend/app/models/chat.py`

```python
# backend/app/models/chat.py
class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String(10), nullable=False)  # user, assistant
    content = Column(Text, nullable=False)
    sources = Column(JSON, nullable=True)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    
    session = relationship("ChatSession", back_populates="messages")
    feedback = relationship("Feedback", back_populates="message", uselist=False)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(Integer, ForeignKey("chat_messages.id"), nullable=False)
    is_helpful = Column(Boolean, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    message = relationship("ChatMessage", back_populates="feedback")
```

- [ ] **提交**
```bash
git add backend/app/models/chat.py
git commit -m "feat(models): add Chat models"
```

---

## Task 6: 配置模型

**Files:**
- Create: `backend/app/models/config.py`

```python
# backend/app/models/config.py
class SystemConfig(Base):
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False, index=True)
    value = Column(Text, nullable=False)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

- [ ] **提交**
```bash
git add backend/app/models/config.py
git commit -m "feat(models): add SystemConfig model"
```

---

## Task 7: Pydantic Schemas

**Files:**
- Create: `backend/app/schemas/token.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/document.py`
- Create: `backend/app/schemas/category.py`
- Create: `backend/app/schemas/chat.py`

- [ ] **提交**
```bash
git add backend/app/schemas/
git commit -m "feat(schemas): add Pydantic schemas"
```

---

## Task 8: 安全模块

**Files:**
- Create: `backend/app/core/security.py`

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta=None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=1440))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
```

- [ ] **提交**
```bash
git add backend/app/core/security.py
git commit -m "feat(security): add authentication utilities"
```

---

## Task 9: 认证服务

**Files:**
- Create: `backend/app/services/auth_service.py`

- [ ] **提交**
```bash
git add backend/app/services/auth_service.py
git commit -m "feat(services): add authentication service"
```

---

## Task 10: 常量和配置

**Files:**
- Create: `backend/app/config.py`
- Create: `backend/app/constants.py`

- [ ] **提交**
```bash
git add backend/app/config.py backend/app/constants.py
git commit -m "feat(config): add configuration and constants"
```

---

## 完成总结

✅ 数据模型完整实现：
- ✅ 数据库基础（session, base）
- ✅ 用户模型
- ✅ 文档模型 + 版本模型
- ✅ 分类模型
- ✅ 权限模型
- ✅ 聊天模型（会话、消息、反馈）
- ✅ 配置模型
- ✅ Pydantic Schemas
- ✅ 安全模块
- ✅ 认证服务
- ✅ 配置和常量