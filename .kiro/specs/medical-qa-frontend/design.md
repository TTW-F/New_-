# 设计文档 - 医疗问答前端界面

## 概述

本文档描述医疗智能问答系统前端界面的设计方案。该系统采用 Vue 3 + TypeScript 技术栈,通过 SSE (Server-Sent Events) 实现与后端的实时流式通信,提供现代化、高质量的用户体验。

### 设计理念

**Purpose (目的):** 为医疗问答系统提供一个专业、可信、易用的界面,帮助用户快速获取医疗建议,同时清晰展示 Agent 的推理过程和信息来源。

**Tone (风格定位):** 医疗专业 + 现代科技感 - 采用"精致极简主义"(Refined Minimalism)美学,结合医疗行业的专业性和 AI 技术的未来感。界面以白色和浅蓝色为主色调,使用柔和的阴影和圆角营造信任感,同时通过精心设计的动画和层级展示体现技术的先进性。

**Differentiation (差异化):** 
1. **透明的 AI 思考过程** - 通过可视化展示 Agent 的工具调用和推理步骤,让用户理解回答的来源
2. **医疗级的信息层级** - 清晰区分 Agent 思考过程、工具结果和最终回答,避免信息混淆
3. **流畅的实时体验** - 真正的流式输出,逐字显示,配合精心设计的动画效果

**Key Visual Element (核心视觉元素):** 
- 使用"脉冲波纹"动画表示 Agent 思考
- 工具调用使用"卡片展开"动画
- 实体高亮使用"柔和发光"效果

## 架构设计

### 技术栈

- **框架:** Vue 3 (Composition API + `<script setup>`)
- **语言:** TypeScript
- **状态管理:** Pinia
- **路由:** Vue Router
- **HTTP 客户端:** Axios
- **SSE 客户端:** EventSource (原生) + 自定义封装
- **UI 组件库:** 自定义组件 (不使用第三方 UI 库,确保独特性)
- **样式:** SCSS + CSS Variables
- **动画:** CSS Animations + Vue Transition
- **Markdown 渲染:** markdown-it
- **代码高亮:** highlight.js
- **构建工具:** Vite

### 项目结构

```
frontend/
├── src/
│   ├── api/              # API 接口封装
│   │   ├── auth.ts       # 认证相关 API
│   │   ├── qa.ts         # 问答相关 API
│   │   ├── history.ts    # 历史记录 API
│   │   └── sse.ts        # SSE 客户端封装
│   ├── assets/           # 静态资源
│   │   ├── fonts/        # 字体文件
│   │   ├── images/       # 图片
│   │   └── styles/       # 全局样式
│   │       ├── variables.scss  # CSS 变量
│   │       ├── mixins.scss     # SCSS Mixins
│   │       └── global.scss     # 全局样式
│   ├── components/       # 组件
│   │   ├── chat/         # 聊天相关组件
│   │   │   ├── ChatContainer.vue      # 聊天容器
│   │   │   ├── MessageList.vue        # 消息列表
│   │   │   ├── MessageItem.vue        # 单条消息
│   │   │   ├── UserMessage.vue        # 用户消息
│   │   │   ├── AssistantMessage.vue   # AI 回答
│   │   │   ├── ToolCallCard.vue       # 工具调用卡片
│   │   │   ├── EntityHighlight.vue    # 实体高亮
│   │   │   └── InputBox.vue           # 输入框
│   │   ├── sidebar/      # 侧边栏组件
│   │   │   ├── Sidebar.vue            # 侧边栏容器
│   │   │   ├── SessionList.vue        # 会话列表
│   │   │   └── SessionItem.vue        # 会话项
│   │   ├── auth/         # 认证组件
│   │   │   ├── LoginForm.vue          # 登录表单
│   │   │   └── RegisterForm.vue       # 注册表单
│   │   ├── common/       # 通用组件
│   │   │   ├── Button.vue             # 按钮
│   │   │   ├── Loading.vue            # 加载指示器
│   │   │   ├── Toast.vue              # 提示消息
│   │   │   └── Modal.vue              # 模态框
│   │   └── renderers/    # 内容渲染器
│   │       ├── MarkdownRenderer.vue   # Markdown 渲染
│   │       ├── DiseaseCard.vue        # 疾病卡片
│   │       ├── DrugCard.vue           # 药品卡片
│   │       └── TreatmentPlan.vue      # 治疗方案
│   ├── composables/      # 组合式函数
│   │   ├── useSSE.ts     # SSE 连接管理
│   │   ├── useChat.ts    # 聊天逻辑
│   │   ├── useAuth.ts    # 认证逻辑
│   │   └── useSession.ts # 会话管理
│   ├── stores/           # Pinia 状态管理
│   │   ├── auth.ts       # 认证状态
│   │   ├── chat.ts       # 聊天状态
│   │   └── ui.ts         # UI 状态
│   ├── types/            # TypeScript 类型定义
│   │   ├── api.ts        # API 类型
│   │   ├── chat.ts       # 聊天类型
│   │   └── sse.ts        # SSE 事件类型
│   ├── utils/            # 工具函数
│   │   ├── format.ts     # 格式化工具
│   │   ├── storage.ts    # 本地存储
│   │   └── validator.ts  # 验证工具
│   ├── views/            # 页面视图
│   │   ├── ChatView.vue  # 聊天页面
│   │   ├── LoginView.vue # 登录页面
│   │   └── NotFound.vue  # 404 页面
│   ├── App.vue           # 根组件
│   ├── main.ts           # 入口文件
│   └── router.ts         # 路由配置
├── public/               # 公共资源
├── index.html            # HTML 模板
├── vite.config.ts        # Vite 配置
├── tsconfig.json         # TypeScript 配置
└── package.json          # 依赖配置
```


## 组件设计

### 核心组件

#### 1. ChatContainer (聊天容器)

主聊天界面容器,负责整体布局和状态管理。

**Props:**
- 无

**State:**
- `currentSessionId`: 当前会话 ID
- `messages`: 消息列表
- `isStreaming`: 是否正在流式输出
- `isLoading`: 是否正在加载

**Methods:**
- `handleSendMessage(message: string)`: 发送消息
- `handleNewSession()`: 创建新会话
- `handleLoadSession(sessionId: string)`: 加载历史会话

#### 2. MessageItem (消息项)

单条消息的容器,根据消息类型渲染不同的子组件。

**Props:**
- `message`: Message 对象
- `isStreaming`: 是否正在流式输出

**Computed:**
- `messageType`: 消息类型 (user | assistant)
- `hasToolCalls`: 是否包含工具调用

#### 3. AssistantMessage (AI 回答)

渲染 AI 的回答内容,支持 Markdown 和实体高亮。

**Props:**
- `content`: 回答内容
- `entities`: 实体列表
- `isStreaming`: 是否正在流式输出
- `toolCalls`: 工具调用列表

**Features:**
- Markdown 渲染
- 实体高亮
- 打字机效果(流式输出时)
- 工具调用卡片展示

#### 4. ToolCallCard (工具调用卡片)

展示单个工具调用的详细信息。

**Props:**
- `toolCall`: ToolCall 对象
- `isExpanded`: 是否展开

**State:**
- `status`: 工具状态 (pending | running | success | error)

**Visual States:**
- **pending**: 灰色边框,等待图标
- **running**: 蓝色边框,脉冲动画
- **success**: 绿色边框,成功图标
- **error**: 红色边框,错误图标

#### 5. InputBox (输入框)

用户输入区域,支持多行输入和快捷键。

**Props:**
- `disabled`: 是否禁用
- `placeholder`: 占位符文本

**Events:**
- `@submit`: 提交消息

**Features:**
- 自动高度调整
- Enter 发送,Shift+Enter 换行
- 字符计数(最大 1000 字符)
- 防抖处理

#### 6. Sidebar (侧边栏)

显示会话列表和用户信息。

**Props:**
- `isOpen`: 是否打开(移动端)

**Features:**
- 会话列表
- 新建会话按钮
- 用户信息
- 登录/登出


## 数据模型

### TypeScript 类型定义

```typescript
// types/chat.ts

/** 消息类型 */
export type MessageRole = 'user' | 'assistant' | 'system';

/** 消息状态 */
export type MessageStatus = 'sending' | 'sent' | 'streaming' | 'completed' | 'error';

/** 工具调用状态 */
export type ToolCallStatus = 'pending' | 'running' | 'success' | 'error';

/** 实体类型 */
export type EntityType = 'Disease' | 'Symptom' | 'Drug' | 'Treatment';

/** 实体 */
export interface Entity {
  type: EntityType;
  name: string;
  score?: number;
}

/** 工具调用 */
export interface ToolCall {
  id: string;
  tool_id: string;
  tool_name: string;
  arguments: Record<string, any>;
  result?: string;
  error?: string;
  status: ToolCallStatus;
  entities?: Entity[];
  timestamp?: string;
}

/** 消息 */
export interface Message {
  id: string;
  role: MessageRole;
  content: string;
  status: MessageStatus;
  toolCalls?: ToolCall[];
  entities?: Entity[];
  timestamp: string;
  sessionId: string;
}

/** 会话 */
export interface Session {
  id: string;
  title: string;
  createdAt: string;
  updatedAt: string;
  messageCount: number;
}

// types/sse.ts

/** SSE 事件类型 */
export type SSEEventType = 
  | 'tool_start' 
  | 'tool_end' 
  | 'chunk' 
  | 'meta' 
  | 'error';

/** SSE 事件基类 */
export interface SSEEvent {
  type: SSEEventType;
}

/** 工具开始事件 */
export interface ToolStartEvent extends SSEEvent {
  type: 'tool_start';
  tool_id: string;
  tool_name: string;
  arguments: Record<string, any>;
}

/** 工具结束事件 */
export interface ToolEndEvent extends SSEEvent {
  type: 'tool_end';
  tool_id: string;
  tool_name: string;
  status: 'success' | 'error';
  result?: string;
  error?: string;
  entities?: Entity[];
}

/** 内容块事件 */
export interface ChunkEvent extends SSEEvent {
  type: 'chunk';
  content: string;
}

/** 元数据事件 */
export interface MetaEvent extends SSEEvent {
  type: 'meta';
  question_id: string;
  session_id: string;
  response_time_ms: number;
  entities: Entity[];
  tool_calls: any[];
  citations: any[];
}

/** 错误事件 */
export interface ErrorEvent extends SSEEvent {
  type: 'error';
  message: string;
}

/** SSE 事件联合类型 */
export type SSEEventData = 
  | ToolStartEvent 
  | ToolEndEvent 
  | ChunkEvent 
  | MetaEvent 
  | ErrorEvent;

// types/api.ts

/** 问答请求 */
export interface QARequest {
  question: string;
  session_id?: string;
}

/** 问答响应 */
export interface QAResponse {
  question_id: string;
  session_id: string;
  question: string;
  answer: string;
  entities: Entity[];
  citations: any[];
  response_time_ms: number;
}

/** 登录请求 */
export interface LoginRequest {
  username: string;
  password: string;
}

/** 登录响应 */
export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: number;
    username: string;
    email: string;
  };
}
```


## API 集成设计

### SSE 客户端封装

```typescript
// api/sse.ts

import type { SSEEventData } from '@/types/sse';

export interface SSEOptions {
  url: string;
  onMessage: (event: SSEEventData) => void;
  onError?: (error: Error) => void;
  onOpen?: () => void;
  onClose?: () => void;
  headers?: Record<string, string>;
}

export class SSEClient {
  private eventSource: EventSource | null = null;
  private options: SSEOptions;
  
  constructor(options: SSEOptions) {
    this.options = options;
  }
  
  connect(): void {
    // 构建 URL (包含 query 参数)
    const url = new URL(this.options.url, window.location.origin);
    
    // 创建 EventSource
    this.eventSource = new EventSource(url.toString());
    
    // 监听消息
    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.close();
        return;
      }
      
      try {
        const data: SSEEventData = JSON.parse(event.data);
        this.options.onMessage(data);
      } catch (error) {
        console.error('Failed to parse SSE data:', error);
      }
    };
    
    // 监听打开
    this.eventSource.onopen = () => {
      this.options.onOpen?.();
    };
    
    // 监听错误
    this.eventSource.onerror = (error) => {
      this.options.onError?.(new Error('SSE connection error'));
      this.close();
    };
  }
  
  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.options.onClose?.();
    }
  }
  
  isConnected(): boolean {
    return this.eventSource !== null && 
           this.eventSource.readyState === EventSource.OPEN;
  }
}

// 使用示例
export function createSSEConnection(
  question: string,
  sessionId: string | undefined,
  onMessage: (event: SSEEventData) => void
): SSEClient {
  const token = localStorage.getItem('access_token');
  
  const client = new SSEClient({
    url: `/api/v1/qa/stream?question=${encodeURIComponent(question)}&session_id=${sessionId || ''}`,
    onMessage,
    onError: (error) => {
      console.error('SSE Error:', error);
    },
    headers: token ? {
      'Authorization': `Bearer ${token}`
    } : undefined
  });
  
  return client;
}
```

### HTTP API 封装

```typescript
// api/qa.ts

import axios from 'axios';
import type { QARequest, QAResponse } from '@/types/api';

const apiClient = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// 请求拦截器 - 添加 Token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截器 - 处理错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token 过期,跳转登录
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/** 同步问答 API */
export async function askQuestion(request: QARequest): Promise<QAResponse> {
  const response = await apiClient.post<QAResponse>('/qa', request);
  return response.data;
}

/** 清空会话 */
export async function clearSession(sessionId: string): Promise<void> {
  await apiClient.post('/qa/clear', null, {
    params: { session_id: sessionId }
  });
}

/** 删除会话 */
export async function deleteSession(sessionId: string): Promise<void> {
  await apiClient.delete(`/qa/session/${sessionId}`);
}

// api/auth.ts

import type { LoginRequest, LoginResponse } from '@/types/api';

/** 用户登录 */
export async function login(request: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/login', request);
  return response.data;
}

/** 用户注册 */
export async function register(request: LoginRequest): Promise<LoginResponse> {
  const response = await apiClient.post<LoginResponse>('/auth/register', request);
  return response.data;
}

/** 用户登出 */
export async function logout(): Promise<void> {
  await apiClient.post('/auth/logout');
}
```


## 状态管理设计

### Chat Store (聊天状态)

```typescript
// stores/chat.ts

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { Message, Session, ToolCall } from '@/types/chat';
import { v4 as uuidv4 } from 'uuid';

export const useChatStore = defineStore('chat', () => {
  // State
  const currentSessionId = ref<string | null>(null);
  const sessions = ref<Map<string, Session>>(new Map());
  const messages = ref<Map<string, Message[]>>(new Map());
  const isStreaming = ref(false);
  const currentStreamingMessageId = ref<string | null>(null);
  
  // Getters
  const currentSession = computed(() => {
    if (!currentSessionId.value) return null;
    return sessions.value.get(currentSessionId.value) || null;
  });
  
  const currentMessages = computed(() => {
    if (!currentSessionId.value) return [];
    return messages.value.get(currentSessionId.value) || [];
  });
  
  // Actions
  function createSession(): string {
    const sessionId = uuidv4().substring(0, 16);
    const session: Session = {
      id: sessionId,
      title: '新对话',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      messageCount: 0
    };
    
    sessions.value.set(sessionId, session);
    messages.value.set(sessionId, []);
    currentSessionId.value = sessionId;
    
    return sessionId;
  }
  
  function switchSession(sessionId: string): void {
    if (sessions.value.has(sessionId)) {
      currentSessionId.value = sessionId;
    }
  }
  
  function addUserMessage(content: string): Message {
    if (!currentSessionId.value) {
      createSession();
    }
    
    const message: Message = {
      id: uuidv4(),
      role: 'user',
      content,
      status: 'sent',
      timestamp: new Date().toISOString(),
      sessionId: currentSessionId.value!
    };
    
    const sessionMessages = messages.value.get(currentSessionId.value!) || [];
    sessionMessages.push(message);
    messages.value.set(currentSessionId.value!, sessionMessages);
    
    // 更新会话标题(使用第一条消息)
    const session = sessions.value.get(currentSessionId.value!);
    if (session && session.messageCount === 0) {
      session.title = content.substring(0, 30) + (content.length > 30 ? '...' : '');
    }
    session!.messageCount++;
    session!.updatedAt = new Date().toISOString();
    
    return message;
  }
  
  function startAssistantMessage(): Message {
    if (!currentSessionId.value) {
      throw new Error('No active session');
    }
    
    const message: Message = {
      id: uuidv4(),
      role: 'assistant',
      content: '',
      status: 'streaming',
      toolCalls: [],
      entities: [],
      timestamp: new Date().toISOString(),
      sessionId: currentSessionId.value
    };
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    sessionMessages.push(message);
    messages.value.set(currentSessionId.value, sessionMessages);
    
    currentStreamingMessageId.value = message.id;
    isStreaming.value = true;
    
    return message;
  }
  
  function appendContent(content: string): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      message.content += content;
    }
  }
  
  function addToolCall(toolCall: Partial<ToolCall>): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      if (!message.toolCalls) {
        message.toolCalls = [];
      }
      
      const existingToolCall = message.toolCalls.find(tc => tc.tool_id === toolCall.tool_id);
      
      if (existingToolCall) {
        // 更新现有工具调用
        Object.assign(existingToolCall, toolCall);
      } else {
        // 添加新工具调用
        message.toolCalls.push({
          id: uuidv4(),
          tool_id: toolCall.tool_id!,
          tool_name: toolCall.tool_name!,
          arguments: toolCall.arguments || {},
          status: toolCall.status || 'pending',
          result: toolCall.result,
          error: toolCall.error,
          entities: toolCall.entities
        });
      }
    }
  }
  
  function updateToolCallStatus(
    toolId: string, 
    status: ToolCallStatus, 
    result?: string, 
    error?: string,
    entities?: Entity[]
  ): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message && message.toolCalls) {
      const toolCall = message.toolCalls.find(tc => tc.tool_id === toolId);
      if (toolCall) {
        toolCall.status = status;
        if (result !== undefined) toolCall.result = result;
        if (error !== undefined) toolCall.error = error;
        if (entities !== undefined) toolCall.entities = entities;
      }
    }
  }
  
  function completeStreaming(entities?: Entity[]): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      message.status = 'completed';
      if (entities) {
        message.entities = entities;
      }
    }
    
    isStreaming.value = false;
    currentStreamingMessageId.value = null;
    
    // 更新会话
    const session = sessions.value.get(currentSessionId.value);
    if (session) {
      session.updatedAt = new Date().toISOString();
    }
  }
  
  function setError(error: string): void {
    if (!currentStreamingMessageId.value || !currentSessionId.value) return;
    
    const sessionMessages = messages.value.get(currentSessionId.value) || [];
    const message = sessionMessages.find(m => m.id === currentStreamingMessageId.value);
    
    if (message) {
      message.status = 'error';
      message.content = error;
    }
    
    isStreaming.value = false;
    currentStreamingMessageId.value = null;
  }
  
  function deleteSession(sessionId: string): void {
    sessions.value.delete(sessionId);
    messages.value.delete(sessionId);
    
    if (currentSessionId.value === sessionId) {
      currentSessionId.value = null;
    }
  }
  
  return {
    // State
    currentSessionId,
    sessions,
    messages,
    isStreaming,
    currentStreamingMessageId,
    
    // Getters
    currentSession,
    currentMessages,
    
    // Actions
    createSession,
    switchSession,
    addUserMessage,
    startAssistantMessage,
    appendContent,
    addToolCall,
    updateToolCallStatus,
    completeStreaming,
    setError,
    deleteSession
  };
});
```


## Composables 设计

### useChat (聊天逻辑)

```typescript
// composables/useChat.ts

import { ref } from 'vue';
import { useChatStore } from '@/stores/chat';
import { SSEClient } from '@/api/sse';
import type { SSEEventData } from '@/types/sse';

export function useChat() {
  const chatStore = useChatStore();
  const sseClient = ref<SSEClient | null>(null);
  const error = ref<string | null>(null);
  
  async function sendMessage(content: string): Promise<void> {
    try {
      error.value = null;
      
      // 添加用户消息
      chatStore.addUserMessage(content);
      
      // 开始 AI 回答
      chatStore.startAssistantMessage();
      
      // 创建 SSE 连接
      const sessionId = chatStore.currentSessionId;
      
      sseClient.value = new SSEClient({
        url: `/api/v1/qa/stream`,
        onMessage: handleSSEMessage,
        onError: handleSSEError,
        onClose: handleSSEClose
      });
      
      // 发送请求(通过 POST body)
      await fetch('/api/v1/qa/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token') || ''}`
        },
        body: JSON.stringify({
          question: content,
          session_id: sessionId
        })
      }).then(response => {
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        // 读取 SSE 流
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();
        
        function readStream(): Promise<void> {
          return reader!.read().then(({ done, value }) => {
            if (done) {
              handleSSEClose();
              return;
            }
            
            const text = decoder.decode(value, { stream: true });
            const lines = text.split('\n');
            
            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.substring(6);
                
                if (data === '[DONE]') {
                  handleSSEClose();
                  return;
                }
                
                try {
                  const event: SSEEventData = JSON.parse(data);
                  handleSSEMessage(event);
                } catch (e) {
                  console.error('Failed to parse SSE data:', e);
                }
              }
            }
            
            return readStream();
          });
        }
        
        return readStream();
      });
      
    } catch (err) {
      const message = err instanceof Error ? err.message : '发送消息失败';
      error.value = message;
      chatStore.setError(message);
    }
  }
  
  function handleSSEMessage(event: SSEEventData): void {
    switch (event.type) {
      case 'tool_start':
        chatStore.addToolCall({
          tool_id: event.tool_id,
          tool_name: event.tool_name,
          arguments: event.arguments,
          status: 'running'
        });
        break;
        
      case 'tool_end':
        chatStore.updateToolCallStatus(
          event.tool_id,
          event.status === 'success' ? 'success' : 'error',
          event.result,
          event.error,
          event.entities
        );
        break;
        
      case 'chunk':
        chatStore.appendContent(event.content);
        break;
        
      case 'meta':
        chatStore.completeStreaming(event.entities);
        break;
        
      case 'error':
        error.value = event.message;
        chatStore.setError(event.message);
        break;
    }
  }
  
  function handleSSEError(err: Error): void {
    error.value = err.message;
    chatStore.setError('连接中断,请重试');
  }
  
  function handleSSEClose(): void {
    sseClient.value = null;
  }
  
  function stopStreaming(): void {
    if (sseClient.value) {
      sseClient.value.close();
      sseClient.value = null;
    }
    chatStore.completeStreaming();
  }
  
  return {
    sendMessage,
    stopStreaming,
    error
  };
}
```

### useAuth (认证逻辑)

```typescript
// composables/useAuth.ts

import { ref, computed } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { login as apiLogin, register as apiRegister, logout as apiLogout } from '@/api/auth';
import type { LoginRequest } from '@/types/api';

export function useAuth() {
  const authStore = useAuthStore();
  const loading = ref(false);
  const error = ref<string | null>(null);
  
  const isAuthenticated = computed(() => authStore.isAuthenticated);
  const currentUser = computed(() => authStore.user);
  
  async function login(credentials: LoginRequest): Promise<boolean> {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await apiLogin(credentials);
      
      authStore.setToken(response.access_token);
      authStore.setUser(response.user);
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '登录失败';
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  async function register(credentials: LoginRequest): Promise<boolean> {
    try {
      loading.value = true;
      error.value = null;
      
      const response = await apiRegister(credentials);
      
      authStore.setToken(response.access_token);
      authStore.setUser(response.user);
      
      return true;
    } catch (err) {
      error.value = err instanceof Error ? err.message : '注册失败';
      return false;
    } finally {
      loading.value = false;
    }
  }
  
  async function logout(): Promise<void> {
    try {
      await apiLogout();
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      authStore.clearAuth();
    }
  }
  
  return {
    isAuthenticated,
    currentUser,
    loading,
    error,
    login,
    register,
    logout
  };
}
```


## 视觉设计规范

### 设计系统

#### 颜色方案

```scss
// assets/styles/variables.scss

:root {
  // 主色调 - 医疗蓝
  --color-primary: #2563eb;        // 主蓝色
  --color-primary-light: #60a5fa;  // 浅蓝色
  --color-primary-dark: #1e40af;   // 深蓝色
  --color-primary-alpha: rgba(37, 99, 235, 0.1);
  
  // 辅助色
  --color-success: #10b981;        // 成功绿
  --color-warning: #f59e0b;        // 警告橙
  --color-error: #ef4444;          // 错误红
  --color-info: #3b82f6;           // 信息蓝
  
  // 中性色
  --color-bg-primary: #ffffff;     // 主背景
  --color-bg-secondary: #f8fafc;   // 次背景
  --color-bg-tertiary: #f1f5f9;    // 三级背景
  --color-bg-hover: #e2e8f0;       // 悬停背景
  
  --color-text-primary: #0f172a;   // 主文本
  --color-text-secondary: #475569; // 次文本
  --color-text-tertiary: #94a3b8;  // 三级文本
  --color-text-disabled: #cbd5e1;  // 禁用文本
  
  --color-border: #e2e8f0;         // 边框
  --color-border-light: #f1f5f9;   // 浅边框
  --color-border-dark: #cbd5e1;    // 深边框
  
  // 实体颜色
  --color-entity-disease: #dc2626;    // 疾病 - 红色
  --color-entity-symptom: #ea580c;    // 症状 - 橙色
  --color-entity-drug: #7c3aed;       // 药品 - 紫色
  --color-entity-treatment: #059669;  // 治疗 - 绿色
  
  // 工具状态颜色
  --color-tool-pending: #94a3b8;   // 等待
  --color-tool-running: #3b82f6;   // 运行中
  --color-tool-success: #10b981;   // 成功
  --color-tool-error: #ef4444;     // 错误
  
  // 阴影
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
  
  // 圆角
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --radius-full: 9999px;
  
  // 间距
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  --spacing-2xl: 48px;
  
  // 过渡
  --transition-fast: 150ms ease;
  --transition-base: 250ms ease;
  --transition-slow: 350ms ease;
  
  // Z-index
  --z-dropdown: 1000;
  --z-modal: 2000;
  --z-toast: 3000;
  --z-tooltip: 4000;
}

// 暗色模式
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #0f172a;
    --color-bg-secondary: #1e293b;
    --color-bg-tertiary: #334155;
    --color-bg-hover: #475569;
    
    --color-text-primary: #f1f5f9;
    --color-text-secondary: #cbd5e1;
    --color-text-tertiary: #94a3b8;
    --color-text-disabled: #64748b;
    
    --color-border: #334155;
    --color-border-light: #1e293b;
    --color-border-dark: #475569;
  }
}
```

#### 字体系统

```scss
// 字体定义
:root {
  // 标题字体 - 使用 Outfit (现代几何无衬线)
  --font-display: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
  
  // 正文字体 - 使用 Inter (优秀的可读性)
  --font-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  
  // 等宽字体 - 用于代码
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  // 字体大小
  --text-xs: 0.75rem;    // 12px
  --text-sm: 0.875rem;   // 14px
  --text-base: 1rem;     // 16px
  --text-lg: 1.125rem;   // 18px
  --text-xl: 1.25rem;    // 20px
  --text-2xl: 1.5rem;    // 24px
  --text-3xl: 1.875rem;  // 30px
  --text-4xl: 2.25rem;   // 36px
  
  // 行高
  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;
  
  // 字重
  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;
}

// 字体导入
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Inter:wght@400;500;600;700&display=swap');
```

#### 动画效果

```scss
// assets/styles/animations.scss

// 淡入
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

// 从下滑入
@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

// 从右滑入
@keyframes slideInRight {
  from {
    opacity: 0;
    transform: translateX(20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

// 脉冲动画 (用于 Agent 思考)
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

// 波纹扩散 (用于工具调用)
@keyframes ripple {
  0% {
    transform: scale(0.8);
    opacity: 1;
  }
  100% {
    transform: scale(2);
    opacity: 0;
  }
}

// 打字光标闪烁
@keyframes blink {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0;
  }
}

// 加载旋转
@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 实体高亮发光
@keyframes glow {
  0%, 100% {
    box-shadow: 0 0 5px currentColor;
  }
  50% {
    box-shadow: 0 0 10px currentColor;
  }
}

// 工具卡片展开
@keyframes expandCard {
  from {
    max-height: 0;
    opacity: 0;
  }
  to {
    max-height: 500px;
    opacity: 1;
  }
}
```


## 正确性属性

*属性是一个特征或行为,应该在系统的所有有效执行中保持为真 - 本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### 属性 1: SSE 连接管理

*对于任何*用户提交的问题,系统应该建立到 `/api/v1/qa/stream` 的 SSE 连接,并在接收到 `[DONE]` 标记后正确关闭连接。

**验证需求: 2.1, 2.4**

### 属性 2: 流式内容追加

*对于任何*接收到的 `chunk` 事件,系统应该将内容实时追加到当前消息的末尾,不丢失任何内容块。

**验证需求: 2.2**

### 属性 3: 工具调用状态管理

*对于任何*工具调用,系统应该正确处理 `tool_start` 和 `tool_end` 事件,并维护工具状态从 pending → running → success/error 的转换。

**验证需求: 3.1, 3.2**

### 属性 4: 实体高亮一致性

*对于任何*包含医疗实体的回答文本,系统应该根据实体类型(疾病/症状/药品/治疗)应用对应的颜色高亮,且同类型实体使用相同颜色。

**验证需求: 5.2, 5.3, 5.4, 5.5**

### 属性 5: Session ID 唯一性

*对于任何*新创建的会话,系统应该生成唯一的 session_id,且不与现有会话 ID 冲突。

**验证需求: 6.1**

### 属性 6: 会话切换一致性

*对于任何*用户选择的历史会话,系统应该加载该会话的完整对话记录,且消息顺序与原始顺序一致。

**验证需求: 6.4**

### 属性 7: Token 认证传递

*对于任何*需要认证的 API 请求,如果用户已登录,系统应该在请求头中包含有效的 Authorization Token。

**验证需求: 7.3**

### 属性 8: 错误处理完整性

*对于任何*类型的错误(SSE 错误、网络错误、服务错误),系统应该显示相应的错误提示,并提供重试选项。

**验证需求: 2.5, 8.1, 8.2, 8.3, 8.4**

### 属性 9: 响应式布局适配

*对于任何*视口宽度,系统应该应用对应的布局样式:桌面端(>1024px)完整布局,平板端(768-1024px)调整布局,移动端(<768px)单列布局。

**验证需求: 10.1, 10.2, 10.3**

### 属性 10: Markdown 渲染正确性

*对于任何*包含 Markdown 语法的文本内容,系统应该正确渲染为对应的 HTML 元素(标题、列表、表格、代码块等)。

**验证需求: 12.1, 12.2, 12.3**

### 属性 11: 工具结果渲染分发

*对于任何*工具调用结果,系统应该根据工具类型选择对应的渲染组件(疾病卡片、药品卡片、治疗方案列表等)。

**验证需求: 4.1, 4.2, 4.3, 4.4**

### 属性 12: 加载状态可见性

*对于任何*异步操作(提交问题、等待响应、工具调用),系统应该显示对应的加载指示器或动画,直到操作完成。

**验证需求: 9.1, 9.2, 9.3**

### 属性 13: 防抖输入处理

*对于任何*用户输入事件,系统应该应用防抖处理,在用户停止输入后的指定延迟(如 300ms)后才触发处理逻辑。

**验证需求: 11.4**

### 属性 14: 工具结果截断

*对于任何*超过指定长度(如 500 字符)的工具结果,系统应该进行截断显示,并提供"展开"选项查看完整内容。

**验证需求: 11.3**


## 错误处理

### 错误类型

1. **网络错误**
   - SSE 连接失败
   - HTTP 请求超时
   - 网络断开

2. **认证错误**
   - Token 过期
   - 未授权访问
   - 登录失败

3. **业务错误**
   - 后端服务不可用
   - 工具调用失败
   - 数据验证失败

4. **客户端错误**
   - 浏览器不支持 SSE
   - 本地存储不可用
   - 内存不足

### 错误处理策略

```typescript
// utils/error-handler.ts

export interface ErrorContext {
  type: 'network' | 'auth' | 'business' | 'client';
  message: string;
  code?: string;
  retryable: boolean;
  action?: () => void;
}

export function handleError(error: any): ErrorContext {
  // 网络错误
  if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
    return {
      type: 'network',
      message: '网络连接超时,请检查网络后重试',
      retryable: true
    };
  }
  
  // 认证错误
  if (error.response?.status === 401) {
    return {
      type: 'auth',
      message: '登录已过期,请重新登录',
      retryable: false,
      action: () => {
        localStorage.removeItem('access_token');
        window.location.href = '/login';
      }
    };
  }
  
  // 服务不可用
  if (error.response?.status === 503) {
    return {
      type: 'business',
      message: '服务暂时不可用,请稍后重试',
      retryable: true
    };
  }
  
  // 默认错误
  return {
    type: 'business',
    message: error.message || '操作失败,请重试',
    retryable: true
  };
}
```

### Toast 通知系统

```typescript
// composables/useToast.ts

import { ref } from 'vue';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration: number;
}

const toasts = ref<Toast[]>([]);

export function useToast() {
  function show(type: ToastType, message: string, duration = 3000): void {
    const id = Date.now().toString();
    const toast: Toast = { id, type, message, duration };
    
    toasts.value.push(toast);
    
    if (duration > 0) {
      setTimeout(() => {
        remove(id);
      }, duration);
    }
  }
  
  function remove(id: string): void {
    const index = toasts.value.findIndex(t => t.id === id);
    if (index > -1) {
      toasts.value.splice(index, 1);
    }
  }
  
  function success(message: string, duration?: number): void {
    show('success', message, duration);
  }
  
  function error(message: string, duration?: number): void {
    show('error', message, duration);
  }
  
  function warning(message: string, duration?: number): void {
    show('warning', message, duration);
  }
  
  function info(message: string, duration?: number): void {
    show('info', message, duration);
  }
  
  return {
    toasts,
    success,
    error,
    warning,
    info,
    remove
  };
}
```

## 测试策略

### 测试类型

本项目采用双重测试方法:

1. **单元测试** - 验证具体示例、边缘情况和错误条件
2. **属性测试** - 验证跨所有输入的通用属性

两者是互补的,都是全面覆盖所必需的。

### 单元测试

使用 Vitest 进行单元测试,重点测试:

- **组件渲染** - 测试组件在不同 props 下的渲染结果
- **用户交互** - 测试点击、输入等交互行为
- **状态管理** - 测试 Pinia store 的状态变化
- **API 调用** - 测试 API 函数的请求和响应处理
- **工具函数** - 测试格式化、验证等工具函数

示例:

```typescript
// components/chat/InputBox.test.ts

import { describe, it, expect, vi } from 'vitest';
import { mount } from '@vue/test-utils';
import InputBox from './InputBox.vue';

describe('InputBox', () => {
  it('应该在用户按下 Enter 时提交消息', async () => {
    const onSubmit = vi.fn();
    const wrapper = mount(InputBox, {
      props: { onSubmit }
    });
    
    const textarea = wrapper.find('textarea');
    await textarea.setValue('测试消息');
    await textarea.trigger('keydown.enter');
    
    expect(onSubmit).toHaveBeenCalledWith('测试消息');
  });
  
  it('应该在用户按下 Shift+Enter 时换行', async () => {
    const onSubmit = vi.fn();
    const wrapper = mount(InputBox, {
      props: { onSubmit }
    });
    
    const textarea = wrapper.find('textarea');
    await textarea.setValue('第一行');
    await textarea.trigger('keydown.enter', { shiftKey: true });
    
    expect(onSubmit).not.toHaveBeenCalled();
  });
  
  it('应该限制输入字符数为 1000', async () => {
    const wrapper = mount(InputBox);
    const textarea = wrapper.find('textarea');
    
    const longText = 'a'.repeat(1001);
    await textarea.setValue(longText);
    
    expect(textarea.element.value.length).toBeLessThanOrEqual(1000);
  });
});
```

### 属性测试

使用 fast-check 进行属性测试,验证通用属性:

```typescript
// stores/chat.test.ts

import { describe, it } from 'vitest';
import { fc } from 'fast-check';
import { setActivePinia, createPinia } from 'pinia';
import { useChatStore } from './chat';

describe('Chat Store Properties', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });
  
  it('属性 5: Session ID 唯一性', () => {
    fc.assert(
      fc.property(fc.nat(100), (count) => {
        const store = useChatStore();
        const sessionIds = new Set<string>();
        
        // 创建多个会话
        for (let i = 0; i < count; i++) {
          const id = store.createSession();
          sessionIds.add(id);
        }
        
        // 验证所有 ID 都是唯一的
        return sessionIds.size === count;
      }),
      { numRuns: 100 }
    );
  });
  
  it('属性 2: 流式内容追加', () => {
    fc.assert(
      fc.property(fc.array(fc.string()), (chunks) => {
        const store = useChatStore();
        store.createSession();
        store.addUserMessage('测试');
        store.startAssistantMessage();
        
        // 追加所有内容块
        for (const chunk of chunks) {
          store.appendContent(chunk);
        }
        
        // 验证最终内容等于所有块的拼接
        const message = store.currentMessages[store.currentMessages.length - 1];
        return message.content === chunks.join('');
      }),
      { numRuns: 100 }
    );
  });
});
```

### E2E 测试

使用 Playwright 进行端到端测试,测试关键用户流程:

```typescript
// e2e/chat-flow.spec.ts

import { test, expect } from '@playwright/test';

test('完整问答流程', async ({ page }) => {
  // 访问页面
  await page.goto('/');
  
  // 输入问题
  await page.fill('textarea[placeholder*="问题"]', '感冒有什么症状?');
  await page.click('button[type="submit"]');
  
  // 等待流式输出开始
  await expect(page.locator('.assistant-message')).toBeVisible();
  
  // 验证工具调用卡片出现
  await expect(page.locator('.tool-call-card')).toBeVisible();
  
  // 等待回答完成
  await expect(page.locator('.typing-cursor')).not.toBeVisible({ timeout: 30000 });
  
  // 验证实体高亮
  await expect(page.locator('.entity-highlight')).toHaveCount({ min: 1 });
  
  // 验证回答内容不为空
  const answerText = await page.locator('.assistant-message .content').textContent();
  expect(answerText).toBeTruthy();
  expect(answerText!.length).toBeGreaterThan(10);
});

test('SSE 连接错误处理', async ({ page }) => {
  // 模拟网络错误
  await page.route('**/api/v1/qa/stream', route => route.abort());
  
  await page.goto('/');
  await page.fill('textarea', '测试问题');
  await page.click('button[type="submit"]');
  
  // 验证错误提示出现
  await expect(page.locator('.toast.error')).toBeVisible();
  
  // 验证重试按钮存在
  await expect(page.locator('button:has-text("重试")')).toBeVisible();
});
```

### 测试配置

每个属性测试必须:
- 运行最少 100 次迭代(由于随机化)
- 引用其设计文档属性
- 使用标签格式: `Feature: medical-qa-frontend, Property {number}: {property_text}`

### 测试覆盖率目标

- 单元测试覆盖率: ≥ 80%
- 组件测试覆盖率: ≥ 90%
- 关键路径 E2E 测试: 100%


## 性能优化

### 关键性能指标

- **首屏渲染时间 (FCP)**: < 2 秒
- **可交互时间 (TTI)**: < 3 秒
- **流式输出延迟**: < 100ms
- **消息渲染时间**: < 50ms
- **内存占用**: < 100MB (1000 条消息)

### 优化策略

#### 1. 代码分割

```typescript
// router.ts

import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'chat',
      component: () => import('./views/ChatView.vue') // 懒加载
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('./views/LoginView.vue')
    }
  ]
});
```

#### 2. 虚拟滚动

```typescript
// components/chat/MessageList.vue

<template>
  <div class="message-list" ref="containerRef">
    <RecycleScroller
      :items="messages"
      :item-size="100"
      key-field="id"
      v-slot="{ item }"
    >
      <MessageItem :message="item" />
    </RecycleScroller>
  </div>
</template>

<script setup lang="ts">
import { RecycleScroller } from 'vue-virtual-scroller';
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css';
</script>
```

#### 3. 防抖和节流

```typescript
// utils/debounce.ts

export function debounce<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout> | null = null;
  
  return function(...args: Parameters<T>) {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }
    
    timeoutId = setTimeout(() => {
      fn(...args);
    }, delay);
  };
}

export function throttle<T extends (...args: any[]) => any>(
  fn: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCall = 0;
  
  return function(...args: Parameters<T>) {
    const now = Date.now();
    
    if (now - lastCall >= delay) {
      lastCall = now;
      fn(...args);
    }
  };
}
```

#### 4. 内容截断

```typescript
// utils/truncate.ts

export interface TruncateOptions {
  maxLength: number;
  suffix?: string;
}

export function truncateText(
  text: string,
  options: TruncateOptions
): { truncated: string; isTruncated: boolean } {
  const { maxLength, suffix = '...' } = options;
  
  if (text.length <= maxLength) {
    return { truncated: text, isTruncated: false };
  }
  
  return {
    truncated: text.substring(0, maxLength - suffix.length) + suffix,
    isTruncated: true
  };
}

export function truncateJSON(
  data: any,
  maxLength: number
): string {
  const json = JSON.stringify(data, null, 2);
  const { truncated, isTruncated } = truncateText(json, { maxLength });
  
  if (isTruncated) {
    return truncated + '\n\n[内容已截断,点击展开查看完整内容]';
  }
  
  return truncated;
}
```

#### 5. 缓存策略

```typescript
// utils/cache.ts

export class LRUCache<K, V> {
  private cache: Map<K, V>;
  private maxSize: number;
  
  constructor(maxSize: number) {
    this.cache = new Map();
    this.maxSize = maxSize;
  }
  
  get(key: K): V | undefined {
    if (!this.cache.has(key)) {
      return undefined;
    }
    
    // 移到最前面(最近使用)
    const value = this.cache.get(key)!;
    this.cache.delete(key);
    this.cache.set(key, value);
    
    return value;
  }
  
  set(key: K, value: V): void {
    // 如果已存在,先删除
    if (this.cache.has(key)) {
      this.cache.delete(key);
    }
    
    // 如果超过容量,删除最旧的
    if (this.cache.size >= this.maxSize) {
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    
    this.cache.set(key, value);
  }
  
  clear(): void {
    this.cache.clear();
  }
}

// 使用示例
const sessionCache = new LRUCache<string, Session>(50);
```

#### 6. 组件懒加载

```typescript
// components/chat/AssistantMessage.vue

<script setup lang="ts">
import { defineAsyncComponent } from 'vue';

// 懒加载 Markdown 渲染器
const MarkdownRenderer = defineAsyncComponent(() =>
  import('../renderers/MarkdownRenderer.vue')
);

// 懒加载工具卡片
const ToolCallCard = defineAsyncComponent(() =>
  import('./ToolCallCard.vue')
);
</script>
```

## 安全考虑

### XSS 防护

```typescript
// utils/sanitize.ts

import DOMPurify from 'dompurify';

export function sanitizeHTML(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'a', 'code', 'pre', 'blockquote', 'table', 'thead',
      'tbody', 'tr', 'th', 'td'
    ],
    ALLOWED_ATTR: ['href', 'class', 'id']
  });
}
```

### CSRF 防护

```typescript
// api/client.ts

// 从 meta 标签获取 CSRF Token
const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

apiClient.interceptors.request.use((config) => {
  if (csrfToken) {
    config.headers['X-CSRF-Token'] = csrfToken;
  }
  return config;
});
```

### 敏感信息保护

```typescript
// utils/storage.ts

// 不在 localStorage 中存储敏感信息
// Token 存储在 httpOnly cookie 中(由后端设置)

export function setSecureItem(key: string, value: string): void {
  // 使用 sessionStorage 而不是 localStorage
  sessionStorage.setItem(key, value);
}

export function getSecureItem(key: string): string | null {
  return sessionStorage.getItem(key);
}
```

## 可访问性

### ARIA 标签

```vue
<!-- components/chat/InputBox.vue -->

<template>
  <div class="input-box" role="region" aria-label="消息输入区域">
    <textarea
      v-model="message"
      :placeholder="placeholder"
      :disabled="disabled"
      aria-label="输入您的问题"
      aria-describedby="char-count"
      @keydown.enter.exact.prevent="handleSubmit"
    />
    
    <div id="char-count" class="char-count" aria-live="polite">
      {{ message.length }} / 1000
    </div>
    
    <button
      type="submit"
      :disabled="disabled || !message.trim()"
      aria-label="发送消息"
      @click="handleSubmit"
    >
      <span class="sr-only">发送</span>
      <SendIcon />
    </button>
  </div>
</template>
```

### 键盘导航

```typescript
// composables/useKeyboard.ts

export function useKeyboardNavigation() {
  function handleKeyDown(event: KeyboardEvent): void {
    // Esc 关闭模态框
    if (event.key === 'Escape') {
      // 关闭逻辑
    }
    
    // Tab 导航
    if (event.key === 'Tab') {
      // 焦点管理
    }
    
    // 方向键导航历史消息
    if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
      // 导航逻辑
    }
  }
  
  onMounted(() => {
    window.addEventListener('keydown', handleKeyDown);
  });
  
  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown);
  });
}
```

### 屏幕阅读器支持

```vue
<!-- components/chat/AssistantMessage.vue -->

<template>
  <div class="assistant-message" role="article" aria-label="AI 回答">
    <!-- 工具调用 -->
    <div
      v-for="tool in toolCalls"
      :key="tool.id"
      class="tool-call"
      role="status"
      :aria-label="`工具调用: ${tool.tool_name}, 状态: ${tool.status}`"
    >
      <!-- 工具内容 -->
    </div>
    
    <!-- 回答内容 -->
    <div class="content" role="region" aria-label="回答内容">
      <MarkdownRenderer :content="content" />
    </div>
    
    <!-- 流式输出指示器 -->
    <span
      v-if="isStreaming"
      class="typing-cursor"
      aria-live="polite"
      aria-label="正在输入"
    />
  </div>
</template>
```

## 部署配置

### Vite 构建配置

```typescript
// vite.config.ts

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import { resolve } from 'path';

export default defineConfig({
  plugins: [vue()],
  
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src')
    }
  },
  
  build: {
    target: 'es2015',
    outDir: 'dist',
    assetsDir: 'assets',
    
    // 代码分割
    rollupOptions: {
      output: {
        manualChunks: {
          'vue-vendor': ['vue', 'vue-router', 'pinia'],
          'markdown': ['markdown-it', 'highlight.js'],
          'utils': ['axios', 'dompurify']
        }
      }
    },
    
    // 压缩
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true,
        drop_debugger: true
      }
    }
  },
  
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
});
```

### 环境变量

```bash
# .env.production

VITE_API_BASE_URL=https://api.medical-qa.com
VITE_APP_TITLE=医疗智能问答系统
VITE_ENABLE_ANALYTICS=true
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name medical-qa.com;
    
    root /var/www/medical-qa/dist;
    index index.html;
    
    # Gzip 压缩
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # SPA 路由
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        
        # SSE 支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }
}
```

## 总结

本设计文档详细描述了医疗问答前端界面的完整设计方案,包括:

1. **架构设计** - Vue 3 + TypeScript + Pinia 技术栈
2. **组件设计** - 模块化、可复用的组件体系
3. **数据模型** - 完整的 TypeScript 类型定义
4. **API 集成** - SSE 流式通信和 HTTP API 封装
5. **状态管理** - Pinia store 设计
6. **视觉设计** - 医疗专业风格的设计系统
7. **正确性属性** - 14 个可测试的正确性属性
8. **错误处理** - 完善的错误处理和用户反馈机制
9. **测试策略** - 单元测试 + 属性测试 + E2E 测试
10. **性能优化** - 虚拟滚动、代码分割、缓存等优化策略
11. **安全考虑** - XSS/CSRF 防护、敏感信息保护
12. **可访问性** - ARIA 标签、键盘导航、屏幕阅读器支持
13. **部署配置** - Vite 构建和 Nginx 部署配置

该设计遵循 frontend-design skill 的要求,采用独特的视觉风格,避免通用 AI 美学,并与真实后端 API 完全对接,支持流式输出和 Agent 思考过程可视化。
