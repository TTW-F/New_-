# 需求文档 - 医疗问答前端界面

## 简介

为基于知识图谱和大语言模型的医疗智能问答系统设计并开发一个现代化、高质量的前端界面。该界面需要支持实时流式输出、Agent 思考过程可视化、工具调用展示等高级功能,并与真实后端 API 完全对接。

## 术语表

- **System**: 医疗问答前端系统
- **User**: 使用医疗问答系统的用户
- **Agent**: 后端医疗诊断智能代理
- **SSE**: Server-Sent Events,服务器推送事件
- **Tool_Call**: Agent 调用的工具(如疾病诊断、药品查询等)
- **Stream**: 流式输出,实时逐字返回内容
- **Session**: 用户会话,用于关联多轮对话
- **Entity**: 医疗实体(疾病、症状、药品等)

## 需求

### 需求 1: 用户界面布局

**用户故事:** 作为用户,我想要一个清晰、美观的界面布局,以便我能够轻松地与医疗问答系统交互。

#### 验收标准

1. THE System SHALL 提供一个主对话区域用于显示问答内容
2. THE System SHALL 提供一个输入区域用于用户输入问题
3. THE System SHALL 提供一个侧边栏用于显示会话历史和设置
4. THE System SHALL 使用响应式设计适配不同屏幕尺寸
5. THE System SHALL 遵循 frontend-design skill 中的设计原则,避免通用 AI 美学

### 需求 2: 实时流式输出

**用户故事:** 作为用户,我想要看到 Agent 的回答实时逐字显示,以便我能够更快地获得反馈。

#### 验收标准

1. WHEN 用户提交问题 THEN THE System SHALL 通过 SSE 连接到后端 `/api/v1/qa/stream` 端点
2. WHEN 接收到 `chunk` 事件 THEN THE System SHALL 实时追加内容到回答区域
3. WHEN 流式输出进行中 THEN THE System SHALL 显示打字动画效果
4. WHEN 接收到 `[DONE]` 标记 THEN THE System SHALL 关闭 SSE 连接
5. IF SSE 连接失败或超时 THEN THE System SHALL 显示错误提示并允许重试

### 需求 3: Agent 思考过程可视化

**用户故事:** 作为用户,我想要看到 Agent 的思考过程和工具调用,以便我能够理解回答的来源和可信度。

#### 验收标准

1. WHEN 接收到 `tool_start` 事件 THEN THE System SHALL 显示工具调用开始状态
2. WHEN 接收到 `tool_end` 事件 THEN THE System SHALL 显示工具调用结果
3. THE System SHALL 使用层级展示区分工具调用过程和最终回答内容
4. THE System SHALL 为不同类型的工具调用使用不同的视觉样式
5. THE System SHALL 允许用户展开/折叠工具调用详情

### 需求 4: 工具调用结果渲染

**用户故事:** 作为用户,我想要以结构化的方式查看工具调用结果,以便我能够快速理解返回的医疗信息。

#### 验收标准

1. WHEN 工具返回疾病诊断结果 THEN THE System SHALL 以卡片形式展示疾病列表
2. WHEN 工具返回药品信息 THEN THE System SHALL 高亮显示药品名称和用法
3. WHEN 工具返回治疗方案 THEN THE System SHALL 使用列表形式展示步骤
4. THE System SHALL 为不同类型的工具结果使用不同的渲染组件
5. THE System SHALL 支持 JSON 数据的格式化显示

### 需求 5: 医疗实体高亮

**用户故事:** 作为用户,我想要在回答中看到医疗实体被高亮显示,以便我能够快速识别关键信息。

#### 验收标准

1. WHEN 接收到 `meta` 事件包含 entities THEN THE System SHALL 提取实体信息
2. THE System SHALL 在回答文本中高亮显示疾病实体
3. THE System SHALL 在回答文本中高亮显示症状实体
4. THE System SHALL 在回答文本中高亮显示药品实体
5. THE System SHALL 为不同类型的实体使用不同的颜色标记

### 需求 6: 会话管理

**用户故事:** 作为用户,我想要管理我的对话会话,以便我能够查看历史对话或开始新对话。

#### 验收标准

1. THE System SHALL 为每个新对话自动生成唯一的 session_id
2. THE System SHALL 在侧边栏显示当前会话的对话历史
3. WHEN 用户点击"新对话"按钮 THEN THE System SHALL 创建新的 session_id
4. WHEN 用户选择历史会话 THEN THE System SHALL 加载该会话的对话记录
5. THE System SHALL 允许用户删除或清空会话

### 需求 7: 用户认证集成

**用户故事:** 作为用户,我想要能够登录系统,以便我的对话历史能够被保存。

#### 验收标准

1. THE System SHALL 提供登录和注册界面
2. WHEN 用户登录成功 THEN THE System SHALL 存储 JWT Token
3. WHEN 发送 API 请求 THEN THE System SHALL 在请求头中包含 Authorization Token
4. WHEN Token 过期 THEN THE System SHALL 提示用户重新登录
5. THE System SHALL 支持匿名访问(不保存历史)

### 需求 8: 错误处理和用户反馈

**用户故事:** 作为用户,我想要在出现错误时得到清晰的提示,以便我知道如何处理问题。

#### 验收标准

1. WHEN 接收到 `error` 事件 THEN THE System SHALL 显示错误消息
2. WHEN 网络请求失败 THEN THE System SHALL 显示网络错误提示
3. WHEN 后端服务不可用 THEN THE System SHALL 显示服务不可用提示
4. THE System SHALL 为所有错误提供重试选项
5. THE System SHALL 使用 Toast 通知显示非阻塞性提示

### 需求 9: 加载状态和动画

**用户故事:** 作为用户,我想要看到清晰的加载状态,以便我知道系统正在处理我的请求。

#### 验收标准

1. WHEN 用户提交问题 THEN THE System SHALL 显示加载指示器
2. WHEN 等待 Agent 响应 THEN THE System SHALL 显示"思考中"动画
3. WHEN 工具调用进行中 THEN THE System SHALL 显示工具执行动画
4. THE System SHALL 在流式输出时显示光标闪烁效果
5. THE System SHALL 使用平滑的过渡动画提升用户体验

### 需求 10: 响应式设计和可访问性

**用户故事:** 作为用户,我想要在不同设备上都能良好使用系统,以便我可以随时随地获取医疗建议。

#### 验收标准

1. THE System SHALL 在桌面端(>1024px)显示完整布局
2. THE System SHALL 在平板端(768px-1024px)调整布局
3. THE System SHALL 在移动端(<768px)使用单列布局
4. THE System SHALL 支持键盘导航
5. THE System SHALL 遵循 WCAG 2.1 AA 级可访问性标准

### 需求 11: 性能优化

**用户故事:** 作为用户,我想要系统快速响应,以便我能够高效地获取医疗信息。

#### 验收标准

1. THE System SHALL 在 2 秒内完成首屏渲染
2. THE System SHALL 使用虚拟滚动处理长对话历史
3. THE System SHALL 对大型工具结果进行分页或截断显示
4. THE System SHALL 使用防抖处理用户输入
5. THE System SHALL 缓存会话数据减少 API 调用

### 需求 12: 特殊内容处理

**用户故事:** 作为用户,我想要看到格式化的医疗内容,以便我能够更好地理解信息。

#### 验收标准

1. THE System SHALL 支持 Markdown 格式渲染
2. THE System SHALL 高亮显示代码块(如果有)
3. THE System SHALL 渲染表格和列表
4. THE System SHALL 显示免责声明和紧急警告的特殊样式
5. THE System SHALL 支持链接的点击跳转
