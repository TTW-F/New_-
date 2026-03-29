# Integrations Codemap

**最后更新：** 2026-03-29

## 外部服务

| 集成 | 配置来源 | 用途 |
|---|---|---|
| DeepSeek API | `DEEPSEEK_*` | 大模型问答与工具调用决策 |
| Neo4j | `NEO4J_*` | 医疗知识图谱查询 |
| MySQL | `DB_*` | 用户、历史、反馈持久化 |
| Redis | `REDIS_*` | 缓存与健康检查/限流辅助 |

## 代码落点

- DeepSeek 客户端：`medical_agent/agent.py`（OpenAI SDK 兼容调用）
- Neo4j 服务：`neo4j_service.py`
- GraphRAG 服务：`graphrag_service.py`
- 数据库连接：`api/core/database.py`

## 请求链路示例

```text
POST /api/v1/qa/stream
 -> QAService
 -> MedicalAgent (DeepSeek)
 -> ToolRegistry
 -> Neo4jService / GraphRAG
 -> SSE 返回前端
```

## 风险提示

- `knowledge/stats` 与 `admin/stats` 中有固定估值字段（非实时统计）。
- 外部服务不可用时，健康检查会降级为 `degraded` 或 `unhealthy`。
