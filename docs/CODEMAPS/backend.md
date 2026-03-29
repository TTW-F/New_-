# Backend Codemap

**最后更新：** 2026-03-29  
**入口：** `api/main.py`

## 结构分层

```text
api/
├── main.py            # FastAPI app、middleware、router 注册
├── routers/           # 路由层（auth/qa/history/knowledge/feedback/health/admin）
├── services/          # 业务层（qa/conversation/user）
├── schemas/           # Pydantic 请求/响应模型
├── models/            # SQLAlchemy 模型
├── security/          # JWT、限流、输入清理
└── core/              # 配置、数据库、日志
```

## 路由模块

| 模块 | 前缀 | 主要能力 |
|---|---|---|
| `auth.py` | `/api/v1/auth` | 注册、登录、登出、改密、当前用户 |
| `qa.py` | `/api/v1/qa` | 同步问答、SSE 流式问答、会话管理 |
| `history.py` | `/api/v1/history` | 历史查询、会话列表、删除、统计 |
| `knowledge.py` | `/api/v1/knowledge` | 搜索、推荐、实体详情、图谱数据 |
| `feedback.py` | `/api/v1/feedback` | 反馈提交与查询 |
| `health.py` | `/health*` | 健康、存活、就绪检查 |
| `admin.py` | `/admin` | 管理端统计、用户/会话/日志管理 |

## 核心服务

| 服务 | 位置 | 作用 |
|---|---|---|
| `QAService` | `api/services/qa_service.py` | 会话级 Agent 缓存、同步/流式问答、保存历史 |
| `ConversationService` | `api/services/conversation_service.py` | 历史、会话分页、软删除、反馈写入 |
| `UserService` | `api/services/user_service.py` | 认证、注册、密码处理 |

## 安全与中间件

- JWT 鉴权：`api/security/jwt.py`
- 限流：`api/security/rate_limit.py`（SlowAPI）
- 全局日志与异常处理：`api/main.py`
- CORS：由 `api/core/config.py` 配置

## 后端数据流

```text
Router -> Service -> (MySQL / Redis / Neo4j / MedicalAgent)
       -> Schema -> JSON / SSE 响应
```
