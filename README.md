# 企业内部知识库 AI 问答系统

基于 RAG (Retrieval-Augmented Generation) 的企业内部知识库问答系统，支持文档管理、智能问答、权限控制。

## 特性

- 📄 文档管理：支持 PDF、Word、Excel、PPT、Markdown 等格式
- 💬 智能问答：基于本地大模型的 RAG 问答系统
- 🔐 权限控制：细粒度的文档访问权限管理
- 🐳 Docker 部署：一键部署到企业内网
- 🔒 完全离线：无需外部网络连接

## 技术栈

- 前端：React 18 + TypeScript + Tailwind CSS + shadcn/ui
- 后端：Python 3.12 + FastAPI + Pydantic v2
- 向量数据库：ChromaDB
- 大模型：Ollama (Llama 3)
- 部署：Docker Compose

## 快速开始

### 前置要求

- Docker 24.0+
- Docker Compose 2.0+
- 至少 8GB 内存（推荐 16GB）

### 启动步骤

```bash
# 1. 克隆项目
git clone <repository-url>
cd enterprise-rag

# 2. 复制环境配置
cp backend/.env.example backend/.env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看日志
docker-compose logs -f

# 5. 初始化数据库
docker-compose exec backend python scripts/init_db.py

# 6. 下载 Ollama 模型（首次启动）
docker-compose exec ollama ollama pull llama3
```

### 访问系统

- 前端：http://localhost
- API 文档：http://localhost/docs
- Ollama：http://localhost:11434

### 默认账号

- 用户名：admin
- 密码：admin123

## 开发

```bash
# 启动开发环境
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# 前端开发
cd frontend
pnpm install
pnpm dev

# 后端开发
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 项目结构

```
enterprise-rag/
├── docker-compose.yml     # Docker Compose 配置
├── frontend/              # React 前端
│   ├── src/
│   │   ├── pages/         # 页面组件
│   │   ├── components/    # UI 组件
│   │   ├── hooks/         # 自定义 Hooks
│   │   └── api/           # API 调用
│   └── package.json
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/           # API 路由
│   │   ├── services/      # 业务逻辑
│   │   ├── models/        # 数据模型
│   │   └── rag/           # RAG 核心
│   └── requirements.txt
└── nginx/                 # Nginx 配置
```

## License

MIT