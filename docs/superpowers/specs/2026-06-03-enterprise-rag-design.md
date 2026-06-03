# 企业内部知识库 AI 问答系统 - 设计文档

## 1. 项目概述

### 1.1 业务背景

解决企业内部信息分散、查找困难的问题，让员工通过自然语言快速获取知识库中的准确信息，同时保证数据安全和权限隔离。

### 1.2 技术栈

- 前端：React 18.3 + TypeScript 5.5 + Tailwind CSS v3.4 + shadcn/ui
- 后端：Python 3.12 + FastAPI 0.115 + Pydantic v2.9
- 向量数据库：ChromaDB（本地）+ SQLite
- 文档解析：LangChain + PyMuPDF + python-docx
- 大模型：Ollama + Llama 3（本地完全离线）
- 工具链：Git + Docker Compose + pytest

### 1.3 部署目标

企业内网 Docker 容器化部署，支持完全离线运行。

---

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           企业内部知识库 AI 问答系统                           │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         React 前端 (localhost:3000)                   │   │
│  │  pages: 知识库管理 | 问答聊天 | 历史记录 | 用户管理 | 系统设置          │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                       │ HTTP/WebSocket                       │
│  ┌───────────────────────────────────▼───────────────────────────────────┐   │
│  │                     FastAPI 后端 (localhost:8000)                     │   │
│  │  API Layer → Service Layer → Data Access Layer                       │   │
│  └───────────────────────────────────┬───────────────────────────────────┘   │
│                                      │                                        │
│    ┌──────────┐  ┌──────────┐  ┌─────▼─────┐  ┌──────────┐                 │
│    │  SQLite  │  │  Files   │  │ ChromaDB  │  │ Ollama   │                 │
│    │  (本地)  │  │(文档存储)│  │  (向量)   │  │ (本地LLM)│                 │
│    └──────────┘  └──────────┘  └───────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 模块划分

#### 前端模块 (frontend/)
- `pages/` - 路由页面：知识库管理、问答聊天、历史记录、用户管理、系统设置
- `components/` - UI 组件 (shadcn/ui)
- `hooks/` - 自定义 Hooks (useAuth, useChat, useDocument)
- `services/` - API 调用封装

#### 后端模块 (backend/app/)
- `api/v1/` - API 路由 (auth, documents, chat, users, admin)
- `core/` - 核心配置 (config, security, exceptions, logging)
- `models/` - Pydantic 模型
- `services/` - 业务逻辑
- `db/` - 数据库 (SQLAlchemy + repositories)

#### RAG 核心模块 (backend/rag/)
- `parser/` - 文档解析 (PDF, Word, Excel, PPT, Markdown, Text)
- `chunker/` - 文本分块
- `vector/` - ChromaDB 接口
- `llm/` - Ollama 适配器
- `pipeline/` - RAG 流程

---

## 3. 数据模型

### 3.1 数据库表

| 表名 | 说明 |
|------|------|
| users | 用户表 |
| documents | 文档表 |
| document_versions | 文档版本表 |
| categories | 分类表 |
| document_permissions | 文档权限表 |
| chat_sessions | 聊天会话表 |
| chat_messages | 聊天消息表 |
| feedback | 反馈表 |
| system_config | 系统配置表 |

### 3.2 权限模型

- 两级角色：admin, user
- 文档级权限控制
- JWT 认证

---

## 4. API 接口

### 4.1 主要接口

| 模块 | 接口 | 说明 |
|------|------|------|
| auth | POST /login, GET /me | 登录/获取用户信息 |
| documents | GET/POST /, GET /{id}, DELETE /{id} | 文档 CRUD |
| documents | GET /{id}/versions, POST /{id}/restore | 版本管理 |
| chat | GET /sessions, POST /chat | 问答 (SSE 流式) |
| users | GET/POST /, PUT /{id}/role | 用户管理 |
| admin | GET /stats, GET/PUT /config | 系统管理 |

### 4.2 错误响应

统一错误格式：
```json
{
  "error": "错误描述",
  "code": "ERROR_CODE"
}
```

---

## 5. RAG 核心流程

### 5.1 文档处理流程

1. 文档上传 → 解析 → 分块 → 向量化 → 存储到 ChromaDB

### 5.2 问答流程

1. 用户提问 → 查询改写 → 混合检索 (语义 + BM25) → RRF 融合 → 重排
2. 构建 Prompt → Ollama 生成 → 引用溯源 → 返回答案

### 5.3 配置参数

- chunk_size: 1000
- chunk_overlap: 200
- retrieval_top_k: 4
- llm_model: llama3
- temperature: 0.7

---

## 6. 权限与安全

### 6.1 认证

- JWT Bearer Token
- 密码 bcrypt 哈希
- Token 有效期 24 小时

### 6.2 权限检查

- 角色级权限矩阵
- 文档级权限
- API 接口权限装饰器

### 6.3 安全措施

- 文件类型白名单
- 文件大小限制 (50MB)
- 请求限流
- 审计日志

---

## 7. 部署架构

### 7.1 Docker Compose

```yaml
services:
  nginx:     # 反向代理
  frontend:  # React 前端
  backend:   # FastAPI 后端
  ollama:    # 本地大模型
```

### 7.2 数据目录

```
data/
├── db/rag.db          # SQLite
├── chroma/            # ChromaDB
└── documents/         # 文档存储
```

### 7.3 初始化

- 创建默认管理员账号 (admin/admin123)
- 初始化系统配置
- 下载 Ollama 模型

---

## 8. 验收标准

- [x] 系统架构设计完成
- [x] 数据模型设计完成
- [x] API 接口设计完成
- [x] RAG 核心流程设计完成
- [x] 权限与安全设计完成
- [x] 部署架构设计完成