# 企业内部知识库 AI 问答系统 - Superpowers 开发规则
## 技术栈（强制执行，禁止擅自变更）
- 前端：React 18.3 + TypeScript 5.5 + Tailwind CSS v3.4 + shadcn/ui
- 后端：Python 3.12 + FastAPI 0.115 + Pydantic v2.9
- 向量数据库：ChromaDB（本地开发）+ Qdrant 1.10（生产集群）
- 文档解析：LangChain 0.3 + Unstructured.io 0.16 + PyMuPDF（OCR 可选）
- 大模型：Claude 3.7 Sonnet（默认）+ Llama 3.1 70B（本地）
- 工具链：Git + Docker Compose + pytest + Playwright + Black + Ruff
- 协议支持：Model Context Protocol（MCP）用于扩展工具

## 代码规范（Claude 自动检查）
- Python：严格遵循 PEP 8，使用 Black 格式化、Ruff 静态检查
- TypeScript：ESLint + Prettier，强制类型注解，禁止 any 类型
- 所有函数必须包含类型注解和 Google 风格 docstring
- 错误处理：业务边界抛出自定义异常，统一全局异常处理
- 日志：使用 structlog 结构化日志，禁止 print() 调试
- 提交信息：Conventional Commits 规范（feat/fix/docs/test/refactor）
- 敏感信息：全部通过环境变量注入，禁止硬编码

## 开发流程（Superpowers 标准）
1. 设计先行：设计文档未确认前，禁止编写任何业务代码
2. 测试驱动：严格执行 RED-GREEN-REFACTOR 循环
3. 小步提交：每个微任务一个提交，提交信息清晰可追溯
4. 代码审查：所有 PR 必须通过 Claude 自动审查 + 人工确认
5. 文档同步：代码修改必须同步更新对应文档与 API 注释

## 测试要求（不达标禁止合并）
- 单元测试覆盖率 ≥ 80%（核心模块 ≥ 90%）
- 所有 API 端点必须有集成测试
- RAG 核心流程必须有端到端测试
- 性能测试：单条问答响应时间 ≤ 2s（95% 分位）
- 测试命令：`pytest tests/ -v --cov=src --cov-report=html`

## 禁止事项（违反直接终止任务）
❌ 禁止在 main 分支直接开发
❌ 禁止修改已应用的数据库迁移文件
❌ 禁止向外部 API 发送企业内部敏感数据
❌ 禁止生成任何 TBD（待确定）内容
❌ 禁止 Agent 自动合并到 main 分支
❌ 禁止使用未在技术栈中列出的第三方库