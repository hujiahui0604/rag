# Phase 1: 基础设施实现计划

> **For agentic workers:** Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 搭建后端基础设施，包括数据库模型、认证系统、配置管理、错误处理和日志系统

**Architecture:** 采用分层架构，使用 SQLAlchemy + Pydantic v2，JWT 认证，structlog 日志

**Tech Stack:** Python 3.12 + FastAPI + SQLAlchemy + Pydantic v2 + python-jose + bcrypt + structlog

---

## 文件结构

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI 应用入口
│   ├── config.py                  # 配置管理
│   ├── constants.py               # 常量定义
│   ├── exceptions.py              # 自定义异常
│   ├── deps.py                    # 依赖注入
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── root.py            # API 根路由
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # JWT/密码安全
│   │   └── logging.py             # 日志配置
│   ├── models/                    # SQLAlchemy 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   ├── category.py
│   │   ├── permission.py
│   │   ├── chat.py
│   │   └── config.py
│   ├── schemas/                   # Pydantic 模型
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── document.py
│   │   └── token.py
│   ├── services/                  # 业务逻辑
│   │   ├── __init__.py
│   │   └── auth_service.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── session.py
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── user_repo.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── requirements.txt
├── scripts/
│   └── init_db.py
└── tests/
    ├── __init__.py
    └── test_phase1/
        ├── test_config.py
        test_security.py
        test_models.py
        └── test_auth.py
```

---

## Task 1: 创建项目基础结构

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/constants.py`

- [ ] **Step 1: 创建 requirements.txt**

```bash
# backend/requirements.txt
fastapi==0.115.0
uvicorn[standard]==0.32.0
pydantic==2.9.0
pydantic-settings==2.5.0
sqlalchemy==2.0.35
alembic==1.13.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
structlog==24.4.0
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
pytest-cov==6.0.0
```

- [ ] **Step 2: 创建配置管理**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用
    APP_NAME: str = "Enterprise RAG"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./data/db/rag.db"
    
    # JWT
    JWT_SECRET_KEY: str = "change-this-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # 文件存储
    DATA_PATH: str = "./data/documents"
    MAX_UPLOAD_SIZE: int = 52428800  # 50MB
    
    # ChromaDB
    CHROMA_PATH: str = "./data/chroma"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"
    
    # RAG 配置
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    RETRIEVAL_TOP_K: int = 4
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2000
    
    # 日志
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
```

- [ ] **Step 3: 创建常量定义**

```python
# backend/app/constants.py
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"
    DELETED = "deleted"


class PermissionLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


# 允许的文件类型
ALLOWED_EXTENSIONS = {
    "pdf", "docx", "doc", "xlsx", "xls", "pptx", "ppt",
    "txt", "md", "markdown"
}

# 公开接口
PUBLIC_PATHS = [
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/docs",
    "/openapi.json",
    "/redoc",
]

# 管理员专用接口
ADMIN_ONLY_PATHS = [
    "/api/v1/users",
    "/api/v1/admin",
]
```

- [ ] **Step 4: 提交**

```bash
git add backend/requirements.txt backend/app/config.py backend/app/constants.py
git commit -m "feat(infrastructure): add project structure and configuration"
```

---

## Task 2: 创建数据库基础

**Files:**
- Create: `backend/app/db/base.py`
- Create: `backend/app/db/session.py`
- Create: `backend/app/db/__init__.py`

- [ ] **Step 1: 创建 SQLAlchemy Base**

```python
# backend/app/db/base.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import MetaData


class Base(DeclarativeBase):
    """SQLAlchemy 基础类"""
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

- [ ] **Step 2: 创建会话管理**

```python
# backend/app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG,
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
```

- [ ] **Step 3: 创建 __init__.py**

```python
# backend/app/db/__init__.py
from app.db.base import Base
from app.db.session import get_db, init_db, engine, SessionLocal

__all__ = ["Base", "get_db", "init_db", "engine", "SessionLocal"]
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/db/
git commit -m "feat(infrastructure): add database session management"
```

---

## Task 3: 创建用户模型

**Files:**
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/__init__.py`

- [ ] **Step 1: 创建用户 SQLAlchemy 模型**

```python
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from app.constants import UserRole


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default=UserRole.USER.value, nullable=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    documents = relationship("Document", back_populates="creator", foreign_keys="Document.created_by")
    chat_sessions = relationship("ChatSession", back_populates="user")
    permissions_granted = relationship("DocumentPermission", back_populates="granter", foreign_keys="DocumentPermission.granted_by")
    
    def __repr__(self):
        return f"<User {self.username}>"
```

- [ ] **Step 2: 创建 models __init__.py**

```python
# backend/app/models/__init__.py
from app.models.user import User

__all__ = ["User"]
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/models/
git commit -m "feat(infrastructure): add User SQLAlchemy model"
```

---

## Task 4: 创建认证安全模块

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/__init__.py`

- [ ] **Step 1: 创建安全模块**

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import settings
from app.db import get_db
from app.models.user import User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """获取密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """解码令牌"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """获取当前活跃用户"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员权限"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin permission required")
    return current_user
```

- [ ] **Step 2: 创建 core __init__.py**

```python
# backend/app/core/__init__.py
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    get_current_active_user,
    require_admin,
)

__all__ = [
    "verify_password",
    "get_password_hash",
    "create_access_token",
    "get_current_user",
    "get_current_active_user",
    "require_admin",
]
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/core/
git commit -m "feat(infrastructure): add authentication and security module"
```

---

## Task 5: 创建日志系统

**Files:**
- Create: `backend/app/core/logging.py`

- [ ] **Step 1: 创建日志配置**

```python
# backend/app/core/logging.py
import structlog
import logging
import sys
from app.config import settings


def configure_logging():
    """配置结构化日志"""
    
    # 配置标准 logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # 配置 structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer() if settings.DEBUG else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__):
    """获取日志器"""
    return structlog.get_logger(name)
```

- [ ] **Step 2: 更新 core __init__.py**

```python
# backend/app/core/__init__.py 添加
from app.core.logging import configure_logging, get_logger
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/core/logging.py
git commit -m "feat(infrastructure): add structured logging"
```

---

## Task 6: 创建异常处理

**Files:**
- Create: `backend/app/exceptions.py`

- [ ] **Step 1: 创建自定义异常**

```python
# backend/app/exceptions.py
from fastapi import HTTPException, status


class RAGException(Exception):
    """基础异常类"""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundError(RAGException):
    """资源不存在"""
    def __init__(self, resource: str, resource_id: int):
        super().__init__(
            message=f"{resource} with id {resource_id} not found",
            code="NOT_FOUND"
        )


class UnauthorizedError(RAGException):
    """未授权"""
    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message=message, code="UNAUTHORIZED")


class ForbiddenError(RAGException):
    """禁止访问"""
    def __init__(self, message: str = "Forbidden"):
        super().__init__(message=message, code="FORBIDDEN")


class ValidationError(RAGException):
    """验证错误"""
    def __init__(self, message: str):
        super().__init__(message=message, code="VALIDATION_ERROR")


class FileTooLargeError(RAGException):
    """文件过大"""
    def __init__(self):
        super().__init__(message="File too large", code="FILE_TOO_LARGE")


class UnsupportedFileTypeError(RAGException):
    """不支持的文件类型"""
    def __init__(self, file_type: str):
        super().__init__(
            message=f"Unsupported file type: {file_type}",
            code="UNSUPPORTED_FILE_TYPE"
        )


def rag_exception_handler(request, exc: RAGException):
    """RAG 异常处理器"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"error": exc.message, "code": exc.code}
    )
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/exceptions.py
git commit -m "feat(infrastructure): add custom exceptions"
```

---

## Task 7: 创建 Pydantic Schema

**Files:**
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/token.py`
- Create: `backend/app/schemas/__init__.py`

- [ ] **Step 1: 创建 Token Schema**

```python
# backend/app/schemas/token.py
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
```

- [ ] **Step 2: 创建 User Schema**

```python
# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


# User schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """数据库中的用户"""
    id: int
    role: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserInDB):
    """用户响应"""
    pass


class UserLogin(BaseModel):
    """登录请求"""
    username: str
    password: str
```

- [ ] **Step 3: 创建 schemas __init__.py**

```python
# backend/app/schemas/__init__.py
from app.schemas.token import Token, TokenData
from app.schemas.user import UserBase, UserCreate, UserUpdate, UserInDB, UserResponse, UserLogin

__all__ = [
    "Token",
    "TokenData",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserInDB",
    "UserResponse",
    "UserLogin",
]
```

- [ ] **Step 4: 提交**

```bash
git add backend/app/schemas/
git commit -m "feat(infrastructure): add Pydantic schemas"
```

---

## Task 8: 创建依赖注入

**Files:**
- Create: `backend/app/deps.py`

- [ ] **Step 1: 创建依赖注入模块**

```python
# backend/app/deps.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.core.security import get_current_user, require_admin, User


# 类型注解
CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentActiveUser = Annotated[User, Depends(get_current_active_user)]
AdminUser = Annotated[User, Depends(require_admin)]
DBSession = Annotated[Session, Depends(get_db)]
```

- [ ] **Step 2: 提交**

```bash
git add backend/app/deps.py
git commit -m "feat(infrastructure): add dependency injection"
```

---

## Task 9: 创建认证服务

**Files:**
- Create: `backend/app/services/auth_service.py`
- Create: `backend/app/services/__init__.py`

- [ ] **Step 1: 创建认证服务**

```python
# backend/app/services/auth_service.py
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.logging import get_logger
from app.config import settings
from app.schemas.token import Token


logger = get_logger(__name__)


class AuthService:
    """认证服务"""
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """验证用户"""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user
    
    @staticmethod
    def create_token(user: User) -> Token:
        """创建访问令牌"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "role": user.role},
            expires_delta=access_token_expires
        )
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    @staticmethod
    def update_last_login(db: Session, user: User) -> None:
        """更新最后登录时间"""
        user.last_login = datetime.utcnow()
        db.commit()
    
    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str, role: str = "user") -> User:
        """创建用户"""
        user = User(
            username=username,
            email=email,
            password_hash=get_password_hash(password),
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info("user_created", user_id=user.id, username=username)
        return user
```

- [ ] **Step 2: 创建 services __init__.py**

```python
# backend/app/services/__init__.py
from app.services.auth_service import AuthService

__all__ = ["AuthService"]
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/services/
git commit -m "feat(infrastructure): add authentication service"
```

---

## Task 10: 创建认证 API

**Files:**
- Create: `backend/app/api/v1/auth.py`
- Create: `backend/app/api/v1/__init__.py`
- Create: `backend/app/api/__init__.py`
- Create: `backend/app/api/v1/root.py`

- [ ] **Step 1: 创建认证路由**

```python
# backend/app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.user import UserLogin, UserResponse, UserCreate
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.core.logging import get_logger
from app.deps import CurrentActiveUser, DBSession


router = APIRouter(prefix="/auth", tags=["auth"])
logger = get_logger(__name__)


@router.post("/login", response_model=Token)
def login(
    user_data: UserLogin,
    db: DBSession
):
    """用户登录"""
    user = AuthService.authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    AuthService.update_last_login(db, user)
    logger.info("user_logged_in", user_id=user.id, username=user.username)
    
    return AuthService.create_token(user)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: CurrentActiveUser):
    """获取当前用户信息"""
    return current_user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: DBSession
):
    """用户注册（开发环境可用，生产环境可关闭）"""
    # 检查用户名是否存在
    existing_user = db.query(User).filter(
        (User.username == user_data.username) | (User.email == user_data.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    user = AuthService.create_user(
        db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password
    )
    
    return user
```

- [ ] **Step 2: 创建 API v1 __init__.py**

```python
# backend/app/api/v1/__init__.py
from fastapi import APIRouter
from app.api.v1 import auth

api_router = APIRouter()
api_router.include_router(auth.router)

__all__ = ["api_router"]
```

- [ ] **Step 3: 创建 API __init__.py**

```python
# backend/app/api/__init__.py
# API package
```

- [ ] **Step 4: 创建根路由**

```python
# backend/app/api/v1/root.py
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
def root():
    """API 根路径"""
    return {"message": "Enterprise RAG API", "version": "1.0.0"}
```

- [ ] **Step 5: 提交**

```bash
git add backend/app/api/
git commit -m "feat(infrastructure): add authentication API routes"
```

---

## Task 11: 创建 FastAPI 主应用

**Files:**
- Create: `backend/app/main.py`

- [ ] **Step 1: 创建主应用**

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core.logging import configure_logging, get_logger
from app.api.v1 import api_router


# 配置日志
configure_logging()
logger = get_logger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="企业内部知识库 AI 问答系统",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup_event():
    """启动事件"""
    logger.info("application_starting", app_name=settings.APP_NAME, version=settings.APP_VERSION)
    from app.db import init_db
    init_db()
    logger.info("database_initialized")


@app.on_event("shutdown")
async def shutdown_event():
    """关闭事件"""
    logger.info("application_shutting_down")


@app.get("/health")
def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

- [ ] **Step 2: 更新 app __init__.py**

```python
# backend/app/__init__.py
from app.main import app

__version__ = "1.0.0"
```

- [ ] **Step 3: 提交**

```bash
git add backend/app/main.py backend/app/__init__.py
git commit -m "feat(infrastructure): create FastAPI main application"
```

---

## Task 12: 创建数据库初始化脚本

**Files:**
- Create: `backend/scripts/init_db.py`

- [ ] **Step 1: 创建初始化脚本**

```python
# backend/scripts/init_db.py
"""数据库初始化脚本"""
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import init_db, SessionLocal
from app.models.user import User
from app.services.auth_service import AuthService
from app.core.logging import configure_logging, get_logger


configure_logging()
logger = get_logger(__name__)


def init_default_admin():
    """初始化默认管理员"""
    db = SessionLocal()
    try:
        # 检查是否已存在管理员
        existing_admin = db.query(User).filter(User.role == "admin").first()
        
        if existing_admin:
            logger.info("admin_already_exists", user_id=existing_admin.id)
            return
        
        # 创建默认管理员
        admin = AuthService.create_user(
            db,
            username="admin",
            email="admin@company.com",
            password="admin123",
            role="admin"
        )
        
        logger.info("default_admin_created", user_id=admin.id, username=admin.username)
        print("默认管理员账号已创建: admin / admin123")
        
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("initializing_database")
    
    # 创建数据库表
    init_db()
    logger.info("database_tables_created")
    
    # 创建默认管理员
    init_default_admin()
    
    logger.info("database_initialization_complete")
    print("数据库初始化完成！")
```

- [ ] **Step 2: 提交**

```bash
git add backend/scripts/init_db.py
git commit -m "feat(infrastructure): add database initialization script"
```

---

## Task 13: 创建测试文件

**Files:**
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_phase1/test_config.py`
- Create: `backend/tests/test_phase1/test_security.py`
- Create: `backend/tests/test_phase1/test_auth.py`

- [ ] **Step 1: 创建测试配置**

```python
# backend/tests/__init__.py
# Test package
```

- [ ] **Step 2: 创建 pytest 配置**

```python
# backend/tests/conftest.py
import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "backend"))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.db.base import Base
from app.db.session import get_db
from app.main import app


# 测试数据库
TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """创建测试客户端"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
```

- [ ] **Step 3: 创建配置测试**

```python
# backend/tests/test_phase1/test_config.py
import pytest
from app.config import settings


def test_settings_loaded():
    """测试配置加载"""
    assert settings.APP_NAME == "Enterprise RAG"
    assert settings.APP_VERSION == "1.0.0"


def test_jwt_config():
    """测试 JWT 配置"""
    assert settings.JWT_SECRET_KEY is not None
    assert settings.JWT_ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0


def test_rag_config():
    """测试 RAG 配置"""
    assert settings.CHUNK_SIZE > 0
    assert settings.CHUNK_OVERLAP >= 0
    assert settings.RETRIEVAL_TOP_K > 0
```

- [ ] **Step 4: 创建安全模块测试**

```python
# backend/tests/test_phase1/test_security.py
import pytest
from app.core.security import verify_password, get_password_hash, create_access_token, decode_token


def test_password_hash():
    """测试密码哈希"""
    password = "test_password123"
    hashed = get_password_hash(password)
    
    assert hashed != password
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)


def test_create_and_decode_token():
    """测试令牌创建和解码"""
    data = {"sub": "1", "username": "test", "role": "user"}
    token = create_access_token(data)
    
    assert token is not None
    assert len(token) > 0
    
    decoded = decode_token(token)
    assert decoded["sub"] == "1"
    assert decoded["username"] == "test"
    assert decoded["role"] == "user"
```

- [ ] **Step 5: 创建认证测试**

```python
# backend/tests/test_phase1/test_auth.py
import pytest
from app.services.auth_service import AuthService
from app.models.user import User


def test_create_user(db_session):
    """测试创建用户"""
    user = AuthService.create_user(
        db_session,
        username="testuser",
        email="test@example.com",
        password="password123",
        role="user"
    )
    
    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.role == "user"
    assert user.is_active is True


def test_authenticate_user(db_session):
    """测试用户认证"""
    # 创建用户
    AuthService.create_user(
        db_session,
        username="authuser",
        email="auth@example.com",
        password="password123"
    )
    
    # 验证成功
    user = AuthService.authenticate_user(db_session, "authuser", "password123")
    assert user is not None
    assert user.username == "authuser"
    
    # 验证失败 - 错误密码
    user = AuthService.authenticate_user(db_session, "authuser", "wrongpassword")
    assert user is None
    
    # 验证失败 - 用户不存在
    user = AuthService.authenticate_user(db_session, "nonexistent", "password123")
    assert user is None


def test_create_token(db_session):
    """测试创建令牌"""
    user = AuthService.create_user(
        db_session,
        username="tokenuser",
        email="token@example.com",
        password="password123"
    )
    
    token = AuthService.create_token(user)
    
    assert token.access_token is not None
    assert token.token_type == "bearer"
    assert token.expires_in > 0
```

- [ ] **Step 6: 创建目录和提交**

```bash
mkdir -p backend/tests/test_phase1
git add backend/tests/
git commit -m "test(infrastructure): add Phase 1 tests"
```

---

## Task 14: Phase 1 完成 - 创建 Git Worktree

- [ ] **Step 1: 创建开发分支**

```bash
# 在实际执行时使用
git checkout -b feat/infrastructure
```

- [ ] **Step 2: 提交**

```bash
git add .
git commit -m "feat(infrastructure): complete Phase 1 - infrastructure setup"
```

---

## Phase 1 完成总结

已完成的基础设施包括：
- ✅ 项目配置管理
- ✅ 数据库基础（SQLAlchemy）
- ✅ 用户模型
- ✅ JWT 认证系统
- ✅ 结构化日志
- ✅ 自定义异常
- ✅ Pydantic Schemas
- ✅ 依赖注入
- ✅ 认证服务
- ✅ 认证 API 路由
- ✅ FastAPI 主应用
- ✅ 数据库初始化脚本
- ✅ 单元测试

**下一步：** Phase 2 - 文档管理模块