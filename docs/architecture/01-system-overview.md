# 系统架构总览

**最后更新：** 2026-03-29

## 分层图

```text
[Vue Frontend]
  routes/views/components/stores
        |
        | HTTP + SSE
        v
[FastAPI Backend]
  routers -> services -> security/core
        |
        +-> [MedicalAgent + DeepSeek]
        +-> [MySQL + Redis]
        +-> [Neo4j + GraphRAG]
```

## 运行入口

- 后端：`uvicorn api.main:app`
- 前端：`vite` (`frontend/package.json`)

## 核心能力

- 医疗问答（同步 + SSE 流式）
- 会话记忆与历史管理
- 知识图谱检索与关系可视化
- 管理后台统计与用户管理

## 架构特征

- 单体后端 + 单体前端（仓库同源）
- 服务层封装业务逻辑，路由层负责协议与鉴权
- Agent 作为后端内部能力，不单独部署
- 离线任务依赖脚本，无常驻 worker
