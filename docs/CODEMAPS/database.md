# Database Codemap

**最后更新：** 2026-03-29

## 数据存储拓扑

```text
MySQL (结构化业务数据)
  - users
  - token_blacklist
  - conversation_history
  - feedback

Redis (缓存与连接可用性检查)
Neo4j (医疗知识图谱)
```

## MySQL 模型映射

| 表 | ORM 模型 | 关键字段 |
|---|---|---|
| `users` | `api/models/user.py::User` | `username,email,password_hash,user_type,is_active` |
| `token_blacklist` | `TokenBlacklist` | `token,user_id,expires_at` |
| `conversation_history` | `ConversationHistory` | `user_id,session_id,question,answer,related_entities,citations,response_time,is_deleted` |
| `feedback` | `Feedback` | `conversation_id,rating,feedback_type,comment` |

## 索引与特性

- `users.username` / `users.email` 唯一索引。
- `conversation_history` 支持软删除（`is_deleted`）。
- 对话关联按 `session_id` 聚合。
- `related_entities` 与 `citations` 以 JSON 字段存储。

## Neo4j（图谱）

核心节点类型（由 `neo4j_service.py` 查询逻辑推断）：

- `Disease`
- `Symptom`
- `Drug`
- `Check`
- `Department`
- `Food`

常见关系类型：

- `HAS_SYMPTOM`
- `RECOMMAND_DRUG`
- `NEED_CHECK`
- `BELONGS_DEPARTMENT`
- `SHOULD_EAT`
- `SHOULD_AVOID`
- `COMPLICATION`

## 连接与初始化

- MySQL/Redis 连接在 `api/core/database.py`。
- 配置来源在 `api/core/config.py`（`.env`）。
- 表初始化在 `init_db()`，应用启动时执行。
