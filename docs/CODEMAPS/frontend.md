# Frontend Codemap

**最后更新：** 2026-03-29  
**入口：** `frontend/src/main.ts`

## 架构分层

```text
src/
├── views/          # 路由页面
├── components/     # UI 组件（chat/common/sidebar/icons/...）
├── stores/         # Pinia 状态（auth/chat/ui）
├── api/            # HTTP API 封装
├── router/         # 路由与守卫
├── composables/    # 可复用逻辑
├── utils/          # 工具函数
└── types/          # TS 类型定义
```

## 路由页面

| 路由 | 页面 | 鉴权 |
|---|---|---|
| `/` | `HomeView.vue` | 需要登录 |
| `/chat` | `ChatView.vue` | 需要登录 |
| `/history` | `HistoryView.vue` | 需要登录 |
| `/knowledge` | `KnowledgeView.vue` | 需要登录 |
| `/profile` | `ProfileView.vue` | 需要登录 |
| `/admin` | `AdminView.vue` | 需要管理员 |
| `/login` | `LoginView.vue` | 公开 |

## 关键模块

| 模块 | 位置 | 作用 |
|---|---|---|
| Router 守卫 | `src/router/index.ts` | 登录态检查、管理员权限检查 |
| Auth Store | `src/stores/auth.ts` | Token 与用户信息管理 |
| Chat Store | `src/stores/chat.ts` | 会话、消息、流式状态维护 |
| HTTP 客户端 | `src/api/client.ts` | Axios 实例、401 全局处理 |
| SSE 客户端 | `src/api/sse.ts` | EventSource 封装和重连机制 |

## 数据流

```text
用户输入 -> chat store -> /api/v1/qa/stream
         <- tool_start/tool_end/chunk/meta SSE
         -> MessageList / MessageItem / ToolCallCard 渲染
```

## 外部依赖（前端）

- Vue 3.5 + Vue Router 4.6 + Pinia 3.0
- Axios（HTTP）
- markdown-it / highlight.js（富文本渲染）
- echarts / relation-graph-vue3（知识图谱可视化）
