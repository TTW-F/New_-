# Design Document: Frontend Streaming Optimization

## Overview

本设计文档描述智能医疗问答系统前端流式传输优化方案。采用 Vue 3 Composition API + SSE (Server-Sent Events) 实现实时流式响应显示和工具调用状态展示。

核心设计理念：
- **实时性**：逐字显示 AI 回复，提供即时反馈
- **可视化**：展示工具调用过程，增强用户信任
- **健壮性**：完善的错误处理和重连机制
- **流畅性**：平滑动画和智能滚动

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend App (Vue 3)                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Chat Component                      │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐      │   │
│  │  │ Message  │    │  Tool    │    │ Streaming│      │   │
│  │  │  List    │    │  Cards   │    │ Indicator│      │   │
│  │  └──────────┘    └──────────┘    └──────────┘      │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│  ┌────────────────────────┼────────────────────────────┐   │
│  │              SSE Event Handler                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ Chunk    │  │ Tool     │  │ Meta     │          │   │
│  │  │ Handler  │  │ Handler  │  │ Handler  │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                     SSE Connection
                            │
┌─────────────────────────────────────────────────────────────┐
│                     Backend API (FastAPI)                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Streaming Response Generator            │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ chunk    │  │tool_start│  │ tool_end │          │   │
│  │  │ events   │  │ events   │  │ events   │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                    MedicalAgent                             │
└─────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. SSE Event Types

```typescript
// 事件类型定义
interface ChunkEvent {
    type: 'chunk';
    content: string;      // 文本内容块
}

interface ToolStartEvent {
    type: 'tool_start';
    tool_id: string;      // 工具调用 ID
    tool_name: string;    // 工具名称
    arguments: object;    // 调用参数
}

interface ToolEndEvent {
    type: 'tool_end';
    tool_id: string;      // 工具调用 ID
    status: 'success' | 'error';
    result?: string;      // 执行结果
    error?: string;       // 错误信息
}

interface MetaEvent {
    type: 'meta';
    question_id: number;
    entities: Entity[];
    citations: Citation[];
    response_time_ms: number;
}

interface ErrorEvent {
    type: 'error';
    message: string;
    code?: string;
}

type SSEEvent = ChunkEvent | ToolStartEvent | ToolEndEvent | MetaEvent | ErrorEvent;
```

### 2. StreamingMessage State

```typescript
interface StreamingMessage {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    isStreaming: boolean;
    toolCalls: ToolCall[];
    entities: Entity[];
    citations: Citation[];
    responseTime?: number;
    error?: string;
    status: 'sending' | 'sent' | 'streaming' | 'complete' | 'error';
}

interface ToolCall {
    id: string;
    name: string;
    arguments: object;
    status: 'running' | 'success' | 'error';
    result?: string;
    error?: string;
    startTime: number;
    endTime?: number;
}
```

### 3. SSE Connection Manager

```javascript
class SSEConnectionManager {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.abortController = null;
        this.retryCount = 0;
        this.maxRetries = 3;
    }
    
    async connect(endpoint, body, handlers) {
        // 取消之前的连接
        this.abort();
        this.abortController = new AbortController();
        
        const response = await fetch(`${this.baseUrl}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
            signal: this.abortController.signal
        });
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        // 处理流式响应
        await this.processStream(reader, decoder, handlers);
    }
    
    async processStream(reader, decoder, handlers) {
        let buffer = '';
        
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || '';
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        handlers.onDone?.();
                        return;
                    }
                    try {
                        const event = JSON.parse(data);
                        this.dispatchEvent(event, handlers);
                    } catch (e) {
                        console.error('Parse error:', e);
                    }
                }
            }
        }
    }
    
    dispatchEvent(event, handlers) {
        switch (event.type) {
            case 'chunk':
                handlers.onChunk?.(event.content);
                break;
            case 'tool_start':
                handlers.onToolStart?.(event);
                break;
            case 'tool_end':
                handlers.onToolEnd?.(event);
                break;
            case 'meta':
                handlers.onMeta?.(event);
                break;
            case 'error':
                handlers.onError?.(event);
                break;
        }
    }
    
    abort() {
        if (this.abortController) {
            this.abortController.abort();
            this.abortController = null;
        }
    }
}
```

### 4. Message Component Structure

```html
<!-- 消息组件结构 -->
<div class="message message-assistant">
    <div class="message-avatar">...</div>
    <div class="message-content">
        <div class="message-header">
            <span class="message-sender">智医助手</span>
            <span class="message-time">刚刚</span>
            <span class="streaming-indicator" v-if="isStreaming">●</span>
        </div>
        
        <!-- 工具调用卡片 -->
        <div class="tool-cards" v-if="toolCalls.length > 0">
            <div class="tool-card" v-for="tool in toolCalls" 
                 :class="tool.status">
                <div class="tool-header">
                    <span class="tool-icon">🔧</span>
                    <span class="tool-name">{{ tool.name }}</span>
                    <span class="tool-status">
                        <span v-if="tool.status === 'running'" class="spinner"></span>
                        <span v-else-if="tool.status === 'success'">✓</span>
                        <span v-else>✗</span>
                    </span>
                </div>
                <div class="tool-result" v-if="tool.result">
                    {{ tool.result }}
                </div>
            </div>
        </div>
        
        <!-- 消息内容 -->
        <div class="message-body markdown-body" 
             :class="{ streaming: isStreaming }"
             v-html="renderedContent">
        </div>
        
        <!-- 实体和引用 -->
        <div class="message-meta" v-if="!isStreaming">
            ...
        </div>
    </div>
</div>
```

## Data Models

### Backend Event Format

```python
# 后端事件格式
class StreamEvent:
    """流式事件基类"""
    type: str

class ChunkEvent(StreamEvent):
    type: str = "chunk"
    content: str

class ToolStartEvent(StreamEvent):
    type: str = "tool_start"
    tool_id: str
    tool_name: str
    arguments: dict

class ToolEndEvent(StreamEvent):
    type: str = "tool_end"
    tool_id: str
    status: str  # "success" | "error"
    result: Optional[str]
    error: Optional[str]

class MetaEvent(StreamEvent):
    type: str = "meta"
    question_id: int
    entities: List[dict]
    citations: List[dict]
    response_time_ms: int
```

### Frontend State Management

```javascript
// Vue 3 响应式状态
const streamingState = reactive({
    isStreaming: false,
    currentMessageId: null,
    content: '',
    toolCalls: [],
    abortController: null,
    autoScroll: true,
    error: null
});
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Chunk Concatenation Integrity

*For any* sequence of chunk events received during streaming, the final displayed message content SHALL equal the concatenation of all chunk contents in the order they were received.

**Validates: Requirements 1.2, 1.5**

### Property 2: Tool Call Ordering Preservation

*For any* sequence of tool_start events, the tool cards SHALL be displayed in the same chronological order as the events were received.

**Validates: Requirements 2.6**

### Property 3: Event Type Handling Completeness

*For any* valid SSE event (chunk, tool_start, tool_end, meta, error, done), the event handler SHALL process it without throwing an exception and update the UI state accordingly.

**Validates: Requirements 3.2**

### Property 4: Message Timestamp Presence

*For any* message displayed in the chat interface, the message SHALL have a visible timestamp element.

**Validates: Requirements 5.4**

### Property 5: Backend Event Structure Validity

*For any* tool call made by the Agent, the backend SHALL emit exactly one tool_start event followed by exactly one tool_end event with matching tool_id.

**Validates: Requirements 6.1, 6.2**

## Error Handling

### 错误类型和处理策略

| 错误类型 | 前端处理 | 用户提示 |
|---------|---------|---------|
| 网络连接失败 | 显示错误，提供重试按钮 | "网络连接失败，请检查网络后重试" |
| SSE 解析错误 | 记录日志，继续处理 | 不显示（静默处理） |
| 服务器错误 | 显示错误消息 | 显示服务器返回的错误信息 |
| 请求超时 | 自动重试（最多3次） | "请求超时，正在重试..." |
| 用户取消 | 清理连接，保留已接收内容 | "已停止生成" |

### 重连策略

```javascript
const retryWithBackoff = async (fn, maxRetries = 3) => {
    for (let i = 0; i < maxRetries; i++) {
        try {
            return await fn();
        } catch (e) {
            if (i === maxRetries - 1) throw e;
            const delay = Math.min(1000 * Math.pow(2, i), 10000);
            await new Promise(r => setTimeout(r, delay));
        }
    }
};
```

## Testing Strategy

### 单元测试

1. **SSE Event Parser 测试**
   - 解析各种事件类型
   - 处理格式错误的数据
   - 处理不完整的数据块

2. **Message State 测试**
   - 状态转换正确性
   - 内容累积正确性
   - 工具调用状态更新

3. **UI Component 测试**
   - 工具卡片渲染
   - 流式指示器显示/隐藏
   - 滚动行为

### 属性测试 (Property-Based Testing)

使用 `fast-check` 库进行前端属性测试：

1. **Property 1**: Chunk 拼接完整性
   - 生成随机 chunk 序列，验证最终内容

2. **Property 2**: 工具调用顺序
   - 生成随机工具事件序列，验证显示顺序

3. **Property 3**: 事件处理完整性
   - 生成各种事件类型，验证处理不抛异常

### 集成测试

1. 完整流式问答流程
2. 工具调用显示流程
3. 错误恢复流程

## Implementation Notes

### 文件修改清单

```
frontend/
├── app.js           # 主要修改：SSE 处理、状态管理
├── styles.css       # 新增：工具卡片样式、流式动画
└── index.html       # 无需修改

api/
├── routers/qa.py    # 修改：增强流式事件格式
└── services/qa_service.py  # 修改：发送工具调用事件

medical_agent/
└── agent.py         # 修改：流式输出时发送工具事件
```

### 关键实现细节

1. **流式 Markdown 渲染**
```javascript
// 使用 marked 库进行增量渲染
const renderMarkdown = (text) => {
    if (!text) return '';
    // 处理不完整的 markdown（如未闭合的代码块）
    let safeText = text;
    const codeBlockCount = (text.match(/```/g) || []).length;
    if (codeBlockCount % 2 !== 0) {
        safeText += '\n```';  // 临时闭合
    }
    return marked.parse(safeText);
};
```

2. **智能滚动**
```javascript
const scrollToBottom = () => {
    if (!autoScroll.value) return;
    const container = document.querySelector('.chat-messages');
    if (container) {
        container.scrollTo({
            top: container.scrollHeight,
            behavior: 'smooth'
        });
    }
};

// 检测用户滚动
const handleScroll = (e) => {
    const { scrollTop, scrollHeight, clientHeight } = e.target;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
    autoScroll.value = isAtBottom;
};
```

3. **停止生成**
```javascript
const stopGenerating = () => {
    if (sseManager.abortController) {
        sseManager.abort();
        const msg = messages.value.find(m => m.isStreaming);
        if (msg) {
            msg.isStreaming = false;
            msg.status = 'complete';
        }
        isTyping.value = false;
    }
};
```

