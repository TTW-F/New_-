# 智医问答 - 医疗诊断智能问答系统

<div align="center">

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-teal.svg)
![Neo4j](https://img.shields.io/badge/Neo4j-5.0+-red.svg)

基于知识图谱和大语言模型的医疗智能问答系统

[功能特性](#功能特性) • [技术架构](#技术架构) • [快速开始](#快速开始) • [项目结构](#项目结构) • [API 文档](#api-文档)

</div>

---
## 文档导航

- 文档总索引：`docs/INDEX.md`
- 代码地图：`docs/CODEMAPS/INDEX.md`
- 接口文档：`docs/API/README.md`
- 开发文档：`docs/DEVELOPMENT/README.md`
- 架构文档：`docs/architecture/INDEX.md`

## 📋 项目简介

智医问答是一个基于 **Neo4j 知识图谱** 和 **DeepSeek 大语言模型** 的医疗智能问答系统。系统通过 Function Calling 技术实现智能工具选择，结合医疗知识图谱提供准确、专业的医疗咨询服务。

### 核心亮点

- 🧠 **智能推理**：基于 DeepSeek Function Calling 的 Agent 架构，自主选择工具完成复杂医疗查询
- 📊 **知识图谱**：Neo4j 存储的医疗知识图谱，包含疾病、症状、药品、检查等多维度关系
- 🔄 **流式输出**：真正的 SSE 流式响应，实时展示工具调用和回答生成过程
- 💬 **多轮对话**：会话级别的对话记忆管理，支持上下文理解
- 🎨 **现代 UI**：深色主题的 Vue 3 前端，优雅的交互体验

---

## ✨ 功能特性

### 1. 智能诊断

- **症状诊断**：输入症状列表，智能匹配可能的疾病
- **疾病查询**：查询疾病的详细信息、治疗方案、并发症等
- **药物查询**：查询疾病相关的推荐药物及用法用量
- **模糊搜索**：支持医疗实体的模糊搜索

### 2. Agent 能力

- **自主工具选择**：Agent 根据用户问题自动选择合适的工具
- **多步推理**：支持多轮工具调用，完成复杂查询任务
- **错误处理**：智能处理工具调用失败，提供备选方案
- **紧急识别**：自动识别紧急医疗情况，提供紧急处理建议

### 3. 用户体验

- **流式响应**：实时展示工具调用过程和回答生成
- **实体高亮**：自动提取并高亮医疗实体（疾病、症状、药品）
- **对话历史**：保存用户对话记录，支持历史查询
- **免责声明**：自动添加药品使用和紧急情况的免责声明

---

## 🏗️ 技术架构

### 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         前端层                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Vue 3 + Marked.js + SSE                             │  │
│  │  - 流式消息渲染                                       │  │
│  │  - 工具调用可视化                                     │  │
│  │  - Markdown 内容展示                                  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓ HTTP/SSE
┌─────────────────────────────────────────────────────────────┐
│                         API 层                               │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  FastAPI + Pydantic                                  │  │
│  │  - RESTful API                                       │  │
│  │  - SSE 流式端点                                       │  │
│  │  - JWT 认证                                          │  │
│  │  - 速率限制                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Agent 服务层                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  MedicalAgent (原生 Python + DeepSeek)               │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Agent Loop                                    │ │  │
│  │  │  - 消息构建                                     │ │  │
│  │  │  - LLM 调用 (Function Calling)                 │ │  │
│  │  │  - 工具执行                                     │ │  │
│  │  │  - 结果整合                                     │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Tool Registry                                 │ │  │
│  │  │  - diagnose_by_symptoms                        │ │  │
│  │  │  - search_disease_info                         │ │  │
│  │  │  - get_treatment_plan                          │ │  │
│  │  │  - search_drugs                                │ │  │
│  │  │  - fuzzy_search                                │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  Conversation Memory                           │ │  │
│  │  │  - 会话级别记忆                                 │ │  │
│  │  │  - 上下文管理                                   │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                       数据层                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Neo4j      │  │    MySQL     │  │    Redis     │     │
│  │  知识图谱     │  │  用户/对话    │  │    缓存      │     │
│  │              │  │              │  │              │     │
│  │ - Disease    │  │ - users      │  │ - 会话缓存    │     │
│  │ - Symptom    │  │ - convs      │  │ - 速率限制    │     │
│  │ - Drug       │  │ - feedback   │  │              │     │
│  │ - Check      │  │              │  │              │     │
│  │ - Department │  │              │  │              │     │
│  │ - Food       │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      外部服务                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  DeepSeek API                                        │  │
│  │  - deepseek-chat 模型                                │  │
│  │  - Function Calling 支持                             │  │
│  │  - 流式输出                                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

#### 后端

- **框架**：FastAPI 0.100+
- **Agent**：原生 Python + OpenAI SDK (DeepSeek 兼容)
- **数据库**：
  - Neo4j 5.0+ (知识图谱)
  - MySQL 8.0+ (用户数据)
  - Redis 6.0+ (缓存)
- **ORM**：SQLAlchemy 2.0+
- **认证**：JWT (python-jose)
- **限流**：SlowAPI

#### 前端

- **框架**：Vue 3 (CDN)
- **Markdown**：Marked.js
- **样式**：原生 CSS (深色主题)
- **通信**：Fetch API + SSE

#### AI/ML

- **LLM**：DeepSeek Chat (deepseek-chat)
- **技术**：Function Calling
- **推理**：Agent Loop (最多 5 轮迭代)

---

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+ (前端开发)
- MySQL 8.0+
- **Neo4j 5.0+** (必需，系统核心依赖)
- Redis 6.0+ (可选，用于缓存)
- Docker (可选，用于 Redis/Neo4j)

### 1. 克隆项目

```bash
git clone <repository-url>
cd medical-qa-system
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# DeepSeek API
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat

# MySQL
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=medical_qa

# Neo4j
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# JWT
JWT_SECRET_KEY=your_secret_key_change_in_production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_HOURS=24
```

### 4. 启动 Neo4j 数据库（必需）

⚠️ **重要**：Neo4j 是系统的核心依赖，必须先启动才能使用问答功能。

#### 方式 1：使用 Neo4j Desktop（推荐）

1. 下载并安装 [Neo4j Desktop](https://neo4j.com/download/)
2. 打开 Neo4j Desktop
3. 创建或选择一个数据库实例
4. 点击 "Start" 按钮启动数据库
5. 确保端口 7687 (Bolt) 和 7474 (HTTP) 可访问
6. 记录数据库的用户名和密码（默认：neo4j/neo4j，首次登录需修改）

#### 方式 2：使用 Docker

```bash
docker run -d \
  --name neo4j-medical \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/your_password \
  -v neo4j-data:/data \
  neo4j:latest
```

#### 方式 3：使用命令行（需先安装 Neo4j）

```bash
# Windows
start-neo4j.bat

# 或直接使用 Neo4j 命令
neo4j console
```

#### 验证 Neo4j 连接

访问 http://localhost:7474 打开 Neo4j Browser，使用配置的用户名和密码登录。

### 5. 初始化数据库

```bash
# 创建 MySQL 数据库
mysql -u root -p
CREATE DATABASE medical_qa CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 导入医疗数据到 Neo4j（确保 Neo4j 已启动）
python neo4j_import.py
```

### 6. 启动服务

#### 方式 1：一键启动（Windows，推荐）

```bash
# 启动所有服务（后端 + 前端 + Neo4j）
start-all.bat

# 或分别启动
start-backend.bat  # 仅启动后端
start-frontend.bat # 仅启动前端
```

✨ **智能启动特性**：
- `start-all.bat` 会自动检查 Neo4j 连接状态
- 如果 Neo4j 未运行且已安装，脚本会自动在新窗口中启动 Neo4j
- 脚本会等待最多 30 秒确保 Neo4j 成功启动
- 如果 Neo4j 未安装，会显示详细的安装指南

⚠️ **注意**：
- 如果使用 Neo4j Desktop，建议手动启动数据库以获得更好的控制
- 自动启动功能需要 Neo4j 命令行工具（`neo4j.bat`）在系统 PATH 中

#### 方式 2：手动启动

```bash
# 1. 启动 Neo4j（必需）
# 参考上面的 Neo4j 启动方式

# 2. 启动 MySQL
net start MySQL80

# 3. 启动 Redis (可选，Docker)
docker start redis-medical-qa

# 4. 启动后端 API 服务
# 激活虚拟环境
.venv\Scripts\activate
# 启动 FastAPI
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload

# 5. 启动前端开发服务器（新终端）
cd frontend
npm run dev
```

### 7. 访问应用

- **前端应用**：http://localhost:3000
- **后端 API**：http://localhost:8000
- **API 文档**：http://localhost:8000/docs
- **Neo4j 浏览器**：http://localhost:7474

### 8. 停止服务

```bash
# Windows 一键停止
stop-all.bat

# 或手动停止各个服务
# 在对应的终端窗口按 Ctrl+C
```

---

## 📁 项目结构

```
medical-qa-system/
├── api/                          # FastAPI 后端
│   ├── core/                     # 核心配置
│   │   ├── config.py            # 应用配置
│   │   └── database.py          # 数据库连接
│   ├── models/                   # SQLAlchemy 模型
│   │   ├── user.py              # 用户模型
│   │   └── conversation.py      # 对话模型
│   ├── routers/                  # API 路由
│   │   ├── auth.py              # 认证路由
│   │   ├── qa.py                # 问答路由
│   │   ├── history.py           # 历史记录路由
│   │   └── feedback.py          # 反馈路由
│   ├── schemas/                  # Pydantic 模型
│   │   ├── user.py              # 用户 Schema
│   │   └── qa.py                # 问答 Schema
│   ├── security/                 # 安全模块
│   │   ├── jwt.py               # JWT 认证
│   │   └── rate_limit.py        # 速率限制
│   ├── services/                 # 业务逻辑
│   │   ├── qa_service.py        # 问答服务
│   │   └── conversation_service.py  # 对话服务
│   └── main.py                   # FastAPI 应用入口
│
├── medical_agent/                # Agent 核心
│   ├── agent.py                 # MedicalAgent 主类
│   ├── tools.py                 # 工具注册器
│   ├── memory.py                # 对话记忆
│   └── schemas.py               # Agent Schema
│
├── frontend/                     # Vue 3 前端
│   ├── index.html               # 主页面
│   ├── app.js                   # Vue 应用
│   └── styles.css               # 样式文件
│
├── data/                         # 数据文件
│   └── medical_data.json        # 医疗数据
│
├── prepare_data/                 # 数据准备脚本
│   └── spider.py                # 数据爬虫
│
├── neo4j_service.py             # Neo4j 服务
├── neo4j_import.py              # 数据导入脚本
├── requirements.txt             # Python 依赖
├── start.bat                    # 一键启动脚本
├── .env                         # 环境变量
└── README.md                    # 项目文档
```

---

## 🔧 核心模块详解

### 1. MedicalAgent

`medical_agent/agent.py` - 智能医疗 Agent 核心

**主要功能**：
- Agent Loop 推理循环
- Function Calling 工具调用
- 流式输出支持
- 对话记忆管理

**关键方法**：
```python
# 同步问答
response = agent.chat(message="我头痛发热", stream=False)

# 流式问答
for event in agent.chat_stream_events(message="糖尿病怎么治疗"):
    if event["type"] == "chunk":
        print(event["content"], end="")
```

### 2. Tool Registry

`medical_agent/tools.py` - 工具注册和管理

**内置工具**：
1. `diagnose_by_symptoms` - 症状诊断
2. `search_disease_info` - 疾病信息查询
3. `get_treatment_plan` - 治疗方案查询
4. `search_drugs` - 药物查询
5. `fuzzy_search` - 模糊搜索

**工具注册示例**：
```python
registry = ToolRegistry()
registry.register(
    name="diagnose_by_symptoms",
    func=diagnose_function,
    description="根据症状诊断疾病",
    parameters={...}
)
```

### 3. Neo4j Service

`neo4j_service.py` - 知识图谱查询服务

**图谱结构**：
- **节点类型**：Disease, Symptom, Drug, Check, Department, Food
- **关系类型**：HAS_SYMPTOM, RECOMMAND_DRUG, NEED_CHECK, BELONGS_DEPARTMENT, SHOULD_EAT, SHOULD_AVOID, COMPLICATION

**查询示例**：
```python
# 根据症状查找疾病
diseases = neo4j_service.find_diseases_by_symptoms(
    symptoms=["头痛", "发热"],
    top_k=5
)

# 获取疾病完整信息
context = neo4j_service.get_disease_full_context("糖尿病")
```

### 4. QA Service

`api/services/qa_service.py` - 问答服务层

**功能**：
- 会话级别的 Agent 实例管理
- 流式事件转发
- 对话历史保存

**流式输出事件**：
```json
// 工具开始
{"type": "tool_start", "tool_id": "...", "tool_name": "...", "arguments": {...}}

// 工具结束
{"type": "tool_end", "tool_id": "...", "status": "success", "result": "..."}

// 内容块
{"type": "chunk", "content": "..."}

// 元数据
{"type": "meta", "entities": [...], "response_time_ms": 1234}
```

---

## 📡 API 文档

### 认证相关

#### POST /api/v1/auth/register
注册新用户

**请求体**：
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123"
}
```

#### POST /api/v1/auth/login
用户登录

**请求体**：
```json
{
  "username": "user123",
  "password": "password123"
}
```

**响应**：
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "user": {...}
}
```

### 问答相关

#### POST /api/v1/qa
同步问答

**请求体**：
```json
{
  "question": "糖尿病有什么症状？",
  "session_id": "optional-session-id"
}
```

**响应**：
```json
{
  "question_id": "abc123",
  "session_id": "session-456",
  "question": "糖尿病有什么症状？",
  "answer": "糖尿病的主要症状包括...",
  "entities": [
    {"type": "Disease", "name": "糖尿病"},
    {"type": "Symptom", "name": "多饮"}
  ],
  "citations": [...],
  "response_time_ms": 1234
}
```

#### POST /api/v1/qa/stream
流式问答（SSE）

**请求体**：同上

**响应**：Server-Sent Events 流

```
data: {"type": "tool_start", "tool_name": "search_disease_info", ...}

data: {"type": "tool_end", "status": "success", ...}

data: {"type": "chunk", "content": "糖尿病"}

data: {"type": "meta", "entities": [...]}

data: [DONE]
```

### 历史记录

#### GET /api/v1/history
获取对话历史

**查询参数**：
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）

**响应**：
```json
{
  "total": 100,
  "page": 1,
  "page_size": 20,
  "conversations": [...]
}
```

---

## 🎨 前端特性

### 1. 流式消息渲染

前端使用 SSE 接收流式事件，实时渲染：

```javascript
const eventSource = new EventSource('/api/v1/qa/stream');

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === 'tool_start') {
    // 显示工具调用开始
  } else if (data.type === 'chunk') {
    // 追加内容块
  }
};
```

### 2. Markdown 渲染

使用 Marked.js 渲染 Markdown 内容：

```javascript
marked.setOptions({
  breaks: false,
  gfm: true
});

const html = marked.parse(markdown);
```

### 3. 工具调用可视化

工具调用以卡片形式展示，支持展开/收起：

```html
<div class="tool-card" :class="tool.status">
  <div class="tool-header" @click="toggleToolExpand(tool)">
    <div class="tool-icon">🔧</div>
    <div class="tool-name">{{ tool.name }}</div>
    <div class="tool-status-badge">{{ tool.status }}</div>
  </div>
  <div class="tool-result" v-show="tool.expanded">
    {{ tool.result }}
  </div>
</div>
```

---

## 🔐 安全特性

### 1. JWT 认证

- 使用 JWT Token 进行用户认证
- Token 有效期 24 小时
- 支持 Token 刷新

### 2. 速率限制

- 匿名用户：10 次/分钟
- 认证用户：60 次/分钟

### 3. 密码加密

- 使用 bcrypt 加密存储密码
- 密码强度验证

### 4. CORS 配置

- 支持跨域请求
- 可配置允许的源

---

## 📊 数据说明

### Neo4j 知识图谱

**节点统计**：
- Disease（疾病）：~8000 个
- Symptom（症状）：~5000 个
- Drug（药品）：~3000 个
- Check（检查）：~500 个
- Department（科室）：~50 个
- Food（食物）：~1000 个

**关系统计**：
- HAS_SYMPTOM：~50000 条
- RECOMMAND_DRUG：~30000 条
- NEED_CHECK：~10000 条
- 其他关系：~20000 条

### 数据来源

数据来源于公开的医疗知识库和医学文献，经过清洗和结构化处理。

---

## 🛠️ 开发指南

### 添加新工具

1. 在 `medical_agent/tools.py` 中定义工具函数
2. 注册工具到 ToolRegistry
3. 更新工具 Schema

```python
def my_new_tool(param1: str) -> str:
    """工具功能描述"""
    # 实现逻辑
    return result

registry.register(
    name="my_new_tool",
    func=my_new_tool,
    description="工具描述",
    parameters={
        "type": "object",
        "properties": {
            "param1": {
                "type": "string",
                "description": "参数描述"
            }
        },
        "required": ["param1"]
    }
)
```

### 自定义 Agent 行为

修改 `medical_agent/schemas.py` 中的 `SYSTEM_PROMPT`：

```python
SYSTEM_PROMPT = """
你是一个专业的医疗助手...
[自定义指令]
"""
```

### 扩展 API 端点

在 `api/routers/` 目录下创建新的路由文件：

```python
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/my_module", tags=["我的模块"])

@router.get("/")
async def my_endpoint():
    return {"message": "Hello"}
```

在 `api/main.py` 中注册路由：

```python
from api.routers import my_module
app.include_router(my_module.router)
```

---

## 🐛 故障排查

### 1. Neo4j 连接失败（最常见）

**错误**：`由于目标计算机积极拒绝，无法连接` 或 `Couldn't connect to localhost:7687`

**原因**：Neo4j 数据库未启动

**解决方案**：
1. **检查 Neo4j 是否运行**：
   - 打开 Neo4j Desktop，确认数据库状态为 "Running"
   - 或访问 http://localhost:7474 查看是否能打开 Neo4j Browser
   
2. **启动 Neo4j**：
   - 使用 Neo4j Desktop：点击数据库的 "Start" 按钮
   - 使用命令行：运行 `start-neo4j.bat` 或 `neo4j console`
   - 使用 Docker：`docker start neo4j-medical`

3. **验证连接**：
   ```bash
   # Windows PowerShell
   Test-NetConnection -ComputerName localhost -Port 7687
   ```

4. **检查配置**：
   - 确认 `.env` 文件中的 Neo4j 配置正确：
     ```env
     NEO4J_URI=bolt://localhost:7687
     NEO4J_USER=neo4j
     NEO4J_PASSWORD=your_password
     ```

### 2. Agent 初始化失败

**错误**：`DEEPSEEK_API_KEY 未设置`

**解决**：检查 `.env` 文件中的 `DEEPSEEK_API_KEY` 配置

### 3. MySQL 连接失败

**错误**：`Access denied for user`

**解决**：
1. 确认 MySQL 服务正在运行
2. 检查数据库用户权限
3. 验证 `.env` 中的数据库配置

### 4. 前端无法连接后端

**错误**：`Network Error` 或 `Failed to fetch`

**解决**：
1. 确认后端服务已启动（http://localhost:8000/docs 可访问）
2. 检查前端环境变量 `VITE_API_BASE_URL`
3. 检查 CORS 配置

### 5. 流式输出中断

**问题**：SSE 连接意外断开

**解决**：
1. 检查网络连接
2. 增加超时时间
3. 查看服务器日志
4. 确认 Neo4j 连接稳定

---

## 📈 性能优化

### 1. Agent 实例缓存

系统使用会话级别的 Agent 实例缓存，避免重复初始化：

```python
_session_agents: Dict[str, MedicalAgent] = {}
```

### 2. 数据库连接池

使用 SQLAlchemy 连接池管理数据库连接：

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
```

### 3. Redis 缓存

使用 Redis 缓存频繁查询的数据：

```python
redis_client = get_redis()
cached_data = redis_client.get(cache_key)
```

---

## 📝 免责声明

本系统仅供学习和研究使用，不构成任何医疗建议。

- ⚠️ 系统提供的信息仅供参考，不能替代专业医疗诊断
- ⚠️ 任何医疗决策应咨询专业医生
- ⚠️ 紧急情况请立即拨打 120 或前往医院急诊

---

## 📄 许可证

MIT License

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📧 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件

---

<div align="center">

**智医问答** - 让医疗知识触手可及

Made with ❤️ by Medical QA Team

</div>

