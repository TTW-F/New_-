# API 文档（按当前代码生成）

**最后更新：** 2026-03-29

## 1. 认证（`/api/v1/auth`）

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| POST | `/register` | 否 | 注册 |
| POST | `/login` | 否 | 登录 |
| POST | `/logout` | 是 | 登出并拉黑 token |
| GET | `/me` | 是 | 当前用户信息 |
| POST | `/change-password` | 是 | 修改密码 |

## 2. 问答（`/api/v1/qa`）

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| POST | `` | 可匿名 | 同步问答 |
| POST | `/stream` | 可匿名 | SSE 流式问答 |
| GET | `/health` | 否 | 问答服务健康检查 |
| POST | `/restore` | 可匿名(建议登录) | 恢复会话上下文 |
| POST | `/clear` | 可匿名 | 清空会话 memory |
| DELETE | `/session/{session_id}` | 可匿名 | 删除会话 memory |

### SSE 事件

- `tool_start`
- `tool_end`
- `chunk`
- `meta`
- `error`

## 3. 历史（`/api/v1/history`）

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| GET | `` | 是 | 历史列表（分页，可按 `session_id`） |
| GET | `/sessions` | 是 | 会话列表（分页） |
| GET | `/stats` | 是 | 用户历史统计 |
| GET | `/{conversation_id}` | 是 | 单条历史详情 |
| DELETE | `/sessions/{session_id}` | 是 | 删除会话（软删） |
| DELETE | `/{conversation_id}` | 是 | 删除单条历史（软删） |

## 4. 知识库（`/api/v1/knowledge`）

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| GET | `/search` | 可匿名 | 实体检索 |
| GET | `/recommend` | 可匿名 | 推荐实体 |
| GET | `/entity/{entity_name}` | 可匿名 | 实体详情 |
| GET | `/stats` | 可匿名 | 知识库统计 |
| GET | `/graph/{entity_name}` | 可匿名 | 图谱可视化数据 |

## 5. 反馈（`/api/v1/feedback`）

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| POST | `` | 是 | 提交反馈 |
| GET | `/conversation/{conversation_id}` | 是 | 获取某对话反馈 |

## 6. 健康检查

| 方法 | 路径 | 鉴权 | 说明 |
|---|---|---|---|
| GET | `/health` | 否 | 全组件健康状态 |
| GET | `/health/live` | 否 | 存活探针 |
| GET | `/health/ready` | 否 | 就绪探针 |

## 7. 管理端（`/admin`，管理员权限）

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/stats` | 系统统计 |
| GET | `/users` | 用户列表 |
| GET | `/users/{user_id}` | 用户详情 |
| PUT | `/users/{user_id}/toggle-status` | 启停用户 |
| DELETE | `/users/{user_id}` | 删除用户 |
| GET | `/conversations` | 会话列表 |
| GET | `/conversations/{conversation_id}` | 会话详情 |
| GET | `/logs` | 日志查询（当前为简化实现） |

## 8. 错误与兼容性说明

- 历史会话响应字段仍包含 `first_question`，前端依赖该字段。
- `knowledge/stats` 与 `admin/stats` 存在固定估值字段，不是实时图谱统计。
- 认证失败统一走 401；前端 Axios 拦截器会清 token 并重定向登录页（登录/注册接口除外）。
