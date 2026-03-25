# Implementation Plan: Frontend Streaming Optimization

## Overview

基于 Vue 3 + SSE 实现前端流式传输优化，包括实时响应显示、工具调用状态展示、智能滚动等功能。采用增量开发方式，先实现核心流式功能，再逐步完善 UI 交互。

## Tasks

- [x] 1. 后端流式 API 增强
  - [x] 1.1 修改 MedicalAgent 支持工具调用事件
    - 在 agent.py 中添加 tool_start/tool_end 事件生成
    - 修改 chat_stream() 方法返回结构化事件
    - _Requirements: 6.1, 6.2_
  - [x] 1.2 更新 qa_service.py 流式处理
    - 转发 Agent 的工具调用事件
    - 确保事件格式符合设计规范
    - _Requirements: 6.3, 6.4_
  - [x] 1.3 更新 qa.py 路由
    - 确保 SSE 响应头正确
    - 添加客户端断开检测
    - _Requirements: 6.5, 6.6_

- [x] 2. Checkpoint - 后端流式 API 验证
  - 使用 curl 或 Postman 测试流式端点
  - 验证事件格式正确
  - 如有问题请询问用户

- [x] 3. 前端 SSE 连接管理
  - [x] 3.1 实现 SSEConnectionManager 类
    - 实现 connect()、abort()、processStream() 方法
    - 实现事件分发逻辑
    - _Requirements: 3.1, 3.4_
  - [x] 3.2 实现重连机制
    - 添加指数退避重试逻辑
    - 最多重试 3 次
    - _Requirements: 3.3_
  - [x] 3.3 实现事件处理器
    - 处理 chunk、tool_start、tool_end、meta、error 事件
    - _Requirements: 3.2, 3.5_

- [x] 4. 前端消息状态管理
  - [x] 4.1 更新消息数据结构
    - 添加 toolCalls、status、isStreaming 字段
    - 实现状态转换逻辑
    - _Requirements: 5.1, 5.2, 5.3_
  - [x] 4.2 实现流式内容累积
    - 处理 chunk 事件，累积内容
    - 实现增量 Markdown 渲染
    - _Requirements: 1.2, 1.5_

- [x] 5. 工具调用 UI 组件
  - [x] 5.1 添加工具卡片样式
    - 创建 .tool-card、.tool-header、.tool-status 样式
    - 添加 running、success、error 状态样式
    - _Requirements: 2.1, 2.2, 2.3, 2.4_
  - [x] 5.2 实现工具卡片组件
    - 显示工具名称和状态
    - 显示执行结果（可折叠）
    - _Requirements: 2.5, 2.6_

- [x] 6. Checkpoint - 流式显示验证
  - 测试完整的流式问答流程
  - 验证工具调用显示正确
  - 如有问题请询问用户

- [x] 7. UI 交互优化
  - [x] 7.1 实现流式指示器
    - 添加打字光标动画
    - 添加流式状态指示器
    - _Requirements: 1.1, 1.3, 1.4_
  - [x] 7.2 实现智能滚动
    - 自动滚动到最新消息
    - 用户滚动时暂停自动滚动
    - 添加"滚动到底部"按钮
    - _Requirements: 4.1, 4.2, 4.3_
  - [x] 7.3 实现停止生成功能
    - 添加"停止生成"按钮
    - 实现请求取消逻辑
    - _Requirements: 4.5, 4.6_

- [x] 8. 错误处理和恢复
  - [x] 8.1 实现错误显示
    - 显示连接错误消息
    - 显示服务器错误消息
    - _Requirements: 7.1, 1.6_
  - [x] 8.2 实现重试功能
    - 添加重试按钮
    - 保留用户输入
    - _Requirements: 7.2, 7.3, 7.5_
  - [x] 8.3 实现多次失败提示
    - 多次重试失败后显示网络检查建议
    - _Requirements: 7.4_

- [x] 9. 消息时间戳优化
  - [x] 9.1 确保所有消息显示时间戳
    - 用户消息和助手消息都显示时间
    - 使用相对时间格式（刚刚、X分钟前）
    - _Requirements: 5.4_

- [x] 10. Checkpoint - 完整功能验证
  - 测试所有交互功能
  - 验证错误处理正确
  - 如有问题请询问用户

- [ ]* 11. 属性测试
  - [ ]* 11.1 编写 Chunk 拼接完整性测试
    - **Property 1: Chunk Concatenation Integrity**
    - **Validates: Requirements 1.2, 1.5**
  - [ ]* 11.2 编写工具调用顺序测试
    - **Property 2: Tool Call Ordering Preservation**
    - **Validates: Requirements 2.6**
  - [ ]* 11.3 编写事件处理完整性测试
    - **Property 3: Event Type Handling Completeness**
    - **Validates: Requirements 3.2**

- [x] 12. Final Checkpoint - 完整验证
  - 确保所有功能正常工作
  - 验证流式传输稳定
  - 如有问题请询问用户

- [x] 13. UI Bug Fix - 工具图标尺寸修复
  - [x] 13.1 修复 .tool-icon SVG 尺寸溢出问题
    - 添加 min/max-width/height 约束
    - 添加 overflow: hidden 和 flex-shrink: 0
    - 使用 !important 确保 SVG 尺寸被强制约束
  - [x] 13.2 添加缺失的 CSS 类
    - 添加 .logo-icon 样式（模板使用但 CSS 缺失）
    - 添加 .welcome-icon 样式（模板使用但 CSS 缺失）
  - [x] 13.3 添加全局 SVG 约束规则
    - 为所有图标容器添加 SVG 尺寸约束
    - 确保 v-html 渲染的 SVG 不会溢出

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- 优先实现后端 API 增强，确保事件格式正确
- 前端实现采用渐进式方式，先核心功能后优化

