# 前端架构文档 (Frontend)

**最后更新**: 2026-03-25  
**框架**: Vue 3.4+ (Composition API)  
**入口文件**: `frontend/src/main.ts`

---

## 📋 目录

- [架构概览](#架构概览)
- [目录结构](#目录结构)
- [核心模块](#核心模块)
- [状态管理](#状态管理)
- [组件系统](#组件系统)
- [API通信](#api通信)
- [SSE流式通信](#sse流式通信)
- [路由系统](#路由系统)
- [工具函数](#工具函数)
- [样式系统](#样式系统)

---

## 🏗️ 架构概览

前端采用 Vue 3 + TypeScript + Pinia 的现代化架构：

```
┌─────────────────────────────────────────────────────────────┐
│                      视图层 (Views)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  ChatView.vue      - 聊天主界面                      │  │
│  │  LoginView.vue     - 登录页面                        │  │
│  │  NotFoundView.vue  - 404页面                         │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    组件层 (Components)                       │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  chat/          - 聊天相关组件                       │  │
│  │  auth/          - 认证相关组件                       │  │
│  │  common/        - 通用组件                           │  │
│  │  sidebar/       - 侧边栏组件                         │  │
│  │  renderers/     - 内容渲染器                         │  │
│  │  icons/         - 图标组件                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  状态管理层 (Pinia Stores)                   │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  authStore      - 认证状态 (用户、Token)            │  │
│  │  chatStore      - 聊天状态 (消息、会话)             │  │
│  │  uiStore        - UI状态 (侧边栏、主题)             │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    API通信层 (API Client)                    │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  client.ts      - HTTP客户端 (axios)                │  │
│  │  auth.ts        - 认证API                            │  │
│  │  qa.ts          - 问答API                            │  │
│  │  history.ts     - 历史API                            │  │
│  │  sse.ts         - SSE客户端                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
frontend/src/
├── api/                      # API通信层
│   ├── client.ts            # axios实例配置
│   ├── auth.ts              # 认证API (login, register, logout, me)
│   ├── qa.ts                # 问答API (askQuestion, clearSession)
│   ├── history.ts           # 历史API (getSessions, getHistory)
│   └── sse.ts               # SSE客户端类
│
├── components/               # 组件库
│   ├── auth/                # 认证组件
│   │   ├── LoginForm.vue    # 登录表单
│   │   └── RegisterForm.vue # 注册表单
│   │
│   ├── chat/                # 聊天组件
│   │   ├── ChatContainer.vue      # 聊天容器
│   │   ├── MessageList.vue        # 消息列表
│   │   ├── MessageItem.vue        # 消息项
│   │   ├── UserMessage.vue        # 用户消息
│   │   ├── AssistantMessage.vue   # 助手消息
│   │   ├── InputBox.vue           # 输入框
│   │   ├── ToolCallCard.vue       # 工具调用卡片
│   │   ├── TypingIndicator.vue    # 输入指示器
│   │   └── EntityHighlight.vue    # 实体高亮
│   │
│   ├── common/              # 通用组件
│   │   ├── Button.vue       # 按钮
│   │   ├── Modal.vue        # 模态框
│   │   ├── Toast.vue        # 提示消息
│   │   ├── Loading.vue      # 加载指示器
│   │   └── ConfirmDialog.vue # 确认对话框
│   │
│   ├── sidebar/             # 侧边栏组件
│   │   ├── Sidebar.vue      # 侧边栏容器
│   │   ├── SessionList.vue  # 会话列表
│   │   └── SessionItem.vue  # 会话项
│   │
│   ├── renderers/           # 内容渲染器
│   │   ├── MarkdownRenderer.vue   # Markdown渲染
│   │   ├── DiseaseCard.vue        # 疾病卡片
│   │   ├── DrugCard.vue           # 药品卡片
│   │   └── TreatmentPlan.vue      # 治疗方案
│   │
│   └── icons/               # 图标组件
│       ├── IconBase.vue     # 图标基础组件
│       ├── IconSend.vue     # 发送图标
│       ├── IconRobot.vue    # 机器人图标
│       ├── IconTool.vue     # 工具图标
│       └── index.ts         # 图标导出
│
├── composables/              # 组合式函数
│   ├── useAuth.ts           # 认证逻辑
│   ├── useChat.ts           # 聊天逻辑
│   ├── useToast.ts          # 提示消息
│   └── useConfirm.ts        # 确认对话框
│
├── stores/                   # Pinia状态管理
│   ├── auth.ts              # 认证状态
│   ├── chat.ts              # 聊天状态
│   └── ui.ts                # UI状态
│
├── types/                    # TypeScript类型定义
│   ├── api.ts               # API类型
│   ├── chat.ts              # 聊天类型
│   └── sse.ts               # SSE类型
│
├── utils/                    # 工具函数
│   ├── cache.ts             # 缓存工具
│   ├── debounce.ts          # 防抖函数
│   ├── error-handler.ts     # 错误处理
│   ├── format.ts            # 格式化工具
│   ├── sanitize.ts          # 输入清理
│   ├── storage.ts           # 本地存储
│   └── validator.ts         # 验证工具
│
├── views/                    # 页面视图
│   ├── HomeView.vue         # 首页（系统介绍）
│   ├── ChatView.vue         # 聊天页面
│   ├── HistoryView.vue      # 历史记录页面
│   ├── KnowledgeView.vue    # 知识库页面
│   ├── ProfileView.vue      # 个人中心页面
│   ├── AdminView.vue        # 管理后台页面
│   ├── LoginView.vue        # 登录页面
│   └── NotFound.vue         # 404页面
│
├── router/                   # 路由配置
│   └── index.ts             # 路由定义
│
├── assets/                   # 静态资源
│   └── styles/              # 样式文件
│       ├── global.scss      # 全局样式
│       ├── variables.scss   # 变量定义
│       ├── animations.scss  # 动画效果
│       └── fixes.scss       # 样式修复
│
├── App.vue                   # 根组件
└── main.ts                   # 应用入口
```

---

## 🔑 核心模块

### 1. 应用入口 (main.ts)

**职责**: 初始化Vue应用、注册插件、挂载应用

```typescript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.use(ElementPlus)

app.mount('#app')
```

### 2. 根组件 (App.vue)

**职责**: 应用布局、全局组件、路由视图

```vue
<template>
  <div id="app" :class="{ 'dark-theme': isDark }">
    <router-view />
    <Toast />
    <ConfirmDialog />
  </div>
</template>
```

---

## � 状态管理

### 1. 认证状态 (stores/auth.ts)

**职责**: 管理用户登录状态、Token、用户信息

**状态**:
```typescript
interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  loading: boolean
}
```

**Actions**:
```typescript
// 登录
async login(credentials: LoginRequest): Promise<void>

// 注册
async register(userData: RegisterRequest): Promise<void>

// 登出
async logout(): Promise<void>

// 获取当前用户
async fetchCurrentUser(): Promise<void>

// 初始化认证状态
async initAuth(): Promise<void>
```

**使用示例**:
```typescript
import { useAuthStore } from '@/stores/auth'

const authStore = useAuthStore()

// 登录
await authStore.login({ username: 'user', password: 'pass' })

// 检查认证状态
if (authStore.isAuthenticated) {
  console.log('已登录:', authStore.user)
}
```

### 2. 聊天状态 (stores/chat.ts)

**职责**: 管理聊天消息、会话、工具调用

**状态**:
```typescript
interface ChatState {
  currentSessionId: string | null
  messages: Message[]
  sessions: Session[]
  isLoading: boolean
  isStreaming: boolean
  currentToolCalls: ToolCall[]
}
```

**Actions**:
```typescript
// 发送消息
async sendMessage(content: string): Promise<void>

// 流式发送消息
async sendMessageStream(content: string): Promise<void>

// 加载会话列表
async loadSessions(): Promise<void>

// 切换会话
async switchSession(sessionId: string): Promise<void>

// 删除会话
async deleteSession(sessionId: string): Promise<void>

// 清空当前会话
clearCurrentSession(): void
```

**使用示例**:
```typescript
import { useChatStore } from '@/stores/chat'

const chatStore = useChatStore()

// 发送消息
await chatStore.sendMessageStream('糖尿病有什么症状？')

// 监听消息变化
watch(() => chatStore.messages, (newMessages) => {
  console.log('消息更新:', newMessages)
})
```

### 3. UI状态 (stores/ui.ts)

**职责**: 管理UI相关状态（侧边栏、主题等）

**状态**:
```typescript
interface UIState {
  sidebarCollapsed: boolean
  theme: 'light' | 'dark'
  toastMessage: string | null
  confirmDialog: ConfirmDialogOptions | null
}
```

---

## 🧩 组件系统

### 聊天组件

#### ChatContainer.vue
**职责**: 聊天界面容器，协调消息列表和输入框

```vue
<template>
  <div class="chat-container">
    <MessageList :messages="messages" />
    <InputBox @send="handleSend" />
  </div>
</template>
```

#### MessageList.vue
**职责**: 消息列表展示，自动滚动

```vue
<template>
  <div class="message-list" ref="listRef">
    <MessageItem
      v-for="msg in messages"
      :key="msg.id"
      :message="msg"
    />
  </div>
</template>
```

#### MessageItem.vue
**职责**: 单条消息展示，区分用户/助手消息

```vue
<template>
  <div :class="['message-item', message.role]">
    <UserMessage v-if="message.role === 'user'" :content="message.content" />
    <AssistantMessage v-else :content="message.content" :toolCalls="message.toolCalls" />
  </div>
</template>
```

#### AssistantMessage.vue
**职责**: 助手消息展示，包含Markdown渲染和工具调用

```vue
<template>
  <div class="assistant-message">
    <!-- 工具调用卡片 -->
    <ToolCallCard
      v-for="tool in toolCalls"
      :key="tool.id"
      :toolCall="tool"
    />
    
    <!-- Markdown内容 -->
    <MarkdownRenderer :content="content" />
  </div>
</template>
```

#### InputBox.vue
**职责**: 用户输入框，支持多行输入和快捷键

```vue
<template>
  <div class="input-box">
    <textarea
      v-model="input"
      @keydown.enter.exact.prevent="handleSend"
      placeholder="输入您的问题..."
    />
    <button @click="handleSend" :disabled="!input.trim()">
      <IconSend />
    </button>
  </div>
</template>
```

#### ToolCallCard.vue
**职责**: 工具调用可视化展示

```vue
<template>
  <div class="tool-card" :class="toolCall.status">
    <div class="tool-header" @click="toggleExpand">
      <IconTool />
      <span class="tool-name">{{ toolCall.name }}</span>
      <span class="tool-status">{{ statusText }}</span>
    </div>
    
    <div v-if="expanded" class="tool-body">
      <div class="tool-arguments">
        <pre>{{ JSON.stringify(toolCall.arguments, null, 2) }}</pre>
      </div>
      <div class="tool-result">
        {{ toolCall.result }}
      </div>
    </div>
  </div>
</template>
```

### 侧边栏组件

#### Sidebar.vue
**职责**: 侧边栏容器，包含会话列表和用户信息

```vue
<template>
  <aside class="sidebar" :class="{ collapsed: uiStore.sidebarCollapsed }">
    <div class="sidebar-header">
      <h2>智医问答</h2>
      <button @click="toggleSidebar">
        <IconMenu />
      </button>
    </div>
    
    <SessionList :sessions="chatStore.sessions" />
    
    <div class="sidebar-footer">
      <UserInfo :user="authStore.user" />
    </div>
  </aside>
</template>
```

#### SessionList.vue
**职责**: 会话列表展示

```vue
<template>
  <div class="session-list">
    <button class="new-session-btn" @click="createNewSession">
      + 新建会话
    </button>
    
    <SessionItem
      v-for="session in sessions"
      :key="session.id"
      :session="session"
      :active="session.id === currentSessionId"
      @click="switchSession(session.id)"
      @delete="deleteSession(session.id)"
    />
  </div>
</template>
```

### 渲染器组件

#### MarkdownRenderer.vue
**职责**: Markdown内容渲染，支持代码高亮

```vue
<template>
  <div class="markdown-content" v-html="renderedHtml"></div>
</template>

<script setup lang="ts">
import { marked } from 'marked'
import { computed } from 'vue'

const props = defineProps<{ content: string }>()

const renderedHtml = computed(() => {
  return marked.parse(props.content, {
    breaks: true,
    gfm: true
  })
})
</script>
```

---

## 🌐 API通信

### HTTP客户端 (api/client.ts)

**配置**:
```typescript
import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器 - 添加Token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 错误处理
client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token过期，跳转登录
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export default client
```

### API模块

#### auth.ts - 认证API
```typescript
export async function login(request: LoginRequest): Promise<LoginResponse> {
  const { data } = await client.post('/api/v1/auth/login', request)
  return data
}

export async function register(request: RegisterRequest): Promise<LoginResponse> {
  const { data } = await client.post('/api/v1/auth/register', request)
  return data
}

export async function logout(): Promise<void> {
  await client.post('/api/v1/auth/logout')
}

export async function me(): Promise<User> {
  const { data } = await client.get('/api/v1/auth/me')
  return data
}
```

#### qa.ts - 问答API
```typescript
export async function askQuestion(request: QARequest): Promise<QAResponse> {
  const { data } = await client.post('/api/v1/qa', request)
  return data
}

export async function clearSession(sessionId: string): Promise<void> {
  await client.post('/api/v1/qa/clear-session', { session_id: sessionId })
}
```

#### history.ts - 历史API
```typescript
export async function getSessions(): Promise<SessionListResponse> {
  const { data } = await client.get('/api/v1/history/sessions')
  return data
}

export async function getHistory(params?: {
  page?: number
  page_size?: number
}): Promise<HistoryResponse> {
  const { data } = await client.get('/api/v1/history', { params })
  return data
}
```

---

## 📡 SSE流式通信

### SSEClient类 (api/sse.ts)

**职责**: 封装SSE连接，提供事件监听

```typescript
class SSEClient {
  private url: string
  private eventSource: EventSource | null = null
  private handlers: Map<string, Set<SSEEventHandler>> = new Map()
  
  constructor(url: string) {
    this.url = url
  }
  
  connect(): void {
    this.eventSource = new EventSource(this.url)
    
    this.eventSource.onmessage = (event) => {
      if (event.data === '[DONE]') {
        this.close()
        return
      }
      
      try {
        const data = JSON.parse(event.data)
        this.emit(data.type, data)
      } catch (error) {
        console.error('解析SSE数据失败:', error)
      }
    }
    
    this.eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error)
      this.emit('error', error)
      this.close()
    }
  }
  
  on(eventType: string, handler: SSEEventHandler): void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    this.handlers.get(eventType)!.add(handler)
  }
  
  off(eventType: string, handler: SSEEventHandler): void {
    this.handlers.get(eventType)?.delete(handler)
  }
  
  private emit(eventType: string, data: any): void {
    this.handlers.get(eventType)?.forEach(handler => handler(data))
  }
  
  close(): void {
    this.eventSource?.close()
    this.eventSource = null
  }
}
```

**使用示例**:
```typescript
const sseClient = new SSEClient('/api/v1/qa/stream')

// 监听工具调用
sseClient.on('tool_start', (data) => {
  console.log('工具开始:', data.tool_name)
})

// 监听内容块
sseClient.on('chunk', (data) => {
  appendContent(data.content)
})

// 监听元数据
sseClient.on('meta', (data) => {
  console.log('实体:', data.entities)
})

// 开始连接
sseClient.connect()
```

---

## 🛣️ 路由系统

### 路由配置 (router/index.ts)

```typescript
import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('@/views/ChatView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('@/views/HistoryView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'Knowledge',
    component: () => import('@/views/KnowledgeView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/ProfileView.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.meta.requiresAuth

  // 刷新后仅有 token：尝试恢复 user 信息
  if (authStore.isAuthenticated && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch {
      // token 无效则按未登录处理
    }
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    // 需要认证但未登录,跳转到登录页
    next({ name: 'Login', query: { redirect: to.fullPath } })
  } else if (to.name === 'Login' && authStore.isAuthenticated) {
    // 已登录用户访问登录页,跳转到首页
    next({ name: 'Home' })
  } else {
    next()
  }
})

export default router
```

---

## 🛠️ 工具函数

### 缓存工具 (utils/cache.ts)
```typescript
export function setCache(key: string, value: any, ttl?: number): void
export function getCache<T>(key: string): T | null
export function clearCache(key: string): void
```

### 防抖函数 (utils/debounce.ts)
```typescript
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void
```

### 错误处理 (utils/error-handler.ts)
```typescript
export function handleApiError(error: any): string
export function showError(message: string): void
```

---

## 🎨 样式系统

### 全局样式 (assets/styles/global.scss)
- 重置样式
- 通用类名
- 布局工具类

### 变量定义 (assets/styles/variables.scss)
```scss
// 颜色
$primary-color: #409eff;
$success-color: #67c23a;
$warning-color: #e6a23c;
$danger-color: #f56c6c;

// 深色主题
$dark-bg: #1a1a1a;
$dark-text: #e0e0e0;

// 间距
$spacing-xs: 4px;
$spacing-sm: 8px;
$spacing-md: 16px;
$spacing-lg: 24px;
```

### 动画效果 (assets/styles/animations.scss)
```scss
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
```

---

## 📝 最佳实践

1. **组件职责单一**: 每个组件只负责一个功能
2. **使用Composition API**: 提高代码复用性
3. **TypeScript类型安全**: 所有API和Props都有类型定义
4. **响应式设计**: 支持移动端和桌面端
5. **性能优化**: 使用虚拟滚动、懒加载等技术
6. **错误边界**: 优雅处理组件错误

---

*本文档由 doc-updater agent 生成 @ 2026-03-25*


---

## 📄 页面视图详解

### 1. HomeView.vue - 首页
**功能**: 系统介绍和快速导航

**主要特性**:
- 系统特点展示（知识图谱、智能问答、多轮对话、实体识别）
- 最近对话列表
- 快速开始按钮

**关键功能**:
```typescript
// 开始新对话
const startChat = () => {
  router.push({ name: 'Chat' })
}

// 查看历史记录
const viewHistory = () => {
  router.push({ name: 'History' })
}

// 继续会话
const continueSession = (sessionId: string) => {
  router.push({ name: 'Chat', query: { session: sessionId } })
}

// 加载最近会话
const loadRecentSessions = async () => {
  const response = await getSessionList(1, 5)
  recentSessions.value = response.sessions || []
}
```

**UI组件**:
- 特性卡片网格（4个特性）
- 最近对话列表
- 渐变背景头部

---

### 2. ChatView.vue - 聊天页面
**功能**: 智能问答主界面

**主要特性**:
- 实时流式对话
- 工具调用可视化
- Markdown渲染
- 实体高亮
- 会话管理

**详见**: 原文档中的聊天组件部分

---

### 3. HistoryView.vue - 历史记录页面
**功能**: 查看和管理对话历史

**主要特性**:
- 会话列表展示
- 搜索过滤
- 分页加载
- 继续对话
- 删除会话

**关键功能**:
```typescript
// 加载会话列表
const loadSessions = async () => {
  loading.value = true
  try {
    const response = await getSessionList(currentPage.value, 10)
    sessions.value = response.sessions || []
    totalPages.value = Math.ceil((response.total || 0) / 10)
  } catch (error) {
    showToast('加载历史记录失败', 'error')
  } finally {
    loading.value = false
  }
}

// 继续会话
const continueSession = (sessionId: string) => {
  router.push({ name: 'Chat', query: { session: sessionId } })
}

// 删除会话（带确认）
const confirmDelete = async (sessionId: string) => {
  const confirmed = await showConfirm(
    '确认删除',
    '确定要删除这个对话吗？',
    '此操作不可恢复',
    'warning'
  )
  
  if (confirmed) {
    await deleteSession(sessionId)
    showToast('删除成功', 'success')
    loadSessions()
  }
}
```

**会话卡片信息**:
- 会话标题
- 更新时间
- 消息数量
- 平均响应时间
- 最后提问预览

---

### 4. KnowledgeView.vue - 知识库页面
**功能**: 医疗知识搜索和浏览

**主要特性**:
- 实体搜索（疾病、症状、药品、检查）
- 类型过滤
- 搜索结果展示
- 实体详情查看
- 向AI咨询

**关键功能**:
```typescript
// 搜索知识
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    showToast('请输入搜索关键词', 'warning')
    return
  }

  loading.value = true
  hasSearched.value = true

  try {
    // 调用后端搜索API
    const response = await searchKnowledge(
      searchKeyword.value, 
      selectedType.value
    )
    searchResults.value = response.results
  } catch (error) {
    showToast('搜索失败', 'error')
    searchResults.value = []
  } finally {
    loading.value = false
  }
}

// 查看详情
const viewDetail = (item: any) => {
  selectedItem.value = item
  showDetailModal.value = true
}

// 向AI咨询
const askAbout = (name: string) => {
  showDetailModal.value = false
  router.push({ 
    name: 'Chat', 
    query: { question: `请介绍一下${name}` }
  })
}
```

**实体类型**:
- 全部
- 疾病 (Disease)
- 症状 (Symptom)
- 药品 (Drug)
- 检查 (Check)

**知识库统计**:
- 10,000+ 疾病
- 5,000+ 药品
- 3,000+ 症状
- 2,000+ 检查项

---

### 5. ProfileView.vue - 个人中心页面
**功能**: 用户信息管理

**主要特性**:
- 用户信息展示
- 修改密码
- 退出登录

**关键功能**:
```typescript
// 修改密码
const handleChangePassword = async () => {
  // 验证密码
  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    showToast('两次输入的密码不一致', 'error')
    return
  }

  if (passwordForm.value.newPassword.length < 6) {
    showToast('新密码至少需要6位', 'error')
    return
  }

  isChangingPassword.value = true
  try {
    await changePassword(passwordForm.value)
    showToast('密码修改成功，请重新登录', 'success')
    
    // 清空表单
    passwordForm.value = {
      oldPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    
    // 延迟后退出登录
    setTimeout(() => {
      authStore.logout()
      router.push({ name: 'Login' })
    }, 1500)
  } catch (error) {
    showToast('密码修改失败', 'error')
  } finally {
    isChangingPassword.value = false
  }
}

// 退出登录（带确认）
const handleLogout = async () => {
  const confirmed = await showConfirm(
    '确认退出',
    '确定要退出登录吗？',
    '',
    'warning'
  )

  if (confirmed) {
    await authStore.logout()
    router.push({ name: 'Login' })
    showToast('已退出登录', 'success')
  }
}
```

**用户信息**:
- 用户名
- 邮箱
- 用户类型（患者/医生/管理员）
- 注册时间

---

### 6. AdminView.vue - 管理后台页面
**功能**: 系统管理（开发中）

**计划功能**:
- 用户管理
- 对话监控
- 系统统计
- 知识库管理

---

### 7. LoginView.vue - 登录页面
**功能**: 用户认证

**主要特性**:
- 登录表单
- 注册表单
- 表单验证
- 错误提示

---

### 8. NotFound.vue - 404页面
**功能**: 处理未找到的路由

**主要特性**:
- 友好的404提示
- 返回首页按钮

---

## 🧭 导航组件

### Navbar.vue - 顶部导航栏
**功能**: 全局导航和用户菜单

**主要特性**:
- Logo和品牌名称
- 导航菜单（首页、智能问答、历史记录、知识库）
- 用户下拉菜单（个人中心、退出登录）
- 响应式设计

**导航项**:
```typescript
const menuItems = [
  { path: '/', label: '首页', icon: HomeIcon },
  { path: '/chat', label: '智能问答', icon: ChatIcon },
  { path: '/history', label: '历史记录', icon: HistoryIcon },
  { path: '/knowledge', label: '知识库', icon: KnowledgeIcon }
]
```

**用户菜单**:
- 用户头像（首字母）
- 用户名显示
- 下拉菜单
  - 个人中心
  - 退出登录

**响应式特性**:
- 移动端隐藏品牌文字
- 移动端隐藏导航文字（仅显示图标）
- 移动端隐藏用户名

---

## 🎨 页面样式系统

### CSS变量
所有页面使用统一的CSS变量系统：

```scss
// 颜色
--color-bg-primary: #ffffff
--color-bg-secondary: #f5f5f5
--color-bg-tertiary: #e8e8e8
--color-text-primary: #333333
--color-text-secondary: #666666
--color-text-tertiary: #999999
--color-primary: #667eea
--color-primary-dark: #5568d3
--color-error: #ff4d4f
--color-border: #e0e0e0

// 间距
--spacing-xs: 4px
--spacing-sm: 8px
--spacing-md: 16px
--spacing-lg: 24px
--spacing-xl: 32px

// 圆角
--radius-sm: 4px
--radius-md: 8px
--radius-lg: 12px
--radius-xl: 16px
--radius-full: 9999px

// 阴影
--shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05)
--shadow-md: 0 2px 8px rgba(0, 0, 0, 0.1)
--shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.15)
--shadow-xl: 0 12px 24px rgba(0, 0, 0, 0.2)

// 字体
--text-xs: 12px
--text-sm: 14px
--text-base: 16px
--text-lg: 18px
--text-xl: 20px
--text-2xl: 24px
--text-3xl: 30px
--text-4xl: 36px

--font-normal: 400
--font-medium: 500
--font-semibold: 600
--font-bold: 700

// 过渡
--transition-fast: 0.15s ease
--transition-base: 0.3s ease
--transition-slow: 0.5s ease
```

### 通用组件样式
- 卡片：白色背景、圆角、阴影、边框
- 按钮：主按钮（蓝色）、次按钮（白色边框）、危险按钮（红色）
- 输入框：边框、圆角、聚焦效果
- 标签：圆角、不同颜色表示不同类型

---

## 📱 响应式设计

### 断点
```scss
// 移动端
@media (max-width: 768px) {
  // 隐藏次要信息
  // 简化导航
  // 调整布局为单列
}

// 平板
@media (min-width: 769px) and (max-width: 1024px) {
  // 两列布局
}

// 桌面
@media (min-width: 1025px) {
  // 多列布局
  // 完整功能展示
}
```

### 移动端优化
- 导航栏：仅显示图标
- 卡片：单列布局
- 表单：全宽输入框
- 按钮：增大点击区域

---

## 🔄 页面间导航流程

```
登录页 (LoginView)
    ↓ 登录成功
首页 (HomeView)
    ↓ 点击"开始咨询"
智能问答 (ChatView)
    ↓ 查看历史
历史记录 (HistoryView)
    ↓ 继续对话
智能问答 (ChatView)
    ↓ 搜索知识
知识库 (KnowledgeView)
    ↓ 向AI咨询
智能问答 (ChatView)
    ↓ 个人中心
个人中心 (ProfileView)
    ↓ 退出登录
登录页 (LoginView)
```

---

*文档更新 @ 2026-03-25 - 新增6个页面和导航组件*
