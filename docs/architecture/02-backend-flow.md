# 后端请求流架构

**最后更新：** 2026-03-29

## 请求链路

```text
Client
 -> FastAPI Router
 -> Depends (DB Session / User Auth)
 -> Service Layer
 -> (MySQL / Redis / Neo4j / MedicalAgent)
 -> Response (JSON 或 SSE)
```

## 问答流（SSE）

1. `POST /api/v1/qa/stream` 接收问题
2. `QAService` 获取/创建会话级 `MedicalAgent`
3. Agent 执行 tool-call 迭代并产出事件
4. Router 将事件包装为 `data: ...\n\n`
5. 前端按 `tool_start/tool_end/chunk/meta` 渲染

## 鉴权流

- Bearer Token 通过 `get_current_user` / `get_current_user_optional` 注入。
- 管理端使用 `require_admin` 二次校验 `user_type`。
- 登出会将 token 写入 `token_blacklist`。

## 可靠性与可观测

- 全局异常处理：`api/main.py`
- 请求日志中间件：记录路径、耗时、状态码
- 健康探针：`/health`, `/health/live`, `/health/ready`
