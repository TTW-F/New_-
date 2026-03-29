# Agent Codemap

**最后更新：** 2026-03-29  
**入口：** `medical_agent/agent.py`

## 模块结构

```text
medical_agent/
├── agent.py      # MedicalAgent 主流程
├── tools.py      # ToolRegistry 与默认工具注册
├── memory.py     # 对话记忆管理
├── schemas.py    # AgentResponse / ToolCall / 系统提示词
└── __init__.py
```

## 运行流程

```text
用户问题
 -> Emergency 检查
 -> 组装 messages(system + memory + user)
 -> LLM tool_call 决策
 -> 执行工具并回填 tool 消息
 -> 生成最终答案（可流式）
 -> 写入 memory
```

## 关键能力

- Function Calling 多轮迭代（默认最多 5 轮）
- 同步问答 `chat(stream=False)`
- 流式事件 `chat_stream_events()`，事件类型：
  - `tool_start`
  - `tool_end`
  - `chunk`
  - `meta`
  - `error`
- 紧急关键词检测与紧急响应
- 药物相关免责声明自动追加

## 与后端关系

- `QAService` 以 `session_id` 维度缓存 Agent 实例。
- 登录用户对话会保存到 `conversation_history`。
- 历史会话可通过 `/api/v1/qa/restore` 回填 Agent memory。
