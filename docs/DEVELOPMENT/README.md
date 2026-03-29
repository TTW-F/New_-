# 开发文档

**最后更新：** 2026-03-29

## 1. 本地启动

### 后端

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

## 2. 环境变量（核心）

- `DEEPSEEK_API_KEY`
- `DEEPSEEK_BASE_URL`
- `DEEPSEEK_MODEL`
- `DB_HOST/DB_PORT/DB_USER/DB_PASSWORD/DB_NAME`
- `NEO4J_URI/NEO4J_USER/NEO4J_PASSWORD`
- `REDIS_HOST/REDIS_PORT/REDIS_DB`
- `JWT_SECRET_KEY/JWT_ALGORITHM/JWT_ACCESS_TOKEN_EXPIRE_HOURS`

参考定义：`api/core/config.py`

## 3. 目录职责

- `api/`：后端 API 与业务逻辑
- `medical_agent/`：LLM Agent 与工具机制
- `frontend/src/`：前端应用
- `prepare_data/`：离线数据处理脚本
- `docs/`：项目文档

## 4. 常见开发任务

### 新增后端接口

1. 在 `api/schemas/` 新增请求/响应模型
2. 在 `api/services/` 实现业务逻辑
3. 在 `api/routers/` 暴露路由
4. 在 `api/main.py` 注册 router（若为新模块）
5. 更新 `docs/API/README.md`

### 新增前端页面

1. 在 `frontend/src/views/` 新建页面
2. 在 `frontend/src/router/index.ts` 注册路由
3. 按需新增 store/composable/api 封装
4. 更新 `docs/CODEMAPS/frontend.md`

### 新增 Agent 工具

1. 在 `medical_agent/tools.py` 定义函数
2. 注册到 `ToolRegistry`
3. 校验工具参数 schema
4. 更新 `docs/CODEMAPS/agent.md`

## 5. 已知注意点

- `api/schemas/history.py` 与 `ConversationService.get_sessions_with_details()` 需保持字段一致。
- 管理接口前缀是 `/admin`，并非 `/api/v1/admin`。
- 当前无独立 worker 服务，批处理脚本由人工/批处理文件触发。

## 6. 文档维护约定

每次以下变更后同步更新文档：

- API 新增/删除/字段变更
- 数据模型变更
- 新增核心模块
- 启动流程或环境变量变更
