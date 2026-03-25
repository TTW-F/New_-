# Design Document: 用户管理与 API 服务模块

## Overview

本设计文档描述医疗诊断智能问答系统的用户管理和 API 服务模块的技术实现方案。该模块基于 **FastAPI** 框架构建，为现有的 GraphRAG 问答核心提供 RESTful API 接口、用户认证、会话管理和对话历史持久化功能。

### 技术选型

| 组件 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 高性能异步框架，自动生成 OpenAPI 文档 |
| 认证 | JWT (python-jose) | 无状态令牌认证 |
| 密码加密 | bcrypt (passlib) | 安全的密码哈希 |
| 数据库 ORM | SQLAlchemy | MySQL 数据库操作 |
| 数据验证 | Pydantic | 请求/响应模型验证 |
| 速率限制 | slowapi | 基于 Redis 的请求限流 |
| 缓存 | Redis | 会话缓存和速率限制 |

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FastAPI Application                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Routers   │  │ Middleware  │  │  Security   │              │
│  │  /auth      │  │  CORS       │  │  JWT Auth   │              │
│  │  /qa        │  │  Logging    │  │  Rate Limit │              │
│  │  /history   │  │  Error      │  │             │              │
│  │  /feedback  │  │  Handler    │  │             │              │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│  ┌──────▼────────────────▼────────────────▼──────┐              │
│  │                  Services Layer                │              │
│  │  ┌────────────┐  ┌────────────┐  ┌──────────┐ │              │
│  │  │UserService │  │ QAService  │  │Conversa- │ │              │
│  │  │            │  │            │  │tionSvc   │ │              │
│  │  └─────┬──────┘  └─────┬──────┘  └────┬─────┘ │              │
│  └────────┼───────────────┼──────────────┼───────┘              │
│           │               │              │                       │
├───────────┼───────────────┼──────────────┼───────────────────────┤
│  ┌────────▼───────────────▼──────────────▼───────┐              │
│  │              Data Access Layer                 │              │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐ │              │
│  │  │  MySQL   │  │  Neo4j   │  │    Redis     │ │              │
│  │  │ (Users,  │  │ (知识图谱)│  │  (Cache,    │ │              │
│  │  │ History) │  │          │  │   Session)  │ │              │
│  │  └──────────┘  └──────────┘  └──────────────┘ │              │
│  └───────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │      GraphRAG Service         │
              │      (已实现的核心服务)         │
              └───────────────────────────────┘
```

## Components and Interfaces

### 1. API Router 模块

#### 1.1 认证路由 (`routers/auth.py`)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from typing import Optional

router = APIRouter(prefix="/api/v1/auth", tags=["认证"])

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    user_type: str = Field(default="patient", pattern="^(doctor|patient|admin)$")

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

@router.post("/register", response_model=dict)
async def register(request: UserRegisterRequest):
    """用户注册"""
    pass

@router.post("/login", response_model=TokenResponse)
async def login(request: UserLoginRequest):
    """用户登录"""
    pass

@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """用户登出"""
    pass
```

#### 1.2 问答路由 (`routers/qa.py`)

```python
router = APIRouter(prefix="/api/v1/qa", tags=["问答"])

class QARequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None

class QAResponse(BaseModel):
    question_id: str
    answer: str
    entities: list
    citations: list
    response_time_ms: int

@router.post("", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    current_user: Optional[dict] = Depends(get_optional_user)
):
    """提交问答请求"""
    pass
```

#### 1.3 对话历史路由 (`routers/history.py`)

```python
router = APIRouter(prefix="/api/v1/history", tags=["对话历史"])

@router.get("", response_model=list)
async def get_history(
    session_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user)
):
    """获取对话历史"""
    pass

@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    current_user: dict = Depends(get_current_user)
):
    """删除对话记录（软删除）"""
    pass
```

#### 1.4 反馈路由 (`routers/feedback.py`)

```python
router = APIRouter(prefix="/api/v1/feedback", tags=["反馈"])

class FeedbackRequest(BaseModel):
    conversation_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback_type: str = Field(..., pattern="^(helpful|incorrect|unclear|other)$")
    comment: Optional[str] = None

@router.post("")
async def submit_feedback(
    request: FeedbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """提交反馈"""
    pass
```

### 2. Service 层

#### 2.1 用户服务 (`services/user_service.py`)

```python
class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register(self, username: str, email: str, 
                       password: str, user_type: str) -> dict:
        """注册新用户"""
        pass
    
    async def authenticate(self, username: str, password: str) -> Optional[dict]:
        """验证用户凭据"""
        pass
    
    async def get_user_by_id(self, user_id: int) -> Optional[dict]:
        """根据 ID 获取用户"""
        pass
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        pass
    
    def hash_password(self, password: str) -> str:
        """哈希密码"""
        pass
    
    def validate_password_strength(self, password: str) -> tuple[bool, str]:
        """验证密码强度"""
        pass
```

#### 2.2 对话服务 (`services/conversation_service.py`)

```python
class ConversationService:
    def __init__(self, db: Session):
        self.db = db
    
    async def save_conversation(
        self, user_id: int, session_id: str, question: str,
        answer: str, entities: list, citations: list, response_time: int
    ) -> int:
        """保存对话记录"""
        pass
    
    async def get_history(
        self, user_id: int, session_id: Optional[str] = None,
        page: int = 1, page_size: int = 20
    ) -> list:
        """获取对话历史"""
        pass
    
    async def soft_delete(self, conversation_id: int, user_id: int) -> bool:
        """软删除对话记录"""
        pass
    
    async def save_feedback(
        self, user_id: int, conversation_id: int,
        rating: int, feedback_type: str, comment: Optional[str]
    ) -> int:
        """保存用户反馈"""
        pass
```

#### 2.3 问答服务 (`services/qa_service.py`)

```python
class QAService:
    def __init__(self, graphrag_service, conversation_service):
        self.graphrag = graphrag_service
        self.conversation = conversation_service
    
    async def process_question(
        self, question: str, user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> dict:
        """处理问答请求"""
        pass
```

### 3. 安全模块

#### 3.1 JWT 认证 (`security/jwt.py`)

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建 JWT Token"""
    pass

def verify_token(token: str) -> Optional[dict]:
    """验证 JWT Token"""
    pass

async def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    """获取当前用户（依赖注入）"""
    pass

async def get_optional_user(token: Optional[str] = Depends(oauth2_scheme_optional)) -> Optional[dict]:
    """获取可选用户（允许匿名）"""
    pass
```

#### 3.2 速率限制 (`security/rate_limit.py`)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# 匿名用户限制
anonymous_limit = "10/minute"

# 登录用户限制
authenticated_limit = "60/minute"

def get_rate_limit(request: Request) -> str:
    """根据用户状态返回速率限制"""
    pass
```

## Data Models

### MySQL 数据模型 (SQLAlchemy)

```python
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    user_type = Column(Enum('doctor', 'patient', 'admin'), default='patient')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class ConversationHistory(Base):
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    related_entities = Column(JSON)
    citations = Column(JSON)
    response_time = Column(Integer)  # 毫秒
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_deleted = Column(Boolean, default=False)

class Feedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    conversation_id = Column(Integer, ForeignKey("conversation_history.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    feedback_type = Column(Enum('helpful', 'incorrect', 'unclear', 'other'))
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class TokenBlacklist(Base):
    """用于存储已登出的 Token（可选，也可用 Redis）"""
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(500), nullable=False, index=True)
    blacklisted_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
```

### Pydantic 响应模型

```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    user_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    session_id: str
    question: str
    answer: Optional[str]
    entities: List[dict]
    citations: List[dict]
    response_time_ms: Optional[int]
    created_at: datetime

class HealthResponse(BaseModel):
    status: str
    version: str
    components: dict
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: 有效注册创建用户

*For any* 有效的注册信息（符合格式要求的用户名、邮箱、密码），注册操作应该成功创建用户，且该用户可以通过相同凭据登录。

**Validates: Requirements 1.1, 2.1**

### Property 2: 重复注册被拒绝

*For any* 已存在的用户名或邮箱，使用相同用户名或邮箱的注册请求应该被拒绝，并返回包含冲突字段信息的错误响应。

**Validates: Requirements 1.2**

### Property 3: 弱密码被拒绝

*For any* 不符合安全要求的密码（少于8位、纯数字、纯字母），注册请求应该被拒绝。

**Validates: Requirements 1.3**

### Property 4: 密码安全存储

*For any* 成功注册的用户，数据库中存储的密码哈希值应该与原始密码不同，且无法从哈希值反推原始密码。

**Validates: Requirements 1.4**

### Property 5: 注册响应不含密码

*For any* 成功的注册请求，响应中应该包含用户基本信息但不包含密码或密码哈希。

**Validates: Requirements 1.5**

### Property 6: 登录凭据验证

*For any* 已注册用户，使用正确的用户名和密码登录应该返回有效的 JWT Token 和用户信息；使用错误凭据应该返回统一的错误信息。

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 7: Token 登出失效

*For any* 已登录用户，执行登出操作后，使用同一 Token 的后续请求应该被拒绝（返回 401）。

**Validates: Requirements 2.5**

### Property 8: 问答响应完整性

*For any* 问答请求，响应应该包含答案、识别的实体列表、引用来源列表和响应时间。

**Validates: Requirements 3.4**

### Property 9: 认证用户对话持久化

*For any* 带有效 JWT Token 的问答请求，对话记录应该被保存到该用户的对话历史中；不带 Token 的请求不应该产生对话历史记录。

**Validates: Requirements 3.2, 3.3**

### Property 10: 对话历史查询正确性

*For any* 用户的对话历史查询，返回的记录应该只属于该用户，按时间倒序排列，且分页参数正确生效。

**Validates: Requirements 4.1, 4.2, 4.5**

### Property 11: 对话记录完整性

*For any* 保存的对话记录，应该包含问题、答案、识别的实体、引用来源和响应时间等完整信息。

**Validates: Requirements 4.3**

### Property 12: 软删除正确性

*For any* 被删除的对话记录，该记录应该在数据库中保留（is_deleted=True）但不出现在用户的对话历史查询结果中。

**Validates: Requirements 4.4**

### Property 13: 反馈保存与验证

*For any* 有效的反馈请求（评分1-5，类型为 helpful/incorrect/unclear/other），反馈应该被保存；对不存在的对话提交反馈应该返回 404。

**Validates: Requirements 5.1, 5.2, 5.3**

### Property 14: 速率限制生效

*For any* 超过速率限制的请求序列（匿名用户 >10次/分钟，登录用户 >60次/分钟），超限请求应该返回 429 状态码。

**Validates: Requirements 6.2, 6.3**

### Property 15: 输入验证防护

*For any* 包含潜在恶意字符（SQL 注入、XSS）的输入，系统应该正确处理而不产生安全漏洞。

**Validates: Requirements 6.1**

### Property 16: 健康检查响应

*For any* 健康检查请求，响应应该包含系统版本和各组件（MySQL、Neo4j、Redis）的连接状态。

**Validates: Requirements 7.1, 7.2, 7.3**

## Error Handling

### HTTP 状态码规范

| 状态码 | 场景 | 响应格式 |
|--------|------|----------|
| 200 | 请求成功 | `{"status": "success", "data": {...}}` |
| 201 | 创建成功 | `{"status": "success", "data": {...}}` |
| 400 | 请求参数错误 | `{"status": "error", "message": "...", "details": [...]}` |
| 401 | 未认证/Token 无效 | `{"status": "error", "message": "认证失败"}` |
| 403 | 权限不足 | `{"status": "error", "message": "权限不足"}` |
| 404 | 资源不存在 | `{"status": "error", "message": "资源不存在"}` |
| 429 | 请求过于频繁 | `{"status": "error", "message": "请求过于频繁", "retry_after": 60}` |
| 500 | 服务器内部错误 | `{"status": "error", "message": "服务器错误"}` |
| 503 | 服务不可用 | `{"status": "error", "message": "服务暂时不可用", "unavailable_components": [...]}` |

### 全局异常处理

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "服务器内部错误"}
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"status": "error", "message": exc.detail}
    )
```

## Testing Strategy

### 测试框架

- **单元测试**: pytest + pytest-asyncio
- **属性测试**: hypothesis
- **API 测试**: httpx (FastAPI TestClient)
- **覆盖率**: pytest-cov

### 单元测试

单元测试用于验证具体示例和边缘情况：

1. **用户服务测试** (`tests/test_user_service.py`)
   - 测试密码哈希和验证
   - 测试密码强度验证的边界情况
   - 测试用户创建和查询

2. **JWT 测试** (`tests/test_jwt.py`)
   - 测试 Token 创建和验证
   - 测试过期 Token 处理
   - 测试无效 Token 处理

3. **对话服务测试** (`tests/test_conversation_service.py`)
   - 测试对话保存和查询
   - 测试软删除功能
   - 测试分页边界情况

### 属性测试 (Property-Based Testing)

使用 hypothesis 库实现属性测试，每个测试至少运行 100 次迭代：

```python
from hypothesis import given, strategies as st, settings

@settings(max_examples=100)
@given(
    username=st.text(min_size=3, max_size=50, alphabet=st.characters(whitelist_categories=('L', 'N'))),
    email=st.emails(),
    password=st.text(min_size=8, max_size=50).filter(lambda p: any(c.isdigit() for c in p) and any(c.isalpha() for c in p))
)
def test_valid_registration_creates_user(username, email, password):
    """
    Feature: user-management-api, Property 1: 有效注册创建用户
    Validates: Requirements 1.1, 2.1
    """
    # 注册用户
    # 验证用户可以登录
    pass
```

### API 集成测试

```python
from fastapi.testclient import TestClient

def test_register_and_login_flow():
    """测试完整的注册-登录流程"""
    pass

def test_qa_with_authentication():
    """测试带认证的问答流程"""
    pass

def test_rate_limiting():
    """测试速率限制"""
    pass
```

### 测试配置

```python
# conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture
def test_db():
    """创建测试数据库"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    yield Session()

@pytest.fixture
def client(test_db):
    """创建测试客户端"""
    app.dependency_overrides[get_db] = lambda: test_db
    return TestClient(app)
```
