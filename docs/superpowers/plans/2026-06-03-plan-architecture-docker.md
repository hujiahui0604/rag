# 系统架构与 Docker 部署计划

> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** 完成项目目录结构搭建、Docker Compose 配置、基础容器化部署

**Architecture:** 前后端分离 + Docker Compose 编排，完全本地化部署

**Tech Stack:** Docker, Docker Compose, Nginx, Node.js 20, Python 3.12

---

## 文件结构

```
enterprise-rag/
├── docker-compose.yml           # Docker Compose 主配置
├── docker-compose.override.yml  # 开发环境覆盖配置
├── .dockerignore
│
├── frontend/                    # React 前端
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── public/
│   │   └── favicon.ico
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css
│       ├── api/
│       │   └── client.ts
│       ├── components/
│       │   └── ui/              # shadcn/ui 组件
│       ├── pages/
│       ├── hooks/
│       └── types/
│
├── backend/                     # FastAPI 后端
│   ├── Dockerfile
│   ├── Dockerfile.dev
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env.example
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── deps.py
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── db/
│   │   └── rag/
│   ├── scripts/
│   │   ├── init_db.py
│   │   └── seed_data.py
│   └── tests/
│
├── nginx/                       # Nginx 配置
│   └── nginx.conf
│
├── data/                        # 数据目录（运行时）
│   ├── db/
│   ├── chroma/
│   └── documents/
│
├── docs/                        # 文档
│   └── superpowers/
│       ├── specs/
│       ├── plans/
│       └── reports/
│
└── README.md
```

---

## Task 1: 创建 Docker Compose 主配置

**Files:**
- Create: `docker-compose.yml`

- [ ] **Step 1: 创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  # Nginx 反向代理
  nginx:
    image: nginx:alpine
    container_name: erag-nginx
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - frontend-static:/usr/share/nginx/html:ro
    depends_on:
      - frontend
      - backend
    networks:
      - erag-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # React 前端
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: erag-frontend
    env_file:
      - ./frontend/.env.production
    environment:
      - NODE_ENV=production
    volumes:
      - frontend-static:/app/build
      - /app/node_modules
    networks:
      - erag-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "test", "-f", "/app/build/index.html"]
      interval: 30s
      timeout: 10s
      retries: 3

  # FastAPI 后端
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: erag-backend
    env_file:
      - ./backend/.env
    environment:
      - PYTHONUNBUFFERED=1
      - DATABASE_URL=sqlite:///./data/db/rag.db
      - CHROMA_PATH=/app/data/chroma
      - DATA_PATH=/app/data/documents
      - OLLAMA_BASE_URL=http://ollama:11434
    volumes:
      - ./data:/app/data
      - ollama-models:/root/.ollama
    depends_on:
      ollama:
        condition: service_healthy
    networks:
      - erag-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Ollama 本地大模型
  ollama:
    image: ollama/ollama:latest
    container_name: erag-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - erag-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 60s
      timeout: 30s
      retries: 5
      start_period: 120s
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
        reservations:
          memory: 4G
          cpus: '2'

networks:
  erag-network:
    driver: bridge

volumes:
  frontend-static:
  ollama-models:
```

- [ ] **Step 2: 创建 docker-compose.override.yml（开发环境）**

```yaml
version: '3.8'

services:
  frontend:
    build:
      dockerfile: Dockerfile.dev
    ports:
      - "3000:3000"
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    environment:
      - NODE_ENV=development
      - CHOKIDAR_USEPOLLING=true
    command: npm run dev

  backend:
    build:
      dockerfile: Dockerfile.dev
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DEBUG=true
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  nginx:
    profiles:
      - production
    ports:
      - "80:80"
```

- [ ] **Step 3: 创建 .dockerignore**

```bash
# backend
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info/
dist/
build/
.env
.venv/
venv/
ENV/
.git/
.pytest_cache/
.coverage
htmlcov/

# frontend
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
build/
.DS_Store
*.local

# data
data/
*.db

# docs
docs/
```

- [ ] **Step 4: 提交**

```bash
git add docker-compose.yml docker-compose.override.yml .dockerignore
git commit -m "feat(docker): add docker-compose configuration"
```

---

## Task 2: 创建前端 Docker 配置

**Files:**
- Create: `frontend/Dockerfile`
- Create: `frontend/Dockerfile.dev`
- Create: `frontend/nginx.conf`

- [ ] **Step 1: 创建生产 Dockerfile**

```dockerfile
# frontend/Dockerfile
# 构建阶段
FROM node:20-alpine AS builder

WORKDIR /app

# 安装 pnpm
RUN npm install -g pnpm

# 复制依赖文件
COPY package.json pnpm-lock.yaml* ./

# 安装依赖
RUN if [ -f pnpm-lock.yaml ]; then pnpm install --frozen-lockfile; else npm install; fi

# 复制源码
COPY . .

# 构建
RUN pnpm build

# 生产阶段
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

- [ ] **Step 2: 创建开发 Dockerfile**

```dockerfile
# frontend/Dockerfile.dev
FROM node:20-alpine

WORKDIR /app

RUN npm install -g pnpm

COPY package.json pnpm-lock.yaml* ./
RUN pnpm install --frozen-lockfile

COPY . .

EXPOSE 3000

CMD ["pnpm", "dev"]
```

- [ ] **Step 3: 创建 nginx.conf**

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/json application/xml;
    gzip_comp_level 6;

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # SPA 路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy";
    }
}
```

- [ ] **Step 4: 提交**

```bash
git add frontend/Dockerfile frontend/Dockerfile.dev frontend/nginx.conf
git commit -m "feat(docker): add frontend Docker configuration"
```

---

## Task 3: 创建后端 Docker 配置

**Files:**
- Create: `backend/Dockerfile`
- Create: `backend/Dockerfile.dev`
- Modify: `backend/requirements.txt`

- [ ] **Step 1: 创建生产 Dockerfile**

```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    # PDF 处理
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    # 文档格式支持
    libreoffice \
    # 工具
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制源码
COPY . .

# 创建数据目录
RUN mkdir -p /app/data/{db,chroma,documents}

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: 创建开发 Dockerfile**

```dockerfile
# backend/Dockerfile.dev
FROM python:3.12-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    libreoffice \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 安装开发依赖
RUN pip install --no-cache-dir pytest pytest-cov pytest-asyncio black ruff

COPY . .

RUN mkdir -p /app/data/{db,chroma,documents}

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

- [ ] **Step 3: 更新 requirements.txt 添加 Docker 相关依赖**

```python
# backend/requirements.txt 更新
# 添加 alembic 用于数据库迁移
alembic>=1.13.0
```

- [ ] **Step 4: 创建 .env.example**

```bash
# backend/.env.example
# ===== 应用配置 =====
APP_NAME=Enterprise RAG
APP_VERSION=1.0.0
DEBUG=false

# ===== 数据库 =====
DATABASE_URL=sqlite:///./data/db/rag.db

# ===== JWT =====
JWT_SECRET_KEY=change-this-secret-key-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# ===== 文件存储 =====
DATA_PATH=./data/documents
MAX_UPLOAD_SIZE=52428800

# ===== ChromaDB =====
CHROMA_PATH=./data/chroma

# ===== Ollama =====
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3

# ===== RAG 配置 =====
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
RETRIEVAL_TOP_K=4
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000

# ===== 日志 =====
LOG_LEVEL=INFO
```

- [ ] **Step 5: 提交**

```bash
git add backend/Dockerfile backend/Dockerfile.dev backend/.env.example
git commit -m "feat(docker): add backend Docker configuration"
```

---

## Task 4: 创建 Nginx 独立配置

**Files:**
- Create: `nginx/nginx.conf`

- [ ] **Step 1: 创建 Nginx 主配置**

```nginx
# nginx/nginx.conf
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml application/json application/javascript application/xml application/xml+rss text/javascript;

    # 上游服务
    upstream frontend {
        server frontend:80;
    }

    upstream backend {
        server backend:8000;
    }

    server {
        listen 80;
        server_name localhost;

        # 前端静态文件
        location / {
            proxy_pass http://frontend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_cache_bypass $http_upgrade;
        }

        # API 代理
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 75s;
        }

        # Ollama 代理
        location /ollama/ {
            proxy_pass http://ollama:11434/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 300s;
        }

        # 健康检查
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
```

- [ ] **Step 2: 提交**

```bash
git add nginx/nginx.conf
git commit -m "feat(docker): add Nginx configuration"
```

---

## Task 5: 创建前端项目基础结构

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tailwind.config.js`
- Create: `frontend/postcss.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/index.css`

- [ ] **Step 1: 创建 package.json**

```json
{
  "name": "enterprise-rag-frontend",
  "version": "1.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx}\""
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0",
    "axios": "^1.7.7",
    "zustand": "^4.5.5",
    "clsx": "^2.1.1",
    "tailwind-merge": "^2.5.2",
    "class-variance-authority": "^0.7.0",
    "@radix-ui/react-dialog": "^1.1.1",
    "@radix-ui/react-dropdown-menu": "^2.1.1",
    "@radix-ui/react-slot": "^1.1.0",
    "@radix-ui/react-tabs": "^1.1.0",
    "@radix-ui/react-toast": "^1.2.1",
    "lucide-react": "^0.441.0",
    "tailwindcss-animate": "^1.0.7"
  },
  "devDependencies": {
    "@types/react": "^18.3.8",
    "@types/react-dom": "^18.3.0",
    "@typescript-eslint/eslint-plugin": "^8.6.0",
    "@typescript-eslint/parser": "^8.6.0",
    "@vitejs/plugin-react": "^4.3.1",
    "autoprefixer": "^10.4.20",
    "eslint": "^8.57.0",
    "eslint-plugin-react-hooks": "^4.6.2",
    "eslint-plugin-react-refresh": "^0.4.12",
    "postcss": "^8.4.45",
    "prettier": "^3.3.3",
    "tailwindcss": "^3.4.11",
    "typescript": "^5.5.4",
    "vite": "^5.4.6"
  }
}
```

- [ ] **Step 2: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

- [ ] **Step 3: 创建 Tailwind 配置**

```javascript
// frontend/tailwind.config.js
/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ["class"],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "2rem",
      screens: {
        "2xl": "1400px",
      },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
}
```

- [ ] **Step 4: 创建 PostCSS 配置**

```javascript
// frontend/postcss.config.js
export default {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
```

- [ ] **Step 5: 创建 index.html**

```html
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>企业知识库 AI 问答系统</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
```

- [ ] **Step 6: 创建入口文件**

```tsx
// frontend/src/main.tsx
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

- [ ] **Step 7: 创建 App.tsx**

```tsx
// frontend/src/App.tsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { LoginPage } from './pages/LoginPage'
import { MainLayout } from './components/layout/MainLayout'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Navigate to="/chat" replace />} />
          {/* 其他页面路由后续添加 */}
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App
```

- [ ] **Step 8: 创建样式文件**

```css
/* frontend/src/index.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 221.2 83.2% 53.3%;
    --radius: 0.5rem;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

- [ ] **Step 9: 提交**

```bash
git add frontend/package.json frontend/tsconfig.json frontend/tailwind.config.js
git add frontend/postcss.config.js frontend/index.html
git add frontend/src/main.tsx frontend/src/App.tsx frontend/src/index.css
git commit -m "feat(frontend): add basic frontend project structure"
```

---

## Task 6: 创建后端基础项目结构

**Files:**
- Modify: `backend/app/main.py` (更新版本)
- Create: `backend/alembic.ini`

- [ ] **Step 1: 创建 alembic 配置**

```ini
# backend/alembic.ini
[alembic]
script_location = alembic
prepend_sys_path = .
version_path_separator = os

sqlalchemy.url = sqlite:///./data/db/rag.db

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

- [ ] **Step 2: 更新 main.py 添加健康检查**

```python
# backend/app/main.py 更新
@app.get("/health")
def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "ollama": "not_checked"  # 后续可以添加 Ollama 连接检查
    }

@app.get("/")
def root():
    """API 根路径"""
    return {
        "message": "Enterprise RAG API",
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }
```

- [ ] **Step 3: 创建基础 API 路由**

```python
# backend/app/api/v1/root.py 更新
@router.get("/health")
def api_health():
    """API 健康检查"""
    return {"status": "healthy"}
```

- [ ] **Step 4: 提交**

```bash
git add backend/alembic.ini backend/app/main.py backend/app/api/v1/root.py
git commit -m "feat(backend): add alembic and update health check"
```

---

## Task 7: 创建 README 和快速启动脚本

**Files:**
- Create: `README.md`

- [ ] **Step 1: 创建 README**

```markdown
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
```

- [ ] **Step 2: 提交**

```bash
git add README.md
git commit -m "docs: add project README"
```

---

## Task 8: 验证 Docker 部署

- [ ] **Step 1: 构建并启动服务**

```bash
# 构建镜像
docker-compose build

# 启动服务（后台）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

- [ ] **Step 2: 验证健康检查**

```bash
# Nginx
curl http://localhost/health

# 后端
curl http://localhost:8000/health

# Ollama
curl http://localhost:11434/api/tags
```

- [ ] **Step 3: 验证前端访问**

```bash
curl http://localhost
```

- [ ] **Step 4: 提交**

```bash
git add .
git commit -m "chore: verify docker deployment"
```

---

## 完成总结

✅ 已完成的系统架构和 Docker 部署计划：

1. Docker Compose 主配置（多服务编排）
2. 开发环境覆盖配置
3. 前端 Docker 配置（构建、开发）
4. 后端 Docker 配置（构建、开发）
5. Nginx 反向代理配置
6. 前端项目基础结构
7. 后端项目配置
8. README 文档
9. Docker 部署验证流程

**下一步计划：**

- **Phase 2:** 数据模型（用户、文档、分类、权限、聊天等数据库表）
- **Phase 3:** API 接口（RESTful 端点）
- **Phase 4:** RAG 核心（文档解析、分块、向量化、检索、生成）
- **Phase 5:** 权限系统（JWT、RBAC）
- **Phase 6:** 前端开发（完整 UI）

请确认是否批准此计划，然后我将开始执行。