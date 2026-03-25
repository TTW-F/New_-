# 智医问答项目代码地图

## 项目概述

**智医问答** - 基于 Neo4j 知识图谱和 DeepSeek 大语言模型的医疗智能问答系统

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      前端层 (Frontend)                       │
│  Vue 3 + Pinia + TypeScript + SSE                          │
│  - ChatView (聊天主界面)                                    │
│  - ChatStore (状态管理)                                     │
│  - SSEClient (流式通信)                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP / SSE
┌─────────────────────────────────────────────────────────────┐
│                      API 层 (api/)                          │
│  FastAPI + Pydantic + JWT + Rate Limit                      │
│  - main.py (应用入口)                                       │
│  - routers/qa.py (问答端点)                                 │
│  - services/qa_service.py (问答逻辑)                        │
│  - services/conversation_service.py (会话管理)              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Agent 服务层 (medical_agent/)              │
│  MedicalAgent + DeepSeek Function Calling                   │
│  - agent.py (Agent 核心)                                    │
│  - tools.py (工具注册器)                                    │
│  - schemas.py (数据模式)                                    │
│  - memory.py (对话记忆)                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    数据层                                    │
│  Neo4j (知识图谱) + SQLite (用户数据)                       │
│  - neo4j_service.py (图数据库服务)                          │
│  - api/core/database.py (数据库初始化)                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
.
├── api/                          # FastAPI 后端
│   ├── core/                     # 核心配置
│   │   ├── config.py             # 应用配置
│   │   └── database.py           # 数据库初始化
│   ├── routers/                  # API 路由
│   │   └── qa.py                 # 问答相关端点
│   ├── services/                 # 业务逻辑
│   │   ├── qa_service.py         # 问答服务
│   │   └── conversation_service.py # 会话服务
│   ├── security/                 # 安全相关
│   │   └── rate_limit.py         # 速率限制
│   ├── models/                   # 数据模型
│   ├── schemas/                  # Pydantic 模型
│   └── main.py                   # 应用入口
│
├── frontend/                     # Vue 3 前端
│   ├── src/
│   │   ├── api/                  # API 客户端
│   │   │   ├── auth.ts           # 认证 API
│   │   │   └── sse.ts            # SSE 客户端
│   │   ├── components/           # 组件
│   │   │   ├── auth/             # 认证组件
│   │   │   ├── chat/             # 聊天组件
│   │   │   ├── common/           # 通用组件
│   │   │   ├── icons/            # 图标组件
│   │   │   ├── renderers/        # 内容渲染器
│   │   │   └── sidebar/          # 侧边栏
│   │   ├── composables/          # 组合式函数
│   │   │   ├── useAuth.ts        # 认证逻辑
│   │   │   ├── useChat.ts        # 聊天逻辑
│   │   │   ├── useToast.ts       # 提示消息
│   │   │   └── useConfirm.ts     # 确认对话框
│   │   ├── stores/               # Pinia 状态
│   │   │   ├── auth.ts           # 认证状态
│   │   │   └── chat.ts           # 聊天状态
│   │   ├── types/                # TypeScript 类型
│   │   │   ├── api.ts            # API 类型
│   │   │   ├── chat.ts           # 聊天类型
│   │   │   └── sse.ts            # SSE 类型
│   │   ├── utils/                # 工具函数
│   │   │   ├── cache.ts          # 缓存
│   │   │   ├── debounce.ts       # 防抖
│   │   │   ├── error-handler.ts  # 错误处理
│   │   │   ├── format.ts         # 格式化
│   │   │   ├── sanitize.ts       # 消毒
│   │   │   ├── storage.ts        # 存储
│   │   │   └── validator.ts      # 验证
│   │   ├── views/                # 页面视图
│   │   │   ├── ChatView.vue      # 聊天页面
│   │   │   └── LoginView.vue     # 登录页面
│   │   ├── router/               # 路由配置
│   │   └── App.vue               # 根组件
│   └── index.html
│
├── medical_agent/                # 医疗 Agent
│   ├── agent.py                  # Agent 核心类
│   ├── tools.py                  # 工具注册器
│   ├── schemas.py                # 数据模式
│   ├── memory.py                 # 对话记忆
│   └── __init__.py
│
├── data/                         # 数据文件
│   ├── medical.json              # 医疗数据
│   └── medical_data.json         # 医疗数据
│
├── .kiro/                        # Kiro 配置
│   ├── .kiro-agents/             # Agent 定义
│   ├── specs/                    # 规格文档
│   ├── steering/                 # 指导规则
│   └── hooks/                    # 钩子配置
│
└── neo4j_service.py              # Neo4j 服务
```

---

## 🔑 核心模块详解

### 1. 前端 (Frontend)

| 模块 | 文件 | 职责 |
|------|------|------|
| 聊天状态 | `stores/chat.ts` | 管理会话、消息、工具调用状态 |
| 认证状态 | `stores/auth.ts` | 管理用户登录状态和 Token |
| SSE 通信 | `api/sse.ts` | 处理服务器发送事件流式响应 |
| 聊天主界面 | `views/ChatView.vue` | 聊天页面主组件 |
| 消息列表 | `components/chat/MessageList.vue` | 消息展示列表 |
| 输入框 | `components/chat/InputBox.vue` | 用户输入组件 |

### 2. 后端 (API)

| 模块 | 文件 | 职责 |
|------|------|------|
| 应用入口 | `main.py` | FastAPI 应用初始化和配置 |
| 问答路由 | `routers/qa.py` | 定义问答相关 API 端点 |
| 问答服务 | `services/qa_service.py` | 集成 MedicalAgent 处理问答 |
| 会话服务 | `services/conversation_service.py` | 管理对话历史 |
| 配置 | `core/config.py` | 应用配置管理 |

### 3. Agent (medical_agent)

| 模块 | 文件 | 职责 |
|------|------|------|
| Agent 核心 | `agent.py` | 医疗诊断 Agent 主类 |
| 工具注册 | `tools.py` | 工具注册和管理 |
| 数据模式 | `schemas.py` | Agent 相关数据模式定义 |
| 对话记忆 | `memory.py` | 管理对话历史记忆 |

### 4. 数据层

| 模块 | 文件 | 职责 |
|------|------|------|
| Neo4j 服务 | `neo4j_service.py` | 知识图谱查询服务 |
| 数据库 | `api/core/database.py` | 数据库初始化 |

---

## 🔧 工具列表 (ToolRegistry)

| 工具名称 | 功能 |
|----------|------|
| `diagnose_by_symptoms` | 根据症状诊断疾病 |
| `search_disease_info` | 查询疾病详细信息 |
| `get_treatment_plan` | 获取治疗方案 |
| `search_drugs` | 搜索相关药物 |
| `fuzzy_search` | 模糊搜索医疗实体 |

---

## 📊 数据流

### 问答流程

```
用户输入
    ↓
InputBox.vue (收集输入)
    ↓
useChat.ts (发送请求)
    ↓
POST /api/qa/chat
    ↓
qa_service.py (QAService)
    ↓
MedicalAgent (medical_agent/agent.py)
    ↓
工具选择 (Function Calling)
    ↓
neo4j_service.py (查询知识图谱)
    ↓
SSE 流式响应
    ↓
SSEClient (frontend/src/api/sse.ts)
    ↓
ChatStore (更新状态)
    ↓
MessageList.vue (渲染消息)
```

---

## 🔗 依赖关系

### 前端依赖
- **Vue 3** - 框架
- **Pinia** - 状态管理
- **Vue Router** - 路由
- **marked** - Markdown 渲染
- **uuid** - UUID 生成

### 后端依赖
- **FastAPI** - Web 框架
- **Pydantic** - 数据验证
- **SQLAlchemy** - ORM
- **neo4j** - 图数据库驱动
- **OpenAI** - DeepSeek 兼容客户端
- **tenacity** - 重试机制
- **slowapi** - 速率限制
- **python-jose** - JWT 处理

### 外部服务
- **Neo4j** - 知识图谱数据库
- **DeepSeek API** - LLM 服务

---

## 🚀 启动入口

| 文件 | 说明 |
|------|------|
| `start-all.bat` | 启动所有服务 |
| `start-backend.bat` | 启动后端 |
| `start-frontend.bat` | 启动前端 |
| `start-neo4j.bat` | 启动 Neo4j |

---

## 📝 配置文件

| 文件 | 说明 |
|------|------|
| `.env` | 环境变量配置 |
| `requirements.txt` | Python 依赖 |
| `frontend/package.json` | 前端依赖 |

---

## 📚 详细文档

完整的架构文档和代码地图请查看：

- **[文档索引](../docs/CODEMAPS/INDEX.md)** - 所有文档的导航入口
- **[前端架构](../docs/CODEMAPS/frontend.md)** - Vue 3 前端详细文档
- **[后端架构](../docs/CODEMAPS/backend.md)** - FastAPI 后端详细文档
- **[Agent系统](../docs/CODEMAPS/agent.md)** - MedicalAgent 核心文档
- **[数据库架构](../docs/CODEMAPS/database.md)** - Neo4j + SQLite 数据库文档
- **[API参考](../docs/CODEMAPS/api.md)** - 完整的API端点文档

---

*最后更新: 2026-03-25*