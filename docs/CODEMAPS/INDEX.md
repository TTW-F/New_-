# 代码地图总索引

**最后更新：** 2026-03-29

## 范围

本索引覆盖当前仓库的核心可运行系统：

- FastAPI 后端（`api/`）
- Vue 3 前端（`frontend/`）
- 医疗 Agent 核心（`medical_agent/`）
- 数据与图谱服务（`api/models`、`neo4j_service.py`、`graphrag_service.py`）

## 子地图

- [frontend.md](./frontend.md)：页面、状态管理、组件分层、前端数据流
- [backend.md](./backend.md)：路由层、服务层、安全层、健康检查
- [database.md](./database.md)：MySQL/Redis/Neo4j 数据结构与关系
- [agent.md](./agent.md)：MedicalAgent 运行机制与工具调用
- [api.md](./api.md)：按模块索引接口分布
- [integrations.md](./integrations.md)：外部依赖与集成点
- [workers.md](./workers.md)：离线脚本与批处理任务

## 全局拓扑

```text
Frontend (Vue + Pinia)
    -> HTTP / SSE
Backend (FastAPI routers)
    -> Services (QA / User / Conversation)
        -> MedicalAgent (DeepSeek Function Calling)
        -> MySQL (users, conversation_history, feedback)
        -> Redis (缓存/限流辅助)
        -> Neo4j (知识图谱)
```

## 主要入口

- 后端启动入口：`api/main.py`
- 前端启动入口：`frontend/src/main.ts`
- Agent 主实现：`medical_agent/agent.py`
- 图谱服务：`neo4j_service.py`

## 现状备注

- 已存在完整管理端接口：`/admin/*`（管理员权限）。
- 问答支持同步与流式两套路径：`/api/v1/qa` 与 `/api/v1/qa/stream`。
- 项目中暂无独立消息队列 worker，离线任务主要在 `prepare_data/` 与根目录脚本中执行。
