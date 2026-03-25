# 后端架构文档 (Backend)

**最后更新**: 2026-03-25  
**框架**: FastAPI 0.100+  
**入口文件**: `api/main.py`

---

## 📋 目录

- [架构概览](#架构概览)
- [目录结构](#目录结构)
- [核心模块](#核心模块)
- [API路由](#api路由)
- [服务层](#服务层)
- [数据模型](#数据模型)
- [安全机制](#安全机制)
- [数据流](#数据流)
- [依赖注入](#依赖注入)
- [错误处理](#错误处理)
- [性能优化](#性能优化)

---

## 🏗️ 架构概览

后端采用经典的三层架构设计：

```
┌─────────────────────────────────────────────────────────────┐
│                      路由层 (Routers)                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  auth.py      - 用户认证 (注册/登录/登出)            │  │
│  │  qa.py        - 问答服务 (同步/流式)                 │  │
│  │  history.py   - 历史记录 (查询/统计)                 │  │
│  │  feedback.py  - 用户反馈                             │  │
│  │  health.py    - 健康检查                             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      服务层 (Services)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  qa_service.py            - 问答业务逻辑             │  │
│  │  conversation_service.py  - 对话管理                 │  │
│  │  user_service.py          - 用户管理                 │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Models)                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  user.py          - 用户模型                         │  │
│  │  conversation.py  - 对话模型                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
api/
├── core/                     # 核心配置
│   ├── config.py            # 应用配置 (环境变量、常量)
│   ├── database.py          # 数据库连接和会话管理
│   └── __init__.py
│
├── routers/                  # API路由 (端点定义)
│   ├── auth.py              # 认证路由 (5个端点)
│   ├── qa.py                # 问答路由 (5个端点)
│   ├── history.py           # 历史路由 (5个端点)
│   ├── feedback.py          # 反馈路由 (2个端点)
│   ├── health.py            # 健康检查 (1个端点)
│   └── __init__.py
│
├── services/                 # 业务逻辑层
│   ├── qa_service.py        # 问答服务 (Agent集成)
│   ├── conversation_service.py  # 对话服务
│   ├── user_service.py      # 用户服务
│   └── __init__.py
│
├── models/                   # SQLAlchemy数据模型
│   ├── user.py              # User模型
│   ├── conversation.py      # Conversation模型
│   └── __init__.py
│
├── schemas/                  # Pydantic数据模式
│   ├── auth.py              # 认证相关Schema
│   ├── qa.py                # 问答相关Schema
│   ├── history.py           # 历史相关Schema
│   ├── feedback.py          # 反馈相关Schema
│   └── __init__.py
│
├── security/                 # 安全模块
│   ├── jwt.py               # JWT令牌处理
│   ├── rate_limit.py        # 速率限制
│   ├── sanitizer.py         # 输入清理
│   └── __init__.py
│
└── main.py                   # FastAPI应用入口
```

---

## 🔑 核心模块

### 1. 应用入口 (main.py)

**职责**: FastAPI应用初始化、中间件配置、路由注册

**关键配置**:
```python
# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由注册
app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(qa.router, prefix="/api/v1", tags=["问答"])
app.include_router(history.router, prefix="/api/v1", tags=["历史"])
app.include_router(feedback.router, prefix="/api/v1", tags=["反馈"])
app.include_router(health.router, prefix="/api/v1", tags=["健康检查"])
```

### 2. 配置管理 (core/config.py)

**职责**: 环境变量加载、应用配置管理

**关键配置项**:
- `DEEPSEEK_API_KEY`: DeepSeek API密钥
- `NEO4J_URI`: Neo4j连接地址
- `DATABASE_URL`: SQLite数据库路径
- `JWT_SECRET_KEY`: JWT签名密钥
- `RATE_LIMIT_*`: 速率限制配置

### 3. 数据库管理 (core/database.py)

**职责**: 数据库连接池、会话管理、依赖注入

**关键功能**:
```python
# 数据库引擎
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 🛣️ API路由

### 1. 认证路由 (routers/auth.py)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/auth/register` | POST | 用户注册 | ❌ |
| `/auth/login` | POST | 用户登录 (JSON) | ❌ |
| `/auth/login-form` | POST | 用户登录 (表单) | ❌ |
| `/auth/logout` | POST | 用户登出 | ✅ |
| `/auth/me` | GET | 获取当前用户信息 | ✅ |

**关键实现**:
```python
@router.post("/auth/register")
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # 1. 验证密码强度
    # 2. 检查用户名/邮箱是否存在
    # 3. 创建用户
    # 4. 返回用户信息
    pass

@router.post("/auth/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    # 1. 验证用户名和密码
    # 2. 生成JWT Token
    # 3. 返回Token和用户信息
    pass
```

### 2. 问答路由 (routers/qa.py)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/qa` | POST | 同步问答 | ✅ |
| `/qa/stream` | POST | 流式问答 (SSE) | ✅ |
| `/qa/health` | GET | 问答服务健康检查 | ❌ |
| `/qa/restore-session` | POST | 恢复会话上下文 | ✅ |
| `/qa/clear-session` | POST | 清除会话 | ✅ |

**流式问答实现**:
```python
@router.post("/qa/stream")
async def ask_question_stream(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    async def event_generator():
        qa_service = QAService(db)
        
        # 流式处理
        for event in qa_service.process_question_stream(
            question=request.question,
            session_id=request.session_id,
            user_id=current_user.id
        ):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 3. 历史路由 (routers/history.py)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/history` | GET | 获取对话历史 | ✅ |
| `/history/sessions` | GET | 获取会话列表 | ✅ |
| `/history/stats` | GET | 获取用户统计 | ✅ |
| `/history/{conversation_id}` | GET | 获取单个对话 | ✅ |
| `/history/{conversation_id}` | DELETE | 删除对话 | ✅ |

### 4. 反馈路由 (routers/feedback.py)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/feedback` | POST | 提交反馈 | ✅ |
| `/feedback/{conversation_id}` | GET | 获取对话反馈 | ✅ |

### 5. 健康检查路由 (routers/health.py)

| 端点 | 方法 | 功能 | 认证 |
|------|------|------|------|
| `/health` | GET | 系统健康检查 | ❌ |

**健康检查响应**:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-25T12:00:00Z",
  "components": {
    "database": "healthy",
    "neo4j": "healthy",
    "agent": "healthy"
  }
}
```

---

## 🔧 服务层

### 1. 问答服务 (services/qa_service.py)

**职责**: 集成MedicalAgent，处理问答逻辑

**核心类**: `QAService`

**关键方法**:
```python
class QAService:
    def __init__(self, db: Session):
        self.db = db
        self.conversation_service = ConversationService(db)
    
    def _get_agent(self, session_id: str) -> MedicalAgent:
        """获取或创建会话级别的Agent实例"""
        # 实现Agent缓存机制
        pass
    
    def process_question(self, question: str, session_id: str, user_id: int):
        """同步问答处理"""
        # 1. 获取Agent
        # 2. 调用Agent.chat()
        # 3. 保存对话记录
        # 4. 返回结果
        pass
    
    def process_question_stream(self, question: str, session_id: str, user_id: int):
        """流式问答处理"""
        # 1. 获取Agent
        # 2. 调用Agent.chat_stream_events()
        # 3. 逐个yield事件
        # 4. 保存对话记录
        pass
    
    def restore_session_context(self, session_id: str, user_id: int):
        """恢复会话上下文"""
        # 从数据库加载历史对话到Agent记忆
        pass
```

**Agent缓存机制**:
```python
# 会话级别的Agent实例缓存
_session_agents: Dict[str, MedicalAgent] = {}

def _get_agent(self, session_id: str) -> MedicalAgent:
    if session_id not in _session_agents:
        agent = MedicalAgent(session_id=session_id)
        _session_agents[session_id] = agent
    return _session_agents[session_id]
```

### 2. 对话服务 (services/conversation_service.py)

**职责**: 对话历史的CRUD操作

**核心类**: `ConversationService`

**关键方法**:
```python
class ConversationService:
    def save_conversation(
        self,
        user_id: int,
        session_id: str,
        question: str,
        answer: str,
        tool_calls: List[Dict] = None,
        entities: List[Dict] = None
    ) -> Conversation:
        """保存对话记录"""
        pass
    
    def get_conversation_by_id(self, conversation_id: int, user_id: int):
        """获取单个对话"""
        pass
    
    def get_history(self, user_id: int, page: int, page_size: int):
        """分页获取历史记录"""
        pass
```

### 3. 用户服务 (services/user_service.py)

**职责**: 用户管理、密码处理

**核心类**: `UserService`

**关键方法**:
```python
class UserService:
    def hash_password(self, password: str) -> str:
        """密码哈希"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    def verify_password(self, plain: str, hashed: str) -> bool:
        """密码验证"""
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """密码强度验证"""
        # 至少8位，包含大小写字母和数字
        pass
```

---

## 📊 数据模型

### 1. 用户模型 (models/user.py)

```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # 关系
    conversations = relationship("Conversation", back_populates="user")
```

### 2. 对话模型 (models/conversation.py)

```python
class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    tool_calls = Column(JSON)  # 工具调用记录
    entities = Column(JSON)    # 提取的实体
    response_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # 关系
    user = relationship("User", back_populates="conversations")
```

---

## 🔐 安全机制

### 1. JWT认证 (security/jwt.py)

**Token生成**:
```python
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(hours=24))
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return encoded_jwt
```

**Token验证**:
```python
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user
```

### 2. 速率限制 (security/rate_limit.py)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# 应用到路由
@router.post("/qa")
@limiter.limit("60/minute")  # 每分钟60次
async def ask_question(...):
    pass
```

### 3. 输入清理 (security/sanitizer.py)

```python
def sanitize_input(text: str) -> str:
    """清理用户输入，防止XSS和注入攻击"""
    # 移除HTML标签
    # 转义特殊字符
    # 限制长度
    pass
```

---

## 🔄 数据流

### 问答流程

```
用户请求
    ↓
[路由层] qa.py::ask_question_stream()
    ↓
[服务层] QAService::process_question_stream()
    ↓
[Agent层] MedicalAgent::chat_stream_events()
    ↓
[工具层] ToolRegistry::execute_tool()
    ↓
[数据层] Neo4jService::query()
    ↓
[服务层] ConversationService::save_conversation()
    ↓
SSE流式响应给前端
```

---

## 💉 依赖注入

FastAPI使用依赖注入管理资源：

```python
# 数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 当前用户
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    # 验证Token并返回用户
    pass

# 在路由中使用
@router.post("/qa")
async def ask_question(
    request: QuestionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # current_user 和 db 自动注入
    pass
```

---

## ⚠️ 错误处理

### 统一错误响应

```python
class APIException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail

@app.exception_handler(APIException)
async def api_exception_handler(request: Request, exc: APIException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )
```

### 常见错误码

| 状态码 | 说明 | 场景 |
|--------|------|------|
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未认证或Token无效 |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 429 | Too Many Requests | 超过速率限制 |
| 500 | Internal Server Error | 服务器内部错误 |

---

## 🚀 性能优化

### 1. Agent实例缓存
避免重复初始化Agent，使用会话级别缓存。

### 2. 数据库连接池
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 3. 异步处理
使用FastAPI的异步特性处理I/O密集型操作。

### 4. 响应压缩
```python
from fastapi.middleware.gzip import GZipMiddleware
app.add_middleware(GZipMiddleware, minimum_size=1000)
```

---

## 📝 最佳实践

1. **路由层只做参数验证和响应格式化**
2. **业务逻辑放在服务层**
3. **使用Pydantic进行数据验证**
4. **所有数据库操作使用事务**
5. **敏感信息不记录日志**
6. **API版本化 (/api/v1/)**

---

*本文档由 doc-updater agent 生成 @ 2026-03-25*
