# 实现计划 - 医疗问答前端界面

## 概述

本实现计划将医疗问答前端界面的设计转换为一系列可执行的编码任务。采用 Vue 3 + TypeScript 技术栈,通过 SSE 实现流式输出,提供 Agent 思考过程可视化和工具调用结果展示。

## 任务列表

### 1. 项目初始化和基础配置

- [ ] 1.1 创建 Vue 3 + TypeScript 项目
  - 使用 Vite 创建项目: `npm create vite@latest frontend -- --template vue-ts`
  - 安装核心依赖: vue-router, pinia, axios
  - 配置 TypeScript (tsconfig.json)
  - 配置 Vite (vite.config.ts)
  - _需求: 所有需求的基础_

- [ ] 1.2 设置项目结构
  - 创建目录结构 (api/, components/, stores/, types/, utils/, views/)
  - 配置路径别名 (@/ 指向 src/)
  - 创建 .env 文件配置环境变量
  - _需求: 所有需求的基础_

- [ ] 1.3 配置设计系统
  - 创建 CSS 变量文件 (variables.scss)
  - 定义颜色方案、字体、间距、阴影等
  - 导入 Google Fonts (Outfit, Inter)
  - 创建全局样式文件 (global.scss)
  - 创建动画文件 (animations.scss)
  - _需求: 1.5, 所有 UI 相关需求_

### 2. TypeScript 类型定义

- [ ] 2.1 定义核心数据类型
  - 创建 types/chat.ts (Message, Session, ToolCall, Entity 等)
  - 创建 types/sse.ts (SSE 事件类型)
  - 创建 types/api.ts (API 请求/响应类型)
  - _需求: 所有需求的基础_

### 3. API 层实现

- [ ] 3.1 实现 HTTP 客户端
  - 创建 Axios 实例 (api/client.ts)
  - 配置请求拦截器(添加 Token)
  - 配置响应拦截器(处理错误)
  - _需求: 7.3, 8.2_

- [ ] 3.2 实现 SSE 客户端
  - 创建 SSEClient 类 (api/sse.ts)
  - 实现连接管理(connect, close, isConnected)
  - 实现事件解析和分发
  - 处理连接错误和重连
  - _需求: 2.1, 2.4, 2.5_

- [ ]* 3.3 编写 SSE 客户端属性测试
  - **属性 1: SSE 连接管理**
  - **验证需求: 2.1, 2.4**

- [ ] 3.4 实现问答 API
  - 创建 api/qa.ts (askQuestion, clearSession, deleteSession)
  - 实现流式问答请求
  - _需求: 2.1, 6.5_

- [ ] 3.5 实现认证 API
  - 创建 api/auth.ts (login, register, logout)
  - _需求: 7.1, 7.2_

### 4. 状态管理 (Pinia Stores)

- [ ] 4.1 实现 Chat Store
  - 创建 stores/chat.ts
  - 实现会话管理(createSession, switchSession, deleteSession)
  - 实现消息管理(addUserMessage, startAssistantMessage, appendContent)
  - 实现工具调用管理(addToolCall, updateToolCallStatus)
  - 实现流式输出状态管理(completeStreaming, setError)
  - _需求: 2.2, 3.1, 3.2, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 4.2 编写 Chat Store 属性测试
  - **属性 5: Session ID 唯一性**
  - **属性 2: 流式内容追加**
  - **属性 6: 会话切换一致性**
  - **验证需求: 6.1, 2.2, 6.4**

- [ ] 4.3 实现 Auth Store
  - 创建 stores/auth.ts
  - 实现认证状态管理(setToken, setUser, clearAuth)
  - 实现 Token 持久化(localStorage)
  - _需求: 7.2, 7.4_

- [ ] 4.4 实现 UI Store
  - 创建 stores/ui.ts
  - 实现侧边栏状态管理
  - 实现 Toast 通知管理
  - _需求: 8.5_

### 5. Composables (组合式函数)

- [ ] 5.1 实现 useChat
  - 创建 composables/useChat.ts
  - 实现 sendMessage 函数(建立 SSE 连接)
  - 实现 SSE 事件处理(handleSSEMessage)
  - 实现错误处理(handleSSEError)
  - 实现停止流式输出(stopStreaming)
  - _需求: 2.1, 2.2, 2.3, 2.4, 2.5, 3.1, 3.2, 5.1, 8.1_

- [ ]* 5.2 编写 useChat 属性测试
  - **属性 3: 工具调用状态管理**
  - **属性 8: 错误处理完整性**
  - **验证需求: 3.1, 3.2, 2.5, 8.1, 8.2, 8.3, 8.4**

- [ ] 5.3 实现 useAuth
  - 创建 composables/useAuth.ts
  - 实现 login, register, logout 函数
  - 实现认证状态计算属性
  - _需求: 7.1, 7.2, 7.4_

- [ ]* 5.4 编写 useAuth 属性测试
  - **属性 7: Token 认证传递**
  - **验证需求: 7.3**

- [ ] 5.5 实现 useToast
  - 创建 composables/useToast.ts
  - 实现 Toast 通知管理(success, error, warning, info)
  - _需求: 8.5_

### 6. 通用组件

- [ ] 6.1 实现 Button 组件
  - 创建 components/common/Button.vue
  - 支持不同类型(primary, secondary, danger)
  - 支持加载状态
  - 支持禁用状态
  - _需求: 所有交互需求_

- [ ] 6.2 实现 Loading 组件
  - 创建 components/common/Loading.vue
  - 实现加载动画(旋转、脉冲等)
  - _需求: 9.1, 9.2_

- [ ] 6.3 实现 Toast 组件
  - 创建 components/common/Toast.vue
  - 支持不同类型(success, error, warning, info)
  - 实现自动消失
  - 实现动画效果
  - _需求: 8.5_

- [ ] 6.4 实现 Modal 组件
  - 创建 components/common/Modal.vue
  - 支持打开/关闭动画
  - 支持键盘 Esc 关闭
  - 支持点击遮罩关闭
  - _需求: 10.4_

### 7. 聊天相关组件

- [ ] 7.1 实现 ChatContainer 组件
  - 创建 components/chat/ChatContainer.vue
  - 实现整体布局(侧边栏 + 主聊天区)
  - 集成 MessageList 和 InputBox
  - 实现响应式布局
  - _需求: 1.1, 1.2, 1.3, 1.4, 10.1, 10.2, 10.3_

- [ ]* 7.2 编写 ChatContainer 响应式测试
  - **属性 9: 响应式布局适配**
  - **验证需求: 10.1, 10.2, 10.3**

- [ ] 7.3 实现 MessageList 组件
  - 创建 components/chat/MessageList.vue
  - 使用虚拟滚动(vue-virtual-scroller)
  - 实现自动滚动到底部
  - 实现消息渲染
  - _需求: 1.1, 11.2_

- [ ] 7.4 实现 MessageItem 组件
  - 创建 components/chat/MessageItem.vue
  - 根据消息类型渲染不同组件
  - 实现消息动画(淡入、滑入)
  - _需求: 1.1, 9.5_

- [ ] 7.5 实现 UserMessage 组件
  - 创建 components/chat/UserMessage.vue
  - 显示用户头像和消息内容
  - 实现样式
  - _需求: 1.1_

- [ ] 7.6 实现 AssistantMessage 组件
  - 创建 components/chat/AssistantMessage.vue
  - 集成 MarkdownRenderer
  - 集成 EntityHighlight
  - 集成 ToolCallCard
  - 实现打字机效果(流式输出时)
  - _需求: 1.1, 2.3, 3.3, 5.2, 5.3, 5.4, 5.5, 12.1_

- [ ]* 7.7 编写 AssistantMessage 单元测试
  - 测试 Markdown 渲染
  - 测试实体高亮
  - 测试工具调用显示
  - _需求: 12.1, 5.2, 3.3_

- [ ] 7.8 实现 ToolCallCard 组件
  - 创建 components/chat/ToolCallCard.vue
  - 显示工具名称、参数、结果
  - 实现状态样式(pending, running, success, error)
  - 实现展开/折叠功能
  - 实现动画效果(脉冲、波纹)
  - _需求: 3.1, 3.2, 3.3, 3.4, 3.5, 9.3_

- [ ]* 7.9 编写 ToolCallCard 属性测试
  - **属性 11: 工具结果渲染分发**
  - **验证需求: 4.1, 4.2, 4.3, 4.4**

- [ ] 7.10 实现 EntityHighlight 组件
  - 创建 components/chat/EntityHighlight.vue
  - 实现实体识别和高亮
  - 为不同类型实体应用不同颜色
  - 实现发光动画
  - _需求: 5.1, 5.2, 5.3, 5.4, 5.5_

- [ ]* 7.11 编写 EntityHighlight 属性测试
  - **属性 4: 实体高亮一致性**
  - **验证需求: 5.2, 5.3, 5.4, 5.5**

- [ ] 7.12 实现 InputBox 组件
  - 创建 components/chat/InputBox.vue
  - 实现多行输入(textarea)
  - 实现字符计数(最大 1000)
  - 实现快捷键(Enter 发送, Shift+Enter 换行)
  - 实现防抖处理
  - 实现禁用状态
  - _需求: 1.2, 11.4_

- [ ]* 7.13 编写 InputBox 单元测试
  - 测试 Enter 发送
  - 测试 Shift+Enter 换行
  - 测试字符限制
  - 测试防抖
  - _需求: 1.2, 11.4_

- [ ]* 7.14 编写 InputBox 属性测试
  - **属性 13: 防抖输入处理**
  - **验证需求: 11.4**

### 8. 侧边栏组件

- [ ] 8.1 实现 Sidebar 组件
  - 创建 components/sidebar/Sidebar.vue
  - 实现侧边栏布局
  - 实现移动端展开/收起
  - 集成 SessionList
  - 显示用户信息
  - _需求: 1.3, 6.2_

- [ ] 8.2 实现 SessionList 组件
  - 创建 components/sidebar/SessionList.vue
  - 显示会话列表
  - 实现新建会话按钮
  - _需求: 6.2, 6.3_

- [ ] 8.3 实现 SessionItem 组件
  - 创建 components/sidebar/SessionItem.vue
  - 显示会话标题和时间
  - 实现选中状态
  - 实现删除按钮
  - _需求: 6.2, 6.4, 6.5_

### 9. 认证组件

- [ ] 9.1 实现 LoginForm 组件
  - 创建 components/auth/LoginForm.vue
  - 实现用户名/密码输入
  - 实现表单验证
  - 实现登录逻辑
  - _需求: 7.1, 7.2_

- [ ] 9.2 实现 RegisterForm 组件
  - 创建 components/auth/RegisterForm.vue
  - 实现注册表单
  - 实现表单验证
  - 实现注册逻辑
  - _需求: 7.1_

### 10. 内容渲染器

- [ ] 10.1 实现 MarkdownRenderer 组件
  - 创建 components/renderers/MarkdownRenderer.vue
  - 集成 markdown-it
  - 集成 highlight.js (代码高亮)
  - 实现 XSS 防护(DOMPurify)
  - 实现表格、列表渲染
  - 实现链接处理
  - _需求: 12.1, 12.2, 12.3, 12.5_

- [ ]* 10.2 编写 MarkdownRenderer 属性测试
  - **属性 10: Markdown 渲染正确性**
  - **验证需求: 12.1, 12.2, 12.3**

- [ ] 10.3 实现 DiseaseCard 组件
  - 创建 components/renderers/DiseaseCard.vue
  - 显示疾病名称、匹配度、症状
  - 实现卡片样式
  - _需求: 4.1_

- [ ] 10.4 实现 DrugCard 组件
  - 创建 components/renderers/DrugCard.vue
  - 显示药品名称、用法、注意事项
  - 高亮药品名称
  - _需求: 4.2_

- [ ] 10.5 实现 TreatmentPlan 组件
  - 创建 components/renderers/TreatmentPlan.vue
  - 以列表形式显示治疗步骤
  - 实现步骤编号
  - _需求: 4.3_

### 11. 工具函数

- [ ] 11.1 实现格式化工具
  - 创建 utils/format.ts
  - 实现日期格式化
  - 实现文本截断(truncateText, truncateJSON)
  - _需求: 11.3_

- [ ]* 11.2 编写格式化工具属性测试
  - **属性 14: 工具结果截断**
  - **验证需求: 11.3**

- [ ] 11.3 实现存储工具
  - 创建 utils/storage.ts
  - 实现 localStorage 封装
  - 实现 sessionStorage 封装
  - _需求: 7.2_

- [ ] 11.4 实现验证工具
  - 创建 utils/validator.ts
  - 实现表单验证(邮箱、密码等)
  - _需求: 7.1_

- [ ] 11.5 实现防抖和节流
  - 创建 utils/debounce.ts
  - 实现 debounce 函数
  - 实现 throttle 函数
  - _需求: 11.4_

- [ ] 11.6 实现错误处理
  - 创建 utils/error-handler.ts
  - 实现 handleError 函数
  - 定义错误类型和处理策略
  - _需求: 8.1, 8.2, 8.3, 8.4_

- [ ] 11.7 实现 XSS 防护
  - 创建 utils/sanitize.ts
  - 集成 DOMPurify
  - 实现 sanitizeHTML 函数
  - _需求: 12.1_

- [ ] 11.8 实现缓存工具
  - 创建 utils/cache.ts
  - 实现 LRU Cache
  - _需求: 11.5_

### 12. 页面视图

- [ ] 12.1 实现 ChatView 页面
  - 创建 views/ChatView.vue
  - 集成 ChatContainer
  - 实现页面布局
  - _需求: 1.1, 1.2, 1.3_

- [ ] 12.2 实现 LoginView 页面
  - 创建 views/LoginView.vue
  - 集成 LoginForm 和 RegisterForm
  - 实现页面布局和切换
  - _需求: 7.1_

- [ ] 12.3 实现 NotFound 页面
  - 创建 views/NotFound.vue
  - 实现 404 页面
  - _需求: 路由错误处理_

### 13. 路由配置

- [ ] 13.1 配置 Vue Router
  - 创建 router.ts
  - 定义路由(/, /login, /404)
  - 实现路由守卫(认证检查)
  - 实现懒加载
  - _需求: 7.1, 7.4_

### 14. 应用入口

- [ ] 14.1 配置应用入口
  - 创建 main.ts
  - 初始化 Vue 应用
  - 注册 Pinia
  - 注册 Router
  - 挂载应用
  - _需求: 所有需求的基础_

- [ ] 14.2 创建根组件
  - 创建 App.vue
  - 实现全局布局
  - 集成 Toast 组件
  - _需求: 所有需求的基础_

### 15. 性能优化

- [ ] 15.1 实现虚拟滚动
  - 安装 vue-virtual-scroller
  - 在 MessageList 中集成
  - _需求: 11.2_

- [ ] 15.2 实现代码分割
  - 配置 Vite rollupOptions
  - 实现组件懒加载
  - _需求: 11.1_

- [ ] 15.3 实现缓存策略
  - 实现会话数据缓存
  - 实现 API 响应缓存
  - _需求: 11.5_

### 16. 可访问性

- [ ] 16.1 添加 ARIA 标签
  - 为所有交互元素添加 aria-label
  - 为动态内容添加 aria-live
  - _需求: 10.5_

- [ ] 16.2 实现键盘导航
  - 创建 composables/useKeyboard.ts
  - 实现 Esc 关闭模态框
  - 实现 Tab 导航
  - 实现方向键导航
  - _需求: 10.4_

### 17. 测试

- [ ]* 17.1 配置测试环境
  - 安装 Vitest, @vue/test-utils
  - 安装 fast-check (属性测试)
  - 安装 Playwright (E2E 测试)
  - 配置 vitest.config.ts
  - _需求: 所有测试需求_

- [ ]* 17.2 编写 E2E 测试
  - 测试完整问答流程
  - 测试 SSE 连接错误处理
  - 测试用户认证流程
  - 测试会话管理
  - _需求: 所有核心功能_

- [ ]* 17.3 运行测试并验证覆盖率
  - 运行单元测试
  - 运行属性测试
  - 运行 E2E 测试
  - 验证覆盖率 ≥ 80%
  - _需求: 所有需求_

### 18. 构建和部署

- [ ] 18.1 配置生产构建
  - 配置 Vite 生产构建选项
  - 配置代码压缩
  - 配置环境变量
  - _需求: 11.1_

- [ ] 18.2 创建部署配置
  - 创建 Nginx 配置文件
  - 配置 Gzip 压缩
  - 配置静态资源缓存
  - 配置 API 代理
  - _需求: 所有需求_

### 19. 检查点 - 确保所有测试通过

- [ ] 19.1 最终验证
  - 运行所有测试
  - 验证所有功能正常
  - 检查性能指标
  - 检查可访问性
  - 询问用户是否有问题

## 注意事项

- 标记 `*` 的任务为可选任务,可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求,确保可追溯性
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边缘情况
- 检查点确保增量验证
