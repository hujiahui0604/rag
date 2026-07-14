# 企业内部知识库 AI 问答系统 - 技术设计规格书

> **版本**: 1.0.0
> **日期**: 2026-06-04
> **状态**: DRAFT - 待确认

---

# 第一章：项目概述与非功能需求

## 1.1 项目背景

本系统是为企业内部构建的智能知识库问答平台，旨在帮助企业员工快速检索和获取内部文档知识。系统基于检索增强生成（RAG）架构，结合大语言模型（LLM）提供自然语言问答能力。

## 1.2 系统定位

- **用户群体**：企业内部员工、技术文档管理员、系统管理员
- **使用场景**：知识查询、技术文档检索、FAQ 问答
- **部署环境**：私有化部署（Docker Compose / Kubernetes）
- **网络要求**：完全离线运行，不依赖外部互联网服务

## 1.3 非功能需求

### 1.3.1 性能指标

| 指标 | 要求 | 说明 |
|------|------|------|
| 问答响应时间 | ≤ 2s（P95） | 从用户提问到返回答案的端到端延迟 |
| 文档上传处理 | ≤ 30s/MB | 文档解析+向量化处理时间 |
| 系统并发用户 | ≥ 100 | 支持同时在线用户数 |
| 向量检索延迟 | ≤ 100ms | ChromaDB 检索耗时 |

### 1.3.2 可用性指标

| 指标 | 要求 |
|------|------|
| 系统可用性 | ≥ 99.9% |
| 数据持久化 | SQLite + ChromaDB 本地存储 |
| 备份策略 | 每日增量备份，每周全量备份 |

### 1.3.3 安全性指标

| 指标 | 要求 |
|------|------|
| 认证方式 | JWT Token |
| 密码加密 | bcrypt |
| 数据隔离 | 用户级文档权限控制 |
| 敏感信息 | 全部通过环境变量注入 |

### 1.3.4 扩展性指标

| 指标 | 要求 |
|------|------|
| 水平扩展 | 支持 Docker Compose 多实例部署 |
| 向量库扩展 | 支持从 ChromaDB 迁移至 Qdrant 集群 |
| LLM 扩展 | 支持 Ollama / Claude / OpenAI 多后端 |

---

# 第二章：系统架构图

## 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              客户端层 (Client)                                │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   Web UI    │  │  Mobile UI  │  │  API Client │  │  Admin UI   │        │
│  │  (React)    │  │   (PWA)     │  │   (SDK)     │  │  (React)    │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
└─────────┼────────────────┼────────────────┼────────────────┼───────────────┘
          │                │                │                │
          └────────────────┴────────────────┴────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              API 网关层 (Gateway)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         Nginx Reverse Proxy                           │   │
│  │   • 负载均衡  • SSL/TLS 终止  • 静态资源服务  • API 路由              │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            后端服务层 (Backend)                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      FastAPI Application                             │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ ┌────────────┐ │    │
│  │  │   Auth API   │ │  Document    │ │   Category   │ │   Chat     │ │    │
│  │  │   /auth      │ │    /docs     │ │   /cats      │ │   /chat    │ │    │
│  │  └──────────────┘ └──────────────┘ └──────────────┘ └────────────┘ │    │
│  │                                                                    │    │
│  │  ┌──────────────────────────────────────────────────────────────┐  │    │
│  │  │                     Business Services                         │  │    │
│  │  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │  │    │
│  │  │  │AuthService  │ │DocService   │ │CatService   │ │ChatSvc  │ │  │    │
│  │  │  │(JWT/Bcrypt) │ │(CRUD+Upload)│ │(Tree)       │ │(RAG)    │ │  │    │
│  │  │  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │  │    │
│  │  └──────────────────────────────────────────────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
          │                                    │                    │
          ▼                                    ▼                    ▼
┌─────────────────────┐         ┌─────────────────────┐    ┌─────────────────────┐
│    数据存储层        │         │    向量存储层        │    │    LLM 推理层       │
├─────────────────────┤         ├─────────────────────┤    ├─────────────────────┤
│  SQLite (元数据)     │         │   ChromaDB          │    │   Ollama            │
│  • users            │         │   (本地开发)         │    │   (Llama 3.1 70B)   │
│  • documents        │         │                     │    │                     │
│  • categories       │         │   Qdrant            │    │   支持 Claude       │
│  • chat_sessions    │         │   (生产集群)         │    │   备选)             │
│  • permissions      │         │                     │    │                     │
└─────────────────────┘         └─────────────────────┘    └─────────────────────┘
```

## 2.2 RAG 流水线架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG (Retrieval-Augmented Generation)                │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  文档上传    │───▶│  文档解析    │───▶│  文本分块    │───▶│  向量化     │
  │  Upload     │    │  Parse      │    │  Chunk      │    │  Embed      │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                                                                    │
                                                                    ▼
  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
  │  用户提问    │───▶│  向量检索    │───▶│  结果重排    │───▶│  LLM 生成   │
  │  Query      │    │  Search     │    │  Rerank     │    │  Generate   │
  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                            │                                    │
                            ▼                                    ▼
                     ┌─────────────┐                      ┌─────────────┐
                     │ ChromaDB    │                      │  答案输出   │
                     │ Vector Store│                      │  + 引用来源 │
                     └─────────────┘                      └─────────────┘
```

## 2.3 技术栈总结

| 层次 | 技术选型 |
|------|----------|
| 前端 | React 18.3 + TypeScript 5.5 + Tailwind CSS v3.4 + shadcn/ui |
| 后端 | Python 3.12 + FastAPI 0.115 + Pydantic v2.9 + SQLAlchemy 2.0 |
| 向量库 | ChromaDB（本地开发）+ Qdrant 1.10（生产） |
| LLM | Ollama + Llama 3.1 70B（离线）/ Claude 3.7 Sonnet |
| 文档解析 | LangChain 0.3 + Unstructured.io 0.16 + PyMuPDF |
| 部署 | Docker Compose + Nginx |
| 监控 | Prometheus + Grafana |

---

# 第三章：数据模型 ER 图

## 3.1 ER 图概览

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Users (用户表)                                   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐                                                            │
│  │    id (PK)  │◄────────────────────┐                                      │
│  │  username   │                     │                                      │
│  │    email    │                     │ created_by                           │
│  │password_hash│              ┌──────┴──────┐                               │
│  │    role     │              │             │                               │
│  │  is_active  │              ▼             ▼                               │
│  │  last_login │      ┌───────────┐ ┌───────────┐                           │
│  │ created_at  │      │Documents  │ │Categories │                           │
│  │ updated_at  │      └─────┬─────┘ └─────┬─────┘                           │
│  └─────────────┘            │             │                                 │
│        │                    │             │                                 │
│        │                    │             │ parent_id                       │
│        │                    │             │ (自引用)                         │
│        │                    │             │                                 │
│        └────────────────────┼─────────────┤                                 │
│                             │             │                                 │
│                             ▼             ▼                                 │
│                    ┌─────────────────────────────┐                          │
│                    │     DocumentVersions        │                          │
│                    ├─────────────────────────────┤                          │
│                    │  id (PK)                     │                          │
│                    │  document_id (FK) ───────────┼────┐                    │
│                    │  version_number              │    │                    │
│                    │  file_path                   │    │                    │
│                    │  file_hash                   │    │                    │
│                    │  chunk_count                 │    │                    │
│                    │  created_at                  │    │                    │
│                    └──────────────────────────────┘    │                    │
│                                                         │                    │
│  ┌──────────────────────────────────────────────────────┴──────────────┐    │
│  │                    DocumentPermissions (文档权限表)                    │    │
│  ├───────────────────────────────────────────────────────────────────────┤    │
│  │  id (PK)                                                                │    │
│  │  document_id (FK) ───────────────────────────────────────────────────┤    │
│  │  user_id (FK) ──────────────────────────────────────────────────────┤    │
│  │  permission_level (read/write/delete/share)                          │    │
│  │  granted_by (FK) ────────────────────────────────────────────────────┤    │
│  │  created_at                                                            │    │
│  └───────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────┐    ┌─────────────────────────────────────────────────┐    │
│  │ChatSessions │    │              ChatMessages                       │    │
│  ├─────────────┤    ├─────────────────────────────────────────────────┤    │
│  │ id (PK)     │    │ id (PK)                                         │    │
│  │ user_id (FK)│◄───┤ session_id (FK) ────────────────────────────────│    │
│  │   title     │    │ role (user/assistant)                           │    │
│  │ created_at  │    │ content                                         │    │
│  │ updated_at  │    │ sources (JSON)                                  │    │
│  └─────────────┘    │ token_count                                     │    │
│                     │ created_at                                      │    │
│                     └─────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         Feedback (反馈表)                             │    │
│  ├───────────────────────────────────────────────────────────────────────┤    │
│  │  id (PK)                                                                │    │
│  │  message_id (FK) ──────────────────────────────────────────────────────┤    │
│  │  is_helpful (boolean)                                                  │    │
│  │  comment (text)                                                        │    │
│  │  created_at                                                            │    │
│  └───────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      SystemConfig (系统配置)                          │    │
│  ├───────────────────────────────────────────────────────────────────────┤    │
│  │  key (PK)                                                                │    │
│  │  value (JSON)                                                           │    │
│  │  description                                                            │    │
│  │  updated_at                                                             │    │
│  └───────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 3.2 数据表说明

### 3.2.1 用户表 (users)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 用户ID |
| username | VARCHAR(50) | UNIQUE, NOT NULL | 用户名 |
| email | VARCHAR(255) | UNIQUE, NOT NULL | 邮箱 |
| password_hash | VARCHAR(255) | NOT NULL | 加密密码 |
| role | VARCHAR(20) | NOT NULL, DEFAULT='user' | 角色：admin/user/guest |
| is_active | BOOLEAN | NOT NULL, DEFAULT=TRUE | 是否激活 |
| last_login | DATETIME | NULLABLE | 最后登录时间 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.2.2 文档表 (documents)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 文档ID |
| title | VARCHAR(255) | NOT NULL | 文档标题 |
| description | TEXT | NULLABLE | 文档描述 |
| file_type | VARCHAR(50) | NOT NULL | 文件类型 |
| file_size | INTEGER | NOT NULL | 文件大小(字节) |
| file_path | VARCHAR(500) | NOT NULL | 文件存储路径 |
| file_hash | VARCHAR(64) | NULLABLE | 文件SHA256 |
| current_version_id | INTEGER | FK, NULLABLE | 当前版本ID |
| category_id | INTEGER | FK, NULLABLE | 分类ID |
| status | VARCHAR(20) | NOT NULL | 状态：pending/processing/completed/failed |
| error_message | TEXT | NULLABLE | 错误信息 |
| chunk_count | INTEGER | DEFAULT=0 | 向量块数量 |
| created_by | INTEGER | FK, NOT NULL | 创建用户 |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.2.3 文档版本表 (document_versions)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 版本ID |
| document_id | INTEGER | FK, NOT NULL | 文档ID |
| version_number | INTEGER | NOT NULL | 版本号 |
| file_path | VARCHAR(500) | NOT NULL | 文件路径 |
| file_hash | VARCHAR(64) | NOT NULL | 文件哈希 |
| chunk_count | INTEGER | DEFAULT=0 | 块数量 |
| created_by | INTEGER | FK, NOT NULL | 创建用户 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.2.4 分类表 (categories)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 分类ID |
| name | VARCHAR(100) | NOT NULL | 分类名称 |
| description | TEXT | NULLABLE | 分类描述 |
| parent_id | INTEGER | FK, NULLABLE | 父分类ID（自引用） |
| created_by | INTEGER | FK, NOT NULL | 创建用户 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.2.5 文档权限表 (document_permissions)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 权限ID |
| document_id | INTEGER | FK, NOT NULL | 文档ID |
| user_id | INTEGER | FK, NULLABLE | 用户ID（NULL=所有人） |
| permission_level | VARCHAR(20) | NOT NULL | 权限级别：read/write/delete/share |
| granted_by | INTEGER | FK, NOT NULL | 授权用户 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.2.6 聊天会话表 (chat_sessions)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 会话ID |
| title | VARCHAR(255) | NULLABLE | 会话标题 |
| user_id | INTEGER | FK, NOT NULL | 用户ID |
| created_at | DATETIME | NOT NULL | 创建时间 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

### 3.2.7 聊天消息表 (chat_messages)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 消息ID |
| session_id | INTEGER | FK, NOT NULL | 会话ID |
| role | VARCHAR(20) | NOT NULL | 角色：user/assistant |
| content | TEXT | NOT NULL | 消息内容 |
| sources | JSON | NULLABLE | 引用来源 |
| token_count | INTEGER | DEFAULT=0 | Token数量 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.2.8 反馈表 (feedback)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PK, AUTOINCREMENT | 反馈ID |
| message_id | INTEGER | FK, NOT NULL | 消息ID |
| is_helpful | BOOLEAN | NULLABLE | 是否有帮助 |
| comment | TEXT | NULLABLE | 评价内容 |
| created_at | DATETIME | NOT NULL | 创建时间 |

### 3.2.9 系统配置表 (system_config)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| key | VARCHAR(100) | PK | 配置键 |
| value | JSON | NOT NULL | 配置值 |
| description | VARCHAR(255) | NULLABLE | 说明 |
| updated_at | DATETIME | NOT NULL | 更新时间 |

## 3.3 索引设计

| 表名 | 索引字段 | 类型 | 说明 |
|------|----------|------|------|
| users | username | UNIQUE | 登录查询 |
| users | email | UNIQUE | 登录查询 |
| documents | created_by | INDEX | 用户文档列表 |
| documents | category_id | INDEX | 分类筛选 |
| documents | status | INDEX | 状态筛选 |
| categories | parent_id | INDEX | 树形查询 |
| chat_sessions | user_id | INDEX | 用户会话列表 |
| chat_messages | session_id | INDEX | 会话消息查询 |

---

# 第四章：RESTful API 接口设计

## 4.1 API 概述

- **Base URL**: `http://localhost:8000/api/v1`
- **Authentication**: Bearer Token (JWT)
- **Content-Type**: application/json

## 4.2 认证接口 (Auth)

### 4.2.1 用户登录

```yaml
POST /auth/login
Summary: 用户登录
Description: 使用用户名和密码获取访问令牌
Tags: [auth]

RequestBody:
  content:
    application/x-www-form-urlencoded:
      schema:
        type: object
        required:
          - username
          - password
        properties:
          username:
            type: string
            description: 用户名
          password:
            type: string
            description: 密码

Responses:
  200:
    description: 登录成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Token'
        example:
          access_token: "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
          token_type: "bearer"
          expires_in: 2592000

  401:
    description: 用户名或密码错误
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
        example:
          detail: "Incorrect username or password"
```

### 4.2.2 用户注册

```yaml
POST /auth/register
Summary: 用户注册
Description: 创建新用户账号
Tags: [auth]

RequestBody:
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/UserCreate'

Responses:
  201:
    description: 注册成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/UserResponse'

  400:
    description: 用户名或邮箱已存在
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/Error'
```

## 4.3 文档接口 (Documents)

### 4.3.1 获取文档列表

```yaml
GET /documents
Summary: 获取文档列表
Description: 分页获取用户有权限访问的文档列表
Tags: [documents]
Security: [BearerAuth]

Parameters:
  - name: page
    in: query
    schema:
      type: integer
      default: 1
      minimum: 1
  - name: page_size
    in: query
    schema:
      type: integer
      default: 20
      minimum: 1
      maximum: 100
  - name: search
    in: query
    schema:
      type: string
    description: 搜索文档标题
  - name: category_id
    in: query
    schema:
      type: integer
    description: 分类筛选
  - name: status
    in: query
    schema:
      type: string
      enum: [pending, processing, completed, failed]

Responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/DocumentListResponse'
```

### 4.3.2 上传文档

```yaml
POST /documents
Summary: 上传文档
Description: 上传新文档并自动开始解析和向量化
Tags: [documents]
Security: [BearerAuth]
Consumes: [multipart/form-data]

RequestBody:
  content:
    multipart/form-data:
      schema:
        type: object
        required:
          - file
          - title
        properties:
          file:
            type: string
            format: binary
            description: 文档文件
          title:
            type: string
            description: 文档标题
          description:
            type: string
            description: 文档描述
          category_id:
            type: integer
            description: 分类ID

Responses:
  201:
    description: 上传成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/DocumentResponse'

  413:
    description: 文件过大
  415:
    description: 不支持的文件类型
```

### 4.3.3 获取文档详情

```yaml
GET /documents/{document_id}
Summary: 获取文档详情
Tags: [documents]
Security: [BearerAuth]

Parameters:
  - name: document_id
    in: path
    required: true
    schema:
      type: integer

Responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/DocumentResponse'

  404:
    description: 文档不存在
  403:
    description: 无权限访问
```

### 4.3.4 更新文档

```yaml
PUT /documents/{document_id}
Summary: 更新文档
Tags: [documents]
Security: [BearerAuth]

Parameters:
  - name: document_id
    in: path
    required: true
    schema:
      type: integer

RequestBody:
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/DocumentUpdate'

Responses:
  200:
    description: 更新成功
  403:
    description: 无权限修改
```

### 4.3.5 删除文档

```yaml
DELETE /documents/{document_id}
Summary: 删除文档
Description: 软删除文档
Tags: [documents]
Security: [BearerAuth]

Parameters:
  - name: document_id
    in: path
    required: true
    schema:
      type: integer

Responses:
  204:
    description: 删除成功
  403:
    description: 无权限删除
```

## 4.4 分类接口 (Categories)

### 4.4.1 获取分类列表

```yaml
GET /categories
Summary: 获取分类列表
Tags: [categories]
Security: [BearerAuth]

Parameters:
  - name: parent_id
    in: query
    schema:
      type: integer
      nullable: true
    description: 父分类ID，空值返回根分类

Responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/CategoryResponse'
```

### 4.4.2 创建分类

```yaml
POST /categories
Summary: 创建分类
Tags: [categories]
Security: [BearerAuth]

RequestBody:
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CategoryCreate'

Responses:
  201:
    description: 创建成功
```

### 4.4.3 更新分类（管理员）

```yaml
PUT /categories/{category_id}
Summary: 更新分类
Description: 仅管理员可更新
Tags: [categories]
Security: [BearerAuth]
```

### 4.4.4 删除分类（管理员）

```yaml
DELETE /categories/{category_id}
Summary: 删除分类
Description: 仅管理员可删除
Tags: [categories]
Security: [BearerAuth]
```

## 4.5 聊天接口 (Chat)

### 4.5.1 获取会话列表

```yaml
GET /chat/sessions
Summary: 获取会话列表
Tags: [chat]
Security: [BearerAuth]

Responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/ChatSessionResponse'
```

### 4.5.2 创建会话

```yaml
POST /chat/sessions
Summary: 创建会话
Tags: [chat]
Security: [BearerAuth]

RequestBody:
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ChatSessionCreate'

Responses:
  201:
    description: 创建成功
```

### 4.5.3 获取会话消息

```yaml
GET /chat/sessions/{session_id}
Summary: 获取会话消息历史
Tags: [chat]
Security: [BearerAuth]

Responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          type: array
          items:
            $ref: '#/components/schemas/ChatMessageResponse'
```

### 4.5.4 发送消息

```yaml
POST /chat/message
Summary: 发送消息
Description: 发送问题并获取AI回答
Tags: [chat]
Security: [BearerAuth]

RequestBody:
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/ChatRequest'

Responses:
  200:
    description: 成功
    content:
      application/json:
        schema:
          $ref: '#/components/schemas/ChatResponse'
        example:
          message: "根据文档内容，答案是..."
          sources:
            - text: "相关文档内容..."
              score: 0.95
              document_id: 1
          session_id: 1
          token_count: 150
```

## 4.6 响应 Schema 定义

```yaml
components:
  schemas:
    Token:
      type: object
      properties:
        access_token:
          type: string
          description: JWT访问令牌
        token_type:
          type: string
          default: bearer
        expires_in:
          type: integer
          description: 过期时间(秒)

    UserCreate:
      type: object
      required:
        - username
        - email
        - password
      properties:
        username:
          type: string
          minLength: 3
          maxLength: 50
        email:
          type: string
          format: email
        password:
          type: string
          minLength: 6

    UserResponse:
      type: object
      properties:
        id:
          type: integer
        username:
          type: string
        email:
          type: string
        role:
          type: string
        is_active:
          type: boolean
        created_at:
          type: string
          format: date-time

    DocumentResponse:
      type: object
      properties:
        id:
          type: integer
        title:
          type: string
        description:
          type: string
        file_type:
          type: string
        file_size:
          type: integer
        status:
          type: string
        chunk_count:
          type: integer
        created_at:
          type: string
          format: date-time

    DocumentListResponse:
      type: object
      properties:
        items:
          type: array
          items:
            $ref: '#/components/schemas/DocumentResponse'
        total:
          type: integer
        page:
          type: integer
        page_size:
          type: integer
        total_pages:
          type: integer

    ChatSessionResponse:
      type: object
      properties:
        id:
          type: integer
        title:
          type: string
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time

    ChatMessageResponse:
      type: object
      properties:
        id:
          type: integer
        role:
          type: string
          enum: [user, assistant]
        content:
          type: string
        created_at:
          type: string
          format: date-time

    ChatResponse:
      type: object
      properties:
        message:
          type: string
        sources:
          type: array
          items:
            type: object
            properties:
              text:
                type: string
              score:
                type: number
              document_id:
                type: integer
        session_id:
          type: integer
        token_count:
          type: integer

    Error:
      type: object
      properties:
        detail:
          type: string

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

---

# 第五章：RAG 核心流程

## 5.1 整体流程架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         RAG 核心流程                                          │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         索引阶段 (Indexing)                               │
  └─────────────────────────────────────────────────────────────────────────┘

  用户上传文档
       │
       ▼
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │ 文件类型检测 │ ──▶ │  文档解析   │ ──▶ │  文本分块   │ ──▶ │  向量化存储 │
  │             │     │             │     │             │     │             │
  │ • PDF       │     │ • 提取文本  │     │ • 固定大小  │     │ • ChromaDB  │
  │ • DOCX      │     │ • 提取表格  │     │ • 段落分割  │     │ • 批量处理  │
  │ • TXT       │     │ • 提取图片  │     │ • 重叠窗口  │     │ • 元数据    │
  │ • MD        │     │ • OCR识别   │     │             │     │             │
  └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                         查询阶段 (Query)                                  │
  └─────────────────────────────────────────────────────────────────────────┘

  用户提问
       │
       ▼
  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
  │  查询理解   │ ──▶ │  向量检索   │ ──▶ │  结果重排   │ ──▶ │  LLM 生成   │
  │             │     │             │     │             │     │             │
  │ • 意图识别  │     │ • 相似度计算│     │ • 相关性过滤│     │ • 上下文组装│
  │ • 关键词提取│     │ • Top-K 返回│     │ • 分数归一化│     │ • Prompt构建│
  │ • 查询扩展  │     │ • 权限过滤  │     │ • 多路融合  │     │ • 答案生成  │
  └─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

## 5.2 文档解析模块

### 5.2.1 支持的文件格式

| 格式 | 解析库 | 表格支持 | 图片支持 |
|------|--------|----------|----------|
| PDF | PyMuPDF | ✅ | ✅ |
| DOCX | python-docx | ✅ | ❌ |
| TXT | 内置 | N/A | N/A |
| MD | 内置 | N/A | N/A |
| HTML | BeautifulSoup | ❌ | ❌ |

### 5.2.2 解析流程

```
输入: file_path, file_type
输出: List[DocumentChunk]

1. 验证文件类型是否支持
2. 根据文件类型选择解析器
3. 提取纯文本内容
4. 保留页码/段落位置信息
5. 输出结构化文本块
```

## 5.3 文本分块模块

### 5.3.1 分块策略

| 策略 | 参数 | 适用场景 |
|------|------|----------|
| by_paragraph | chunk_size=1000, overlap=200 | 通用场景 |
| by_page | 按页分割 | 报告/论文 |
| by_title | 按标题层级 | 规范文档 |

### 5.3.2 分块算法

```python
# by_paragraph 策略伪代码
def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    paragraphs = split_by_double_newline(text)
    chunks = []
    current_chunk = ""
    
    for para in paragraphs:
        if len(current_chunk) + len(para) <= chunk_size:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks
```

### 5.3.3 分块参数配置

| 参数 | 默认值 | 说明 |
|------|--------|------|
| CHUNK_SIZE | 1000 | 块大小（字符数） |
| CHUNK_OVERLAP | 200 | 块重叠大小 |
| MIN_CHUNK_SIZE | 100 | 最小块大小 |

## 5.4 向量化模块

### 5.4.1 嵌入模型

| 模型 | 维度 | 供应商 | 离线支持 |
|------|------|--------|----------|
| nomic-embed-text | 768 | Ollama | ✅ |
| bge-m3 | 1024 | Ollama | ✅ |
| text-embedding-3-small | 1536 | OpenAI | ❌ |

### 5.4.2 向量化流程

```
输入: text
输出: embedding(List[float])

1. 文本预处理（去除特殊字符、标准化）
2. 调用 Ollama API 获取嵌入向量
3. 返回归一化向量
```

### 5.4.3 批处理优化

- 批量向量化：每次最多处理 100 个文本块
- 并发控制：最大 5 个并发请求
- 错误重试：失败后最多重试 3 次

## 5.5 向量存储模块

### 5.5.1 ChromaDB 配置

```python
# 开发环境配置
chroma_client = chromadb.PersistentClient(
    path="./data/chroma",
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)

# 生产环境配置（Qdrant）
qdrant_client = QdrantClient(
    url="http://qdrant:6333",
    api_key=os.getenv("QDRANT_API_KEY")
)
```

### 5.5.2 集合设计

| 集合名 | 维度 | 说明 |
|--------|------|------|
| documents | 768 | 文档向量集合 |

### 5.5.3 元数据索引

```json
{
  "document_id": 1,
  "chunk_index": 0,
  "start_char": 0,
  "end_char": 500,
  "file_type": "pdf",
  "created_at": "2026-06-04T10:00:00Z"
}
```

## 5.6 检索模块

### 5.6.1 检索流程

```
用户查询
    │
    ▼
查询向量化 ──▶ 向量数据库检索
    │              │
    │              ▼
    │        权限过滤（用户可访问的文档）
    │              │
    │              ▼
    │        相关性过滤（min_score >= 0.3）
    │              │
    ▼              ▼
结果返回 ◀───────
```

### 5.6.2 检索参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| top_k | 5 | 返回结果数量 |
| min_score | 0.3 | 最小相似度阈值 |

### 5.6.3 权限过滤

- 管理员：可检索所有已索引文档
- 普通用户：仅可检索自己创建的或有权限的文档
- 访客：仅可检索公开文档

## 5.7 重排模块

### 5.7.1 重排策略

| 策略 | 说明 |
|------|------|
| similarity_threshold | 过滤低于阈值的结果 |
| diversity_rerank | 避免返回相似度过高的结果 |
| MMR (Maximal Marginal Relevance) | 平衡相关性与多样性 |

### 5.7.2 多路融合

- BM25 稀疏检索 + 向量密检索
- RRF (Reciprocal Rank Fusion) 融合结果

## 5.8 生成模块

### 5.8.1 LLM 配置

| 模型 | 供应商 | 最大Token | 温度 |
|------|--------|-----------|------|
| llama3.1:70b | Ollama | 4096 | 0.7 |
| claude-3-7-sonnet-20250219 | Anthropic | 4096 | 0.7 |

### 5.8.2 Prompt 模板

```python
SYSTEM_PROMPT = """你是一个有帮助的AI助手，基于提供的文档内容回答用户问题。
请准确引用来源，如果文档中没有相关信息，请如实说明。"""

USER_PROMPT = """Context information:
{context}

Based on the above context, please answer the following question.
If the context doesn't provide enough information to answer, say so honestly.

Question: {query}

Answer:"""
```

### 5.8.3 生成参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| MAX_TOKENS | 4096 | 最大生成token数 |
| TEMPERATURE | 0.7 | 生成随机性 |

## 5.9 缓存策略

| 缓存类型 | TTL | 说明 |
|----------|-----|------|
| 查询嵌入 | 1小时 | 相同查询直接返回 |
| LLM响应 | 24小时 | 相同问题+文档的响应 |
| 文档块 | 永久 | 文档ID+块索引 |

---

# 第六章：权限控制设计

## 6.1 权限体系概述

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         权限控制体系                                           │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                      RBAC (基于角色的访问控制)                             │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────┐     ┌─────────┐     ┌─────────┐
  │ Admin   │     │  User   │     │  Guest  │
  │  管理员  │     │  普通用户 │     │   访客   │
  └────┬────┘     └────┬────┘     └────┬────┘
       │               │               │
       │◄──────────────┼──────────────►│
       │               │               │
       ▼               ▼               ▼
  ┌─────────┐     ┌─────────┐     ┌─────────┐
  │ 用户管理  │     │ 文档操作 │     │ 只读    │
  │ 分类管理  │     │ 发起问答 │     │ 文档    │
  │ 系统配置  │     │ 创建分类 │     │         │
  │ 权限分配  │     │          │     │         │
  └─────────┘     └─────────┘     └─────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                    ACL (文档级访问控制)                                   │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                    DocumentPermission                                │
  ├─────────────────────────────────────────────────────────────────────┤
  │  document_id ──┬── user_id ──► 特定用户权限                          │
  │                │                                                          │
  │                ├─── permission_level ──► read/write/delete/share   │
  │                │                                                          │
  │                └─── granted_by ──► 授权人（审计追踪）                │
  └─────────────────────────────────────────────────────────────────────┘
```

## 6.2 RBAC 设计

### 6.2.1 角色定义

| 角色 | 权限描述 | 适用场景 |
|------|----------|----------|
| admin | 完全控制：用户管理、分类管理、系统配置、文档CRUD、权限分配 | 系统管理员 |
| user | 标准权限：文档上传/编辑/删除、发起问答、创建分类 | 企业员工 |
| guest | 有限权限：只读公开文档、发起问答 | 外部合作方 |

### 6.2.2 角色权限矩阵

| 功能 | admin | user | guest |
|------|-------|------|-------|
| 登录系统 | ✅ | ✅ | ✅ |
| 查看文档列表 | 全部 | 有权限的 | 公开的 |
| 上传文档 | ✅ | ✅ | ❌ |
| 编辑自己文档 | ✅ | ✅ | ❌ |
| 删除自己文档 | ✅ | ✅ | ❌ |
| 编辑他/她文档 | ✅ | ❌ | ❌ |
| 删除他/她文档 | ✅ | ❌ | ❌ |
| 创建分类 | ✅ | ✅ | ❌ |
| 删除分类 | ✅ | ❌ | ❌ |
| 管理用户 | ✅ | ❌ | ❌ |
| 系统配置 | ✅ | ❌ | ❌ |
| 发起问答 | ✅ | ✅ | ✅ |

### 6.2.3 角色实现

```python
# backend/app/models/user.py
class User(Base):
    role = Column(String(20), default="user", nullable=False)
    # role ∈ ["admin", "user", "guest"]

# backend/app/deps.py
def get_admin_user(current_user: User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user
```

## 6.3 文档 ACL 设计

### 6.3.1 权限级别

| 权限 | 代码 | 说明 |
|------|------|------|
| read | read | 读取文档内容和问答 |
| write | write | 编辑文档元数据 |
| delete | delete | 删除文档 |
| share | share | 将文档分享给其他用户 |

### 6.3.2 权限继承规则

```
文档创建者
    │
    ├── 自动获得所有权限 (read/write/delete/share)
    │
    ├── 可授予其他用户权限
    │       │
    │       ▼
    │   permission_level: read/write/delete/share
    │
    └── 可设置公开访问
            │
            ▼
        user_id = NULL  →  所有人可访问
```

### 6.3.3 权限表结构

```python
# backend/app/models/permission.py
class DocumentPermission(Base):
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # NULL = 公开
    permission_level = Column(String(20), nullable=False, default="read")
    granted_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
```

## 6.4 权限检查流程

### 6.4.1 文档访问检查

```
用户请求访问文档
        │
        ▼
┌─────────────────┐
│ 获取用户角色     │
└────────┬────────┘
         │
    ┌────┴────┐
    │ admin?  │ ──是──▶ 允许访问
    └────┬────┘
         │否
         ▼
┌─────────────────┐
│ 是创建者?       │
└────────┬────────┘
         │
    ┌────┴────┐
    │  是?    │ ──是──▶ 允许访问
    └────┬────┘
         │否
         ▼
┌─────────────────┐
│ 有ACL权限?      │
└────────┬────────┘
         │
    ┌────┴────┐
    │  有?    │ ──是──▶ 允许访问
    └────┬────┘
         │否
         ▼
    拒绝访问 (403)
```

### 6.4.2 权限检查代码

```python
# backend/app/services/document_service.py
def check_document_access(user: User, document: Document, required_permission: str):
    # 1. 管理员放行
    if user.role == "admin":
        return True
    
    # 2. 创建者拥有所有权限
    if document.created_by == user.id:
        return True
    
    # 3. 检查ACL权限
    permission = db.query(DocumentPermission).filter(
        DocumentPermission.document_id == document.id,
        DocumentPermission.user_id == user.id
    ).first()
    
    if not permission:
        return False
    
    # 4. 权限级别检查
    permission_levels = ["read", "write", "delete", "share"]
    required_level_index = permission_levels.index(required_permission)
    user_level_index = permission_levels.index(permission.permission_level)
    
    return user_level_index >= required_level_index
```

## 6.5 问答权限控制

### 6.5.1 检索范围

| 用户角色 | 可检索文档 |
|----------|------------|
| admin | 所有已索引文档 |
| user | 自己创建的 + ACL授权的 |
| guest | ACL中 user_id=NULL 的公开文档 |

### 6.5.2 实现逻辑

```python
# backend/app/rag/rag_service.py
def _get_user_document_ids(self, db: Session, user_id: int) -> List[int]:
    user = db.query(User).filter(User.id == user_id).first()
    
    # 管理员可访问所有
    if user.role == "admin":
        return db.query(Document.id).all()
    
    # 自己创建的文档
    my_docs = db.query(Document.id).filter(
        Document.created_by == user_id
    ).all()
    
    # ACL授权的文档
    acl_docs = db.query(DocumentPermission.document_id).filter(
        DocumentPermission.user_id == user_id
    ).all()
    
    # 公开文档 (user_id IS NULL)
    public_docs = db.query(DocumentPermission.document_id).filter(
        DocumentPermission.user_id.is_(None)
    ).all()
    
    return list(set(my_docs + acl_docs + public_docs))
```

## 6.6 审计日志

### 6.6.1 审计事件

| 事件 | 记录内容 |
|------|----------|
| 用户登录 | 用户ID、时间、IP |
| 文档上传 | 用户ID、文档ID、文件名 |
| 文档删除 | 用户ID、文档ID、时间 |
| 权限变更 | 授权人、被授权人、权限级别 |
| 敏感操作 | 管理员操作记录 |

### 6.6.2 日志存储

```python
# 审计日志表 (未来扩展)
class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)  # login/upload/delete/grant
    resource_type = Column(String(20))  # document/user/permission
    resource_id = Column(Integer)
    ip_address = Column(String(45))
    created_at = Column(DateTime, server_default=func.now())
```

---

# 第七章：部署架构图

## 7.1 Docker Compose 部署（开发/小规模）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Docker Compose 架构                                   │
└─────────────────────────────────────────────────────────────────────────────┘

                        ┌─────────────────────────────┐
                        │       Host Machine          │
                        │     (Linux/Windows Server)  │
                        └──────────────┬──────────────┘
                                       │
            ┌──────────────────────────┼──────────────────────────┐
            │                          │                          │
            ▼                          ▼                          ▼
┌───────────────────────┐  ┌───────────────────────┐  ┌───────────────────────┐
│     nginx:80          │  │    ollama:11434       │
│   Reverse Proxy       │  │                       │
│   + SSL Termination   │  │   Llama 3.1 70B       │
│                       │  │   (Local LLM)         │
│   • /api/* → backend  │  │                       │
│   • /ollama/* →       │  │                       │
│   • /   → frontend    │  └───────────────────────┘
└───────────┬───────────┘
            │
     ┌──────┼──────┐
     │      │      │
     ▼      ▼      ▼
┌────────┐┌────────┐┌────────┐
│frontend││backend ││ chroma │
│ :5173  ││ :8000  ││ :8000  │
│  React ││FastAPI ││VectorDB│
└────────┘└────────┘└────────┘
     │      │      │
     │      │      │
     └──────┼──────┘
            │
            ▼
┌───────────────────────┐
│   sqlite:5432         │
│   (PostgreSQL)        │
│                       │
│   • users             │
│   • documents         │
│   • categories        │
│   • chat_sessions     │
└───────────────────────┘
```

### 7.1.1 docker-compose.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/dist:/usr/share/nginx/html:ro
    depends_on:
      - frontend
      - backend
    networks:
      - rag-network

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    environment:
      - VITE_API_URL=http://localhost/api/v1
    depends_on:
      - backend
    networks:
      - rag-network

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://rag:ragpass@db:5432/ragdb
      - CHROMA_PERSIST_DIR=/data/chroma
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
    depends_on:
      - db
      - ollama
    networks:
      - rag-network

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=rag
      - POSTGRES_PASSWORD=ragpass
      - POSTGRES_DB=ragdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - rag-network

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - rag-network

volumes:
  postgres_data:
  ollama_data:

networks:
  rag-network:
    driver: bridge
```

### 7.1.2 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| nginx | 80, 443 | HTTP/HTTPS 入口 |
| frontend | 5173 | Vite 开发服务器 |
| backend | 8000 | FastAPI 应用 |
| db | 5432 | PostgreSQL |
| ollama | 11434 | LLM API |

## 7.2 Kubernetes 部署（生产/大规模）

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Kubernetes 架构                                      │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           Load Balancer (云厂商提供)                         │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Ingress Controller (Nginx)                         │
│                      ┌─────────────────────────────┐                        │
│                      │  SSL Termination            │                        │
│                      │  Path-based Routing         │                        │
│                      └─────────────────────────────┘                        │
└─────────────────────────────────┬───────────────────────────────────────────┘
                                  │
           ┌──────────────────────┼──────────────────────┐
           │                      │                      │
           ▼                      ▼                      ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│  Frontend Pod    │    │   Backend Pod    │    │   Backend Pod    │
│  (Deployment)    │    │   (Deployment)   │    │   (Deployment)   │
│  Replicas: 2     │    │  Replicas: 3     │    │  Replicas: 3     │
│                  │    │                  │    │                  │
│  nginx + React   │    │  FastAPI + Gunicorn│   │                  │
└────────┬─────────┘    └────────┬─────────┘    └────────┬─────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌──────────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   PostgreSQL     │    │    Qdrant        │    │    Ollama        │
│   (Deployment)   │    │   (StatefulSet)  │    │  (Deployment)    │
│                  │    │                  │    │                  │
│  Primary + Replica│   │  Replicas: 3     │    │  GPU Required    │
│  (HA)            │    │                  │    │                  │
└──────────────────┘    └──────────────────┘    └──────────────────┘
```

### 7.2.1 Kubernetes 资源清单

```yaml
# backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: rag-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: rag-backend
  template:
    spec:
      containers:
      - name: backend
        image: rag-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: rag-secrets
              key: database-url
        - name: OLLAMA_BASE_URL
          value: "http://ollama-service:11434"
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
---
# qdrant-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: qdrant
spec:
  serviceName: qdrant
  replicas: 3
  selector:
    matchLabels:
      app: qdrant
  template:
    spec:
      containers:
      - name: qdrant
        image: qdrant/qdrant:v1.10.0
        ports:
        - containerPort: 6333
        - containerPort: 6334
        volumeMounts:
        - name: qdrant-storage
          mountPath: /qdrant/storage
  volumeClaimTemplates:
  - metadata:
      name: qdrant-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      storageClassName: fast-storage
      resources:
        requests:
          storage: 50Gi
```

### 7.2.2 服务发现

| 服务 | K8s Service | 内部域名 |
|------|-------------|----------|
| Frontend | ClusterIP | frontend.rag.svc.cluster.local |
| Backend | ClusterIP | backend.rag.svc.cluster.local |
| PostgreSQL | ClusterIP | postgres.rag.svc.cluster.local |
| Qdrant | ClusterIP | qdrant.rag.svc.cluster.local |
| Ollama | ClusterIP | ollama.rag.svc.cluster.local |

## 7.3 存储规划

### 7.3.1 存储类型

| 数据类型 | 存储方案 | 大小预估 | 备份策略 |
|----------|----------|----------|----------|
| PostgreSQL | SSD PV | 10-50GB | 每日增量 |
| ChromaDB/Qdrant | SSD PV | 50-500GB | 每周全量 |
| Ollama Models | SSD PV | 30-100GB | 镜像备份 |
| 上传文件 | NFS/对象存储 | 动态增长 | 按需备份 |

### 7.3.2 备份策略

```bash
# PostgreSQL 备份
pg_dump -h postgres -U rag ragdb > backup_$(date +%Y%m%d).sql

# Qdrant 备份
docker run --rm -v qdrant_storage:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant_backup_$(date +%Y%m%d).tar.gz /data

# 定时任务 (crontab)
0 2 * * * /opt/scripts/backup.sh  # 每日凌晨2点
```

## 7.4 高可用设计

### 7.4.1 组件高可用

| 组件 | 高可用方案 | 故障转移 |
|------|------------|----------|
| Nginx | 多副本 + Keepalived | 自动 |
| Backend | K8s Deployment (3副本) | 自动 |
| PostgreSQL | 主从复制 | 自动 |
| Qdrant | 集群模式 (3节点) | 自动 |
| Ollama | 单点 (无内置HA) | 手动重启 |

### 7.4.2 健康检查

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

---

# 第八章：监控与告警设计

## 8.1 监控体系架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         监控与告警体系                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          数据采集层                                       │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │   Node       │  │   Container  │  │   Application│  │   Custom     │
  │   Exporter   │  │   Exporter   │  │   Metrics    │  │   Exporter   │
  │              │  │              │  │              │  │              │
  │ • CPU/内存   │  │ • CPU/内存   │  │ • 请求延迟   │  │ • 业务指标   │
  │ • 磁盘       │  │ • 网络       │  │ • 错误率     │  │ • RAG指标    │
  │ • 网络       │  │ • 容器状态   │  │ • QPS        │  │ • 用户活跃   │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │                 │
         └─────────────────┼─────────────────┼─────────────────┘
                           │                 │
                           ▼                 ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          时序数据库                                       │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                       Prometheus (TSDB)                              │
  │   • 指标采集  • 存储  • 查询                                           │
  └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          可视化层                                        │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌─────────────────────────────────────────────────────────────────────┐
  │                         Grafana                                       │
  │   • Dashboard  • Alert  • AlertManager                               │
  └─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                          告警通知                                        │
  └─────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │    Email     │  │    Slack     │  │   DingTalk   │  │    Webhook   │
  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
```

## 8.2 监控指标

### 8.2.1 基础设施指标

| 指标名称 | 类型 | 采集方式 | 告警阈值 |
|----------|------|----------|----------|
| node_cpu_usage | Gauge | Node Exporter | > 80% |
| node_memory_usage | Gauge | Node Exporter | > 85% |
| node_disk_usage | Gauge | Node Exporter | > 90% |
| node_network_in | Counter | Node Exporter | - |
| node_network_out | Counter | Node Exporter | - |

### 8.2.2 容器指标

| 指标名称 | 类型 | 采集方式 | 告警阈值 |
|----------|------|----------|----------|
| container_cpu_usage | Gauge | cAdvisor | > 80% |
| container_memory_usage | Gauge | cAdvisor | > 85% |
| container_restart_count | Counter | cAdvisor | > 0 |
| container_status | Gauge | cAdvisor | = 0 (down) |

### 8.2.3 应用指标

| 指标名称 | 类型 | 采集方式 | 告警阈值 |
|----------|------|----------|----------|
| http_requests_total | Counter | 应用埋点 | - |
| http_request_duration_seconds | Histogram | 应用埋点 | P95 > 2s |
| http_request_errors_total | Counter | 应用埋点 | > 10/min |
| api_active_connections | Gauge | 应用埋点 | > 1000 |

### 8.2.4 业务指标

| 指标名称 | 类型 | 采集方式 | 告警阈值 |
|----------|------|----------|----------|
| rag_query_total | Counter | 应用埋点 | - |
| rag_query_duration_seconds | Histogram | 应用埋点 | P95 > 5s |
| rag_documents_indexed | Gauge | 应用埋点 | - |
| rag_vector_store_count | Gauge | 应用埋点 | - |
| chat_sessions_active | Gauge | 应用埋点 | < 1 (无会话) |

## 8.3 告警规则

### 8.3.1 告警规则 YAML

```yaml
# alert-rules.yaml
groups:
  - name: infrastructure
    rules:
      - alert: HighCPUUsage
        expr: node_cpu_usage > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: HighMemoryUsage
        expr: node_memory_usage > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage on {{ $labels.instance }}"
          description: "Memory usage is above 85% for 5 minutes"

      - alert: DiskSpaceLow
        expr: node_disk_usage > 90
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space on {{ $labels.instance }}"
          description: "Disk usage is above 90%"

      - alert: ContainerDown
        expr: container_status == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Container {{ $labels.container }} is down"
          description: "Container has been down for 1 minute"

  - name: application
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, http_request_duration_seconds) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API latency"
          description: "P95 latency is above 2s for 5 minutes"

      - alert: HighErrorRate
        expr: rate(http_request_errors_total[5m]) > 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate"
          description: "Error rate is above 10/min for 2 minutes"

  - name: business
    rules:
      - alert: RAGQueryTimeout
        expr: histogram_quantile(0.95, rag_query_duration_seconds) > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "RAG query timeout"
          description: "RAG query P95 latency is above 10s"

      - alert: NoActiveSessions
        expr: chat_sessions_active == 0
        for: 10m
        labels:
          severity: info
        annotations:
          summary: "No active chat sessions"
          description: "No active chat sessions for 10 minutes"
```

### 8.3.2 告警级别

| 级别 | 描述 | 通知方式 | 响应时间 |
|------|------|----------|----------|
| Critical (P1) | 系统不可用 | 电话 + 短信 + 邮件 | 5分钟 |
| Warning (P2) | 功能受损 | 邮件 + Slack | 30分钟 |
| Info (P3) | 需关注 | 邮件 | 2小时 |

## 8.4 Grafana Dashboard

### 8.4.1 系统概览 Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     System Overview Dashboard                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐          │
│  │   System Uptime  │ │  Active Users    │ │  Documents       │          │
│  │     99.9%        │ │      45          │ │     1,234        │          │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘          │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Request Rate (QPS)                               │   │
│  │  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                     │   │
│  │  ████████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░                   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌───────────────────────────┐ ┌───────────────────────────────────────┐   │
│  │      CPU Usage            │ │         Memory Usage                  │   │
│  │  ██████████████░░░░░░░░░░ │ │  ██████████████░░░░░░░░░░░░░░░░░░░░   │   │
│  └───────────────────────────┘ └───────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    API Response Time                                 │   │
│  │  P50: 120ms  P90: 350ms  P95: 800ms  P99: 1.5s                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.4.2 RAG 业务 Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      RAG Business Dashboard                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐          │
│  │   Total Queries  │ │   Avg Latency    │ │   Success Rate   │          │
│  │     12,456       │ │     1.8s         │ │     98.5%        │          │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘          │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                  Query Latency Distribution                          │   │
│  │  ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░           │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
│  ┌───────────────────────────┐ ┌───────────────────────────────────────┐   │
│  │    Vector Store Size      │ │         Documents by Status           │   │
│  │       456 MB              │ │  Processing: 5  Completed: 1234       │   │
│  └───────────────────────────┘ └───────────────────────────────────────┘   │
│                                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    Top Queries                                       │   │
│  │  1. 如何配置OAuth...      (234次)                                     │   │
│  │  2. API接口文档在哪里...  (189次)                                     │   │
│  │  3. 部署步骤是什么...      (156次)                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                            │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 8.5 日志收集

### 8.5.1 日志架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          日志收集架构                                        │
└─────────────────────────────────────────────────────────────────────────────┘

  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
  │   Backend    │  │   Frontend   │  │   Ollama     │
  │   Logs       │  │   Logs       │  │   Logs       │
  │   (JSON)     │  │   (JSON)     │  │   (Text)     │
  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
         │                 │                 │
         └─────────────────┼─────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                      Fluent Bit / Filebeat                          │
  │   • 收集  • 解析  • 转发                                            │
  └─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                         Elasticsearch                                │
  │   • 存储  • 索引  • 查询                                             │
  └─────────────────────────────────────────────────────────────────────┘
                           │
                           ▼
  ┌─────────────────────────────────────────────────────────────────────┐
  │                          Kibana                                      │
  │   • 可视化  • 搜索  • 分析                                           │
  └─────────────────────────────────────────────────────────────────────┘
```

### 8.5.2 日志级别

| 级别 | 使用场景 |
|------|----------|
| DEBUG | 开发调试信息 |
| INFO | 正常业务流程 |
| WARNING | 潜在问题（可恢复） |
| ERROR | 错误但不影响功能 |
| CRITICAL | 系统级错误 |

## 8.6 告警通知配置

### 8.6.1 AlertManager 配置

```yaml
# alertmanager-config.yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname', 'severity']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'
  routes:
    - match:
        severity: critical
      receiver: 'critical-alerts'
      continue: true
    - match:
        severity: warning
      receiver: 'warning-alerts'

receivers:
  - name: 'default'
    email_configs:
      - to: 'team@example.com'
        send_resolved: true

  - name: 'critical-alerts'
    email_configs:
      - to: 'oncall@example.com'
        send_resolved: true
    slack_configs:
      - channel: '#alerts-critical'
        send_resolved: true
    webhook_configs:
      - url: 'http://dingtalk-webhook:8060/dingtalk/webhook'

  - name: 'warning-alerts'
    email_configs:
      - to: 'team@example.com'
        send_resolved: true
    slack_configs:
      - channel: '#alerts'
        send_resolved: true
```

---

# 设计文档完成

**本文档已完成全部 8 章内容：**

1. ✅ 项目概述与非功能需求
2. ✅ 系统架构图（前后端分离 + RAG 流水线）
3. ✅ 数据模型 ER 图（含权限控制表）
4. ✅ RESTful API 接口设计（OpenAPI 3.0 格式）
5. ✅ RAG 核心流程（分块 → 向量化 → 检索 → 重排 → 生成）
6. ✅ 权限控制设计（RBAC + 文档 ACL）
7. ✅ 部署架构图（Docker Compose + Kubernetes 备选）
8. ✅ 监控与告警设计

---

**请确认是否符合需求，如有修改意见请告知。**