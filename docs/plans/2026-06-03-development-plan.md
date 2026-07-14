# 企业内部知识库 AI 问答系统 - 开发计划

> **版本**: 1.0.0
> **日期**: 2026-06-04
> **基于**: 2026-06-03-enterprise-rag-spec.md

---

## 里程碑概览

| 里程碑 | 描述 | 预计任务数 | 预计时间 |
|--------|------|------------|----------|
| M1: MVP | 核心功能可用（用户认证 + 文档上传 + RAG问答） | 45 任务 | 4 小时 |
| M2: 全功能 | 所有设计功能完成 | 35 任务 | 3 小时 |
| M3: 生产就绪 | 部署、监控、测试完善 | 20 任务 | 2 小时 |

---

## 任务统计

- **总任务数**: 100 任务
- **预计总时间**: 9 小时（约 540 分钟）

---

# 第一部分：基础架构 (Infrastructure)

## 任务组 A: 数据库与配置

| ID | 描述 | 依赖 | 文件路径 | 验证步骤 | 预计时间 |
|----|------|------|----------|----------|----------|

### A1: 数据库初始化
| A1.1 | 创建 SQLAlchemy Base 类 | - | `backend/app/db/base.py` | 导入测试无错 | 2 min |
| A1.2 | 配置数据库连接 (SQLite/PostgreSQL) | A1.1 | `backend/app/db/session.py` | 连接测试通过 | 2 min |
| A1.3 | 创建数据库初始化脚本 | A1.2 | `backend/app/db/init_db.py` | 脚本执行成功 | 3 min |

### A2: 环境配置
| A2.1 | 创建 .env.example 配置模板 | - | `backend/.env.example` | 包含所有必需配置项 | 2 min |
| A2.2 | 实现 Settings 类加载环境变量 | - | `backend/app/config.py` | 已存在，跳过 | 2 min |
| A2.3 | 创建常量定义文件 | - | `backend/app/constants.py` | 已存在，跳过 | 2 min |

### A3: Docker 基础镜像
| A3.1 | 编写后端 Dockerfile | A2.1 | `backend/Dockerfile` | 镜像构建成功 | 3 min |
| A3.2 | 编写前端 Dockerfile | - | `frontend/Dockerfile` | 镜像构建成功 | 3 min |
| A3.3 | 创建 docker-compose.yml | A3.1, A3.2 | `docker-compose.yml` | docker-compose config 验证通过 | 3 min |

---

# 第二部分：后端 API (Backend API)

## 任务组 B: 用户认证

| ID | 描述 | 依赖 | 文件路径 | 验证步骤 | 预计时间 |
|----|------|------|----------|----------|----------|

### B1: 用户模型与 Schema
| B1.1 | 创建 User SQLAlchemy 模型 | A1.1 | `backend/app/models/user.py` | 已存在，跳过 | 2 min |
| B1.2 | 创建 User Pydantic Schema | B1.1 | `backend/app/schemas/user.py` | 已存在，跳过 | 2 min |
| B1.3 | 创建 Token Schema | - | `backend/app/schemas/token.py` | 已存在，跳过 | 2 min |

### B2: 安全模块
| B2.1 | 实现密码哈希工具 (bcrypt) | - | `backend/app/core/security.py` | 已存在，跳过 | 2 min |
| B2.2 | 实现 JWT 创建与验证 | B2.1 | `backend/app/core/security.py` | Token 创建/验证测试通过 | 3 min |
| B2.3 | 创建 OAuth2 依赖注入 | B2.2 | `backend/app/deps.py` | 已存在，跳过 | 2 min |

### B3: 认证服务
| B3.1 | 创建 AuthService | B2.1, B1.1 | `backend/app/services/auth_service.py` | 已存在，跳过 | 3 min |
| B3.2 | 创建登录 API 端点 | B3.1 | `backend/app/api/v1/auth.py` | 已存在，跳过 | 2 min |
| B3.3 | 创建注册 API 端点 | B3.1 | `backend/app/api/v1/auth.py` | 已存在，跳过 | 2 min |

## 任务组 C: 文档管理

### C1: 文档模型
| C1.1 | 创建 Document 模型 | A1.1 | `backend/app/models/document.py` | 已存在，跳过 | 2 min |
| C1.2 | 创建 DocumentVersion 模型 | C1.1 | `backend/app/models/document.py` | 已存在，跳过 | 2 min |
| C1.3 | 创建 Document Schema | C1.1 | `backend/app/schemas/document.py` | 已存在，跳过 | 2 min |

### C2: 文档 API
| C2.1 | 创建文档列表 API | C1.3 | `backend/app/api/v1/documents.py` | 已存在，跳过 | 3 min |
| C2.2 | 创建文档上传 API | C2.1 | `backend/app/api/v1/documents.py` | 已存在，跳过 | 3 min |
| C2.3 | 创建文档详情 API | C2.1 | `backend/app/api/v1/documents.py` | 已存在，跳过 | 2 min |
| C2.4 | 创建文档更新 API | C2.1 | `backend/app/api/v1/documents.py` | 已存在，跳过 | 2 min |
| C2.5 | 创建文档删除 API | C2.1 | `backend/app/api/v1/documents.py` | 已存在，跳过 | 2 min |

## 任务组 D: 分类管理

### D1: 分类模型与 API
| D1.1 | 创建 Category 模型 | A1.1 | `backend/app/models/category.py` | 已存在，跳过 | 2 min |
| D1.2 | 创建 Category Schema | D1.1 | `backend/app/schemas/category.py` | 已存在，跳过 | 2 min |
| D1.3 | 创建分类 CRUD API | D1.2 | `backend/app/api/v1/categories.py` | 已存在，跳过 | 3 min |

## 任务组 E: 聊天功能

### E1: 聊天模型
| E1.1 | 创建 ChatSession 模型 | A1.1 | `backend/app/models/chat.py` | 已存在，跳过 | 2 min |
| E1.2 | 创建 ChatMessage 模型 | E1.1 | `backend/app/models/chat.py` | 已存在，跳过 | 2 min |
| E1.3 | 创建 Feedback 模型 | E1.1 | `backend/app/models/chat.py` | 已存在，跳过 | 2 min |
| E1.4 | 创建 Chat Schema | E1.1 | `backend/app/schemas/chat.py` | 已存在，跳过 | 2 min |

### E2: 聊天 API
| E2.1 | 创建会话列表 API | E1.4 | `backend/app/api/v1/chat.py` | 已存在，跳过 | 2 min |
| E2.2 | 创建会话创建 API | E2.1 | `backend/app/api/v1/chat.py` | 已存在，跳过 | 2 min |
| E2.3 | 创建消息历史 API | E2.1 | `backend/app/api/v1/chat.py` | 已存在，跳过 | 2 min |
| E2.4 | 创建发送消息 API | E2.3 | `backend/app/api/v1/chat.py` | 已存在，跳过 | 3 min |

---

# 第三部分：RAG 核心 (RAG Core)

## 任务组 F: 文档处理

### F1: 文档解析器
| F1.1 | 创建 DocumentProcessor 类 | - | `backend/app/rag/document_processor.py` | 已存在，跳过 | 3 min |
| F1.2 | 实现 PDF 解析 | F1.1 | `backend/app/rag/document_processor.py` | PDF 解析测试通过 | 3 min |
| F1.3 | 实现 DOCX 解析 | F1.1 | `backend/app/rag/document_processor.py` | DOCX 解析测试通过 | 3 min |
| F1.4 | 实现 TXT/MD 解析 | F1.1 | `backend/app/rag/document_processor.py` | 文本解析测试通过 | 2 min |

### F2: 文本分块
| F2.1 | 创建 TextChunker 类 | - | `backend/app/rag/chunker.py` | 已存在，跳过 | 3 min |
| F2.2 | 实现 by_paragraph 策略 | F2.1 | `backend/app/rag/chunker.py` | 分块测试通过 | 3 min |
| F2.3 | 实现 by_page 策略 | F2.1 | `backend/app/rag/chunker.py` | 分块测试通过 | 2 min |
| F2.4 | 实现 by_size 策略 | F2.1 | `backend/app/rag/chunker.py` | 分块测试通过 | 2 min |

## 任务组 G: 向量存储

### G1: ChromaDB 集成
| G1.1 | 创建 VectorStore 类 | - | `backend/app/rag/vector_store.py` | 已存在，跳过 | 3 min |
| G1.2 | 实现 add_chunks 方法 | G1.1 | `backend/app/rag/vector_store.py` | 添加向量测试通过 | 3 min |
| G1.3 | 实现 search 方法 | G1.2 | `backend/app/rag/vector_store.py` | 检索测试通过 | 3 min |
| G1.4 | 实现 delete_document 方法 | G1.1 | `backend/app/rag/vector_store.py` | 删除测试通过 | 2 min |

### G2: 嵌入服务
| G2.1 | 创建 EmbeddingService 类 | - | `backend/app/rag/embedding.py` | 已存在，跳过 | 3 min |
| G2.2 | 实现 Ollama 嵌入调用 | G2.1 | `backend/app/rag/embedding.py` | 嵌入生成测试通过 | 3 min |
| G2.3 | 实现 MockEmbeddingService | G2.1 | `backend/app/rag/embedding.py` | 降级服务测试通过 | 2 min |

## 任务组 H: LLM 生成

### H1: LLM 服务
| H1.1 | 创建 LLMService 类 | - | `backend/app/rag/llm.py` | 已存在，跳过 | 3 min |
| H1.2 | 实现 Ollama 生成调用 | H1.1 | `backend/app/rag/llm.py` | 文本生成测试通过 | 3 min |
| H1.3 | 实现 generate_with_sources | H1.2 | `backend/app/rag/llm.py` | 带引用生成测试通过 | 3 min |

## 任务组 I: RAG 服务整合

### I1: RAG 主服务
| I1.1 | 创建 RAGService 类 | F1.1, G1.3, H1.3 | `backend/app/rag/rag_service.py` | 已存在，跳过 | 3 min |
| I1.2 | 实现 index_document 方法 | I1.1 | `backend/app/rag/rag_service.py` | 文档索引测试通过 | 5 min |
| I1.3 | 实现 query 方法 | I1.1 | `backend/app/rag/rag_service.py` | 问答测试通过 | 5 min |
| I1.4 | 实现 _get_user_document_ids | I1.3 | `backend/app/rag/rag_service.py` | 权限过滤测试通过 | 3 min |

### I2: Chat Service 集成
| I2.1 | 创建 ChatService 集成 RAG | E2.4, I1.3 | `backend/app/services/chat_service.py` | 已存在，跳过 | 3 min |
| I2.2 | 实现 send_message 集成 | I2.1 | `backend/app/services/chat_service.py` | 完整问答流程测试通过 | 5 min |

---

# 第四部分：权限控制 (Permission)

## 任务组 J: 权限模型

### J1: 权限模型创建
| J1.1 | 创建 DocumentPermission 模型 | A1.1 | `backend/app/models/permission.py` | 已存在，跳过 | 2 min |
| J1.2 | 创建权限检查依赖 | J1.1 | `backend/app/deps.py` | 权限验证测试通过 | 3 min |

### J2: 权限 API
| J2.1 | 创建权限授予 API | J1.2 | `backend/app/api/v1/permissions.py` | 权限授予测试通过 | 3 min |
| J2.2 | 创建权限撤销 API | J2.1 | `backend/app/api/v1/permissions.py` | 权限撤销测试通过 | 2 min |
| J2.3 | 创建权限查询 API | J2.1 | `backend/app/api/v1/permissions.py` | 权限查询测试通过 | 2 min |

### J3: 权限服务
| J3.1 | 创建 PermissionService | J1.1 | `backend/app/services/permission_service.py` | 权限操作测试通过 | 3 min |

---

# 第五部分：前端 (Frontend)

## 任务组 K: 前端基础

### K1: 项目初始化
| K1.1 | 验证 package.json 依赖 | - | `frontend/package.json` | npm install 成功 | 2 min |
| K1.2 | 配置 Tailwind CSS | K1.1 | `frontend/tailwind.config.js` | 构建测试通过 | 2 min |
| K1.3 | 配置 TypeScript | K1.1 | `frontend/tsconfig.json` | tsc 无错误 | 2 min |

### K2: 公共组件
| K2.1 | 实现 Button 组件 | - | `frontend/src/components/ui/button.tsx` | 已存在，跳过 | 2 min |
| K2.2 | 实现 Input 组件 | - | `frontend/src/components/ui/input.tsx` | 已存在，跳过 | 2 min |
| K2.3 | 实现 Card 组件 | - | `frontend/src/components/ui/card.tsx` | 已存在，跳过 | 2 min |
| K2.4 | 实现 Label 组件 | - | `frontend/src/components/ui/label.tsx` | 已存在，跳过 | 2 min |

### K3: 工具函数
| K3.1 | 创建 utils 工具函数 | - | `frontend/src/lib/utils.ts` | 已存在，跳过 | 2 min |
| K3.2 | 创建 API 客户端 | - | `frontend/src/lib/api.ts` | 已存在，跳过 | 3 min |

## 任务组 L: 认证模块

### L1: 认证状态
| L1.1 | 实现 AuthContext | K3.2 | `frontend/src/context/AuthContext.tsx` | 已存在，跳过 | 3 min |

### L2: 认证页面
| L2.1 | 实现登录页面 | L1.1 | `frontend/src/pages/LoginPage.tsx` | 已存在，跳过 | 3 min |
| L2.2 | 实现注册页面 | L2.1 | `frontend/src/pages/RegisterPage.tsx` | 已存在，跳过 | 3 min |

## 任务组 M: 功能页面

### M1: 布局组件
| M1.1 | 实现 Header 导航 | K2.1 | `frontend/src/components/Header.tsx` | 已存在，跳过 | 3 min |

### M2: 文档页面
| M2.1 | 实现文档列表页面 | K3.2, M1.1 | `frontend/src/pages/DocumentsPage.tsx` | 已存在，跳过 | 5 min |
| M2.2 | 实现文档上传功能 | M2.1 | `frontend/src/pages/DocumentsPage.tsx` | 上传测试通过 | 3 min |

### M3: 聊天页面
| M3.1 | 实现聊天页面布局 | K3.2, M1.1 | `frontend/src/pages/ChatPage.tsx` | 已存在，跳过 | 5 min |
| M3.2 | 实现消息发送功能 | M3.1 | `frontend/src/pages/ChatPage.tsx` | 消息发送测试通过 | 3 min |
| M3.3 | 实现会话列表功能 | M3.1 | `frontend/src/pages/ChatPage.tsx` | 会话切换测试通过 | 3 min |

### M4: 路由配置
| M4.1 | 配置 React Router | L2.2, M2.2, M3.3 | `frontend/src/App.tsx` | 已存在，跳过 | 3 min |
| M4.2 | 添加路由守卫 | M4.1 | `frontend/src/App.tsx` | 未登录跳转测试通过 | 2 min |

---

# 第六部分：测试 (Testing)

## 任务组 N: 单元测试

### N1: 后端单元测试
| N1.1 | 创建 pytest 配置 | - | `backend/pytest.ini` | pytest 运行成功 | 2 min |
| N1.2 | 编写安全模块测试 | B2.2 | `backend/tests/test_core.py` | 已存在，跳过 | 3 min |
| N1.3 | 编写常量测试 | N1.2 | `backend/tests/test_core.py` | 已存在，跳过 | 2 min |
| N1.4 | 编写配置测试 | N1.2 | `backend/tests/test_core.py` | 已存在，跳过 | 2 min |

### N2: API 集成测试
| N2.1 | 编写认证 API 测试 | B3.2 | `backend/tests/test_auth.py` | 登录/注册测试通过 | 3 min |
| N2.2 | 编写文档 API 测试 | C2.5 | `backend/tests/test_documents.py` | CRUD 测试通过 | 5 min |
| N2.3 | 编写聊天 API 测试 | E2.4 | `backend/tests/test_chat.py` | 消息测试通过 | 3 min |

## 任务组 O: E2E 测试

### O1: Playwright 测试
| O1.1 | 配置 Playwright | - | `frontend/playwright.config.ts` | Playwright 安装成功 | 3 min |
| O1.2 | 编写登录 E2E 测试 | O1.1 | `frontend/tests/login.spec.ts` | 登录流程测试通过 | 3 min |
| O1.3 | 编写文档上传 E2E 测试 | O1.2 | `frontend/tests/document.spec.ts` | 上传流程测试通过 | 5 min |
| O1.4 | 编写问答 E2E 测试 | O1.2 | `frontend/tests/chat.spec.ts` | 问答流程测试通过 | 5 min |

---

# 第七部分：部署 (Deployment)

## 任务组 P: Docker 部署

### P1: 生产镜像
| P1.1 | 优化后端 Dockerfile | A3.1 | `backend/Dockerfile` | 镜像大小 < 500MB | 3 min |
| P1.2 | 优化前端 Dockerfile | A3.2 | `frontend/Dockerfile` | 镜像大小 < 200MB | 3 min |
| P1.3 | 添加健康检查配置 | P1.1, P1.2 | `docker-compose.yml` | 健康检查通过 | 2 min |

### P2: 生产部署配置
| P2.1 | 创建生产 docker-compose | P1.3 | `docker-compose.prod.yml` | 启动成功 | 3 min |
| P2.2 | 配置 Nginx 生产配置 | P2.1 | `nginx/nginx.conf` | 静态资源正确服务 | 2 min |
| P2.3 | 添加数据持久化配置 | P2.1 | `docker-compose.prod.yml` | 重启数据保留 | 2 min |

## 任务组 Q: 监控配置

### Q1: 监控部署
| Q1.1 | 部署 Prometheus | - | `k8s/prometheus.yaml` | 指标收集成功 | 3 min |
| Q1.2 | 部署 Grafana | Q1.1 | `k8s/grafana.yaml` | Dashboard 正常显示 | 3 min |
| Q1.3 | 配置告警规则 | Q1.1 | `k8s/alert-rules.yaml` | 告警触发测试通过 | 3 min |

### Q2: 日志收集
| Q2.1 | 配置 Fluent Bit | - | `k8s/fluent-bit.yaml` | 日志收集成功 | 3 min |
| Q2.2 | 配置 Elasticsearch | Q2.1 | `k8s/elasticsearch.yaml` | 日志存储成功 | 3 min |
| Q2.3 | 配置 Kibana | Q2.2 | `k8s/kibana.yaml` | 日志搜索正常 | 2 min |

---

# 里程碑与依赖关系

## 里程碑 1: MVP 完成

**目标**: 核心功能可用（用户认证 + 文档上传 + RAG问答）

**任务列表**:
```
A1.1 → A1.2 → A1.3 → A2.1 → A2.2 → A2.3
     → A3.1 → A3.2 → A3.3

B1.1 → B1.2 → B1.3 → B2.1 → B2.2 → B2.3
     → B3.1 → B3.2 → B3.3

C1.1 → C1.2 → C1.3 → C2.1 → C2.2 → C2.3
     → C2.4 → C2.5

F1.1 → F1.2 → F1.3 → F1.4
F2.1 → F2.2 → F2.3 → F2.4

G1.1 → G1.2 → G1.3 → G1.4
G2.1 → G2.2 → G2.3

H1.1 → H1.2 → H1.3

I1.1 → I1.2 → I1.3 → I1.4
I2.1 → I2.2

K1.1 → K1.2 → K1.3
K2.1 → K2.2 → K2.3 → K2.4
K3.1 → K3.2

L1.1 → L2.1 → L2.2

M1.1 → M2.1 → M2.2
M3.1 → M3.2 → M3.3
M4.1 → M4.2
```

**验证标准**: 用户可以注册登录、上传文档、发起问答并获得答案

---

## 里程碑 2: 全功能完成

**目标**: 所有设计功能完成

**任务列表**:
```
D1.1 → D1.2 → D1.3
E1.1 → E1.2 → E1.3 → E1.4
E2.1 → E2.2 → E2.3 → E2.4

J1.1 → J1.2 → J2.1 → J2.2 → J2.3 → J3.1
```

**验证标准**: 分类管理、权限控制、聊天历史全部可用

---

## 里程碑 3: 生产就绪

**目标**: 部署、监控、测试完善

**任务列表**:
```
N1.1 → N1.2 → N1.3 → N1.4
N2.1 → N2.2 → N2.3

O1.1 → O1.2 → O1.3 → O1.4

P1.1 → P1.2 → P1.3 → P2.1 → P2.2 → P2.3
Q1.1 → Q1.2 → Q1.3
Q2.1 → Q2.2 → Q2.3
```

**验证标准**: 单元测试覆盖 >80%，E2E 测试通过，生产部署可用

---

# 高风险与技术难点

## 高风险任务

| ID | 任务 | 风险描述 | 缓解措施 |
|----|------|----------|----------|

### 风险 1: RAG 问答质量
| I1.3 | query 方法实现 | LLM 生成质量不可控 | 添加来源引用验证fallback |
| I1.2 | index_document 方法 | 文档解析失败 | 添加多种解析器备选 |

### 风险 2: 向量检索性能
| G1.3 | search 方法 | 大数据量检索慢 | 添加 Qdrant 集群支持 |
| G2.2 | Ollama 嵌入调用 | API 超时 | 添加缓存和重试机制 |

### 风险 3: 前端构建
| M4.1 | React Router 配置 | 路由守卫逻辑复杂 | 先实现基础路由再添加守卫 |

### 风险 4: Docker 构建
| A3.1, A3.2 | Dockerfile 编写 | 构建失败 | 使用多阶段构建优化 |

## 技术难点

| ID | 难点 | 说明 |
|----|------|------|

### 难点 1: 文档解析兼容性
- PDF/DOCX 解析可能遇到特殊格式
- 需要处理各种编码问题

### 难点 2: 权限继承逻辑
- 文档创建者权限自动获得
- 公开文档与私有文档的区分

### 难点 3: RAG 检索准确性
- 向量相似度与实际相关性的差异
- 需要调优 top_k 和 min_score 参数

### 难点 4: LLM 生成一致性
- 相同问题可能产生不同答案
- 需要添加缓存策略

---

# 开发顺序建议

## Phase 1: 基础设施 (30 分钟)
```
A1 → A2 → A3 → K1
```

## Phase 2: 核心 API (45 分钟)
```
B → C → D → E → F → G → H → I → L → M
```

## Phase 3: 权限控制 (20 分钟)
```
J
```

## Phase 4: 测试与部署 (30 分钟)
```
N → O → P → Q
```

---

**文档状态**: DRAFT
**最后更新**: 2026-06-04