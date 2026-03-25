# Requirements Document

## Introduction

本文档定义了智能医疗问答系统前端交互页面优化和流式传输增强的需求。目标是提升用户体验，实现更流畅的实时响应显示、工具调用状态展示，以及基于 Server-Sent Events (SSE) 的事件订阅机制。

## Glossary

- **Frontend_App**: 基于 Vue 3 的前端单页应用
- **SSE**: Server-Sent Events，服务器推送事件协议
- **Streaming_Response**: 流式响应，逐块返回内容而非一次性返回
- **Tool_Call_Event**: 工具调用事件，Agent 执行工具时产生的状态更新
- **Event_Subscription**: 事件订阅，客户端监听服务器推送的特定事件类型
- **Typing_Indicator**: 打字指示器，显示 AI 正在生成回复的动画效果
- **Message_Chunk**: 消息块，流式传输中的单个内容片段

## Requirements

### Requirement 1: 流式响应显示优化

**User Story:** As a user, I want to see the AI's response appearing character by character in real-time, so that I don't have to wait for the complete response and can start reading immediately.

#### Acceptance Criteria

1. WHEN the AI starts generating a response, THE Frontend_App SHALL display a typing indicator immediately
2. WHEN a Message_Chunk is received, THE Frontend_App SHALL append it to the current message without flickering
3. WHILE streaming is in progress, THE Frontend_App SHALL display a pulsing cursor at the end of the message
4. WHEN streaming completes, THE Frontend_App SHALL remove the cursor and show the complete message
5. THE Frontend_App SHALL render Markdown content progressively as chunks arrive
6. IF streaming is interrupted, THEN THE Frontend_App SHALL display an error indicator and allow retry

### Requirement 2: 工具调用状态展示

**User Story:** As a user, I want to see what tools the AI is using to answer my question, so that I understand how the answer is being generated and can trust the response.

#### Acceptance Criteria

1. WHEN the Agent starts a tool call, THE Frontend_App SHALL display a tool card with the tool name and "执行中" status
2. WHILE a tool is executing, THE Frontend_App SHALL show a loading animation on the tool card
3. WHEN a tool call completes successfully, THE Frontend_App SHALL update the tool card to show "完成" status with a checkmark
4. IF a tool call fails, THEN THE Frontend_App SHALL show "失败" status with an error icon
5. THE Frontend_App SHALL display tool results in a collapsible section within the tool card
6. WHEN multiple tools are called, THE Frontend_App SHALL display them in chronological order

### Requirement 3: SSE 事件订阅机制

**User Story:** As a developer, I want a robust event subscription system, so that the frontend can reliably receive and process different types of server events.

#### Acceptance Criteria

1. THE Frontend_App SHALL establish SSE connection using the EventSource API or fetch with ReadableStream
2. THE Frontend_App SHALL handle the following event types:
   - `chunk`: 文本内容块
   - `tool_start`: 工具调用开始
   - `tool_end`: 工具调用结束
   - `meta`: 元数据（实体、引用等）
   - `error`: 错误信息
   - `done`: 流结束标记
3. WHEN connection is lost, THE Frontend_App SHALL attempt to reconnect with exponential backoff
4. THE Frontend_App SHALL properly close the connection when the user navigates away or starts a new question
5. IF the server sends an error event, THEN THE Frontend_App SHALL display the error message to the user

### Requirement 4: UI/UX 交互优化

**User Story:** As a user, I want a smooth and responsive chat interface, so that I can have a pleasant experience while asking medical questions.

#### Acceptance Criteria

1. THE Frontend_App SHALL auto-scroll to the latest message as new content arrives
2. WHEN the user scrolls up during streaming, THE Frontend_App SHALL pause auto-scroll
3. THE Frontend_App SHALL show a "scroll to bottom" button when the user is not at the bottom
4. THE Frontend_App SHALL support smooth animations for message appearance
5. THE Frontend_App SHALL disable the send button while a response is being generated
6. WHEN a message is being streamed, THE Frontend_App SHALL show a "stop generating" button

### Requirement 5: 消息状态管理

**User Story:** As a user, I want to see the status of my messages clearly, so that I know if my question was received and is being processed.

#### Acceptance Criteria

1. WHEN a user sends a message, THE Frontend_App SHALL immediately display it with a "sending" indicator
2. WHEN the server acknowledges the message, THE Frontend_App SHALL update the status to "sent"
3. WHILE waiting for a response, THE Frontend_App SHALL show a loading state for the assistant message
4. THE Frontend_App SHALL display timestamps for all messages
5. IF a message fails to send, THEN THE Frontend_App SHALL show a retry button

### Requirement 6: 后端流式 API 增强

**User Story:** As a developer, I want the backend to send structured streaming events, so that the frontend can properly display tool calls and intermediate states.

#### Acceptance Criteria

1. THE Backend_API SHALL send `tool_start` events when a tool call begins, including tool name and arguments
2. THE Backend_API SHALL send `tool_end` events when a tool call completes, including the result or error
3. THE Backend_API SHALL send `chunk` events for each text content piece
4. THE Backend_API SHALL send `meta` events with entities, citations, and response time at the end
5. THE Backend_API SHALL properly handle client disconnection and clean up resources
6. THE Backend_API SHALL support cancellation of ongoing requests

### Requirement 7: 错误处理和恢复

**User Story:** As a user, I want the system to handle errors gracefully, so that I can continue using the application even when something goes wrong.

#### Acceptance Criteria

1. IF the SSE connection fails, THEN THE Frontend_App SHALL display a connection error message
2. THE Frontend_App SHALL provide a "重试" button for failed requests
3. WHEN retrying a failed request, THE Frontend_App SHALL show a loading indicator
4. IF multiple retries fail, THEN THE Frontend_App SHALL suggest checking network connection
5. THE Frontend_App SHALL preserve the user's input when an error occurs

