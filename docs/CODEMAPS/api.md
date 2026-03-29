# API Codemap

**最后更新：** 2026-03-29

## 接口分组总览

| 分组 | 前缀 | 文件 |
|---|---|---|
| Auth | `/api/v1/auth` | `api/routers/auth.py` |
| QA | `/api/v1/qa` | `api/routers/qa.py` |
| History | `/api/v1/history` | `api/routers/history.py` |
| Knowledge | `/api/v1/knowledge` | `api/routers/knowledge.py` |
| Feedback | `/api/v1/feedback` | `api/routers/feedback.py` |
| Health | `/health*` | `api/routers/health.py` |
| Admin | `/admin` | `api/routers/admin.py` |

## 权限模型

- 公开接口：`/`, `/health*`, `/api/v1/auth/register`, `/api/v1/auth/login`。
- 可匿名访问：`/api/v1/qa*`, `/api/v1/knowledge*`（登录后会附带历史能力）。
- 登录必需：`/api/v1/history*`, `/api/v1/feedback*`, `/api/v1/auth/me`, `/api/v1/auth/logout`。
- 管理员必需：`/admin/*`。

## 交互协议

- 标准 JSON API：绝大多数接口。
- SSE 流式：`POST /api/v1/qa/stream`。
- 文档入口：`/docs`、`/openapi.json`（FastAPI 自动生成）。

## 关联文档

- 完整接口清单见：`docs/API/README.md`
- 后端结构见：`docs/CODEMAPS/backend.md`
