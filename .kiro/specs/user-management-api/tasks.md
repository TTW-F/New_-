# Implementation Plan: 用户管理与 API 服务模块

## Overview

本实现计划将设计文档中的 FastAPI 用户管理和 API 服务模块分解为可执行的开发任务。采用增量开发方式，每个任务都建立在前一个任务的基础上，确保代码始终可运行。

## Tasks

- [x] 1. 项目结构和基础设施搭建
  - 创建 FastAPI 应用目录结构
  - 配置数据库连接（MySQL、Redis）
  - 设置环境变量和配置管理
  - _Requirements: 7.1_

- [ ] 2. 数据模型和数据库初始化
  - [x] 2.1 创建 SQLAlchemy 数据模型
    - 实现 User、ConversationHistory、Feedback、TokenBlacklist 模型
    - 配置数据库迁移
    - _Requirements: 1.4, 4.3_
  - [ ]* 2.2 编写数据模型属性测试
    - **Property 4: 密码安全存储**
    - **Validates: Requirements 1.4**

- [ ] 3. 用户服务实现
  - [x] 3.1 实现 UserService 核心功能
    - 实现密码哈希和验证（bcrypt）
    - 实现密码强度验证
    - 实现用户注册逻辑
    - 实现用户认证逻辑
    - _Requirements: 1.1, 1.3, 1.4, 2.1_
  - [ ]* 3.2 编写用户服务属性测试
    - **Property 1: 有效注册创建用户**
    - **Property 3: 弱密码被拒绝**
    - **Validates: Requirements 1.1, 1.3, 2.1**

- [ ] 4. JWT 认证模块
  - [x] 4.1 实现 JWT Token 管理
    - 实现 Token 创建和验证
    - 实现 Token 黑名单（登出）
    - 实现 FastAPI 依赖注入（get_current_user）
    - _Requirements: 2.1, 2.4, 2.5_
  - [ ]* 4.2 编写 JWT 属性测试
    - **Property 6: 登录凭据验证**
    - **Property 7: Token 登出失效**
    - **Validates: Requirements 2.1, 2.5**

- [x] 5. Checkpoint - 确保认证模块测试通过
  - 运行所有测试，确保通过
  - 如有问题，请向用户确认

- [ ] 6. 认证 API 路由
  - [x] 6.1 实现 /api/v1/auth 路由
    - 实现 POST /register 端点
    - 实现 POST /login 端点
    - 实现 POST /logout 端点
    - _Requirements: 1.1, 1.2, 1.5, 2.1, 2.2, 2.3, 2.5_
  - [ ]* 6.2 编写认证 API 属性测试
    - **Property 2: 重复注册被拒绝**
    - **Property 5: 注册响应不含密码**
    - **Validates: Requirements 1.2, 1.5**

- [ ] 7. 对话服务实现
  - [x] 7.1 实现 ConversationService
    - 实现对话记录保存
    - 实现对话历史查询（分页、按会话过滤）
    - 实现软删除功能
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  - [ ]* 7.2 编写对话服务属性测试
    - **Property 10: 对话历史查询正确性**
    - **Property 11: 对话记录完整性**
    - **Property 12: 软删除正确性**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [ ] 8. 问答 API 集成
  - [x] 8.1 实现 QAService 和 /api/v1/qa 路由
    - 集成现有 GraphRAG 服务
    - 实现问答请求处理
    - 实现对话持久化（认证用户）
    - _Requirements: 3.1, 3.2, 3.3, 3.4_
  - [ ]* 8.2 编写问答 API 属性测试
    - **Property 8: 问答响应完整性**
    - **Property 9: 认证用户对话持久化**
    - **Validates: Requirements 3.2, 3.3, 3.4**

- [ ] 9. 对话历史 API 路由
  - [x] 9.1 实现 /api/v1/history 路由
    - 实现 GET /history 端点（分页查询）
    - 实现 DELETE /history/{id} 端点
    - _Requirements: 4.1, 4.2, 4.4, 4.5_

- [x] 10. Checkpoint - 确保核心功能测试通过
  - 运行所有测试，确保通过
  - 如有问题，请向用户确认

- [ ] 11. 反馈服务实现
  - [x] 11.1 实现反馈功能和 /api/v1/feedback 路由
    - 实现反馈保存
    - 实现对话存在性验证
    - _Requirements: 5.1, 5.2, 5.3_
  - [ ]* 11.2 编写反馈服务属性测试
    - **Property 13: 反馈保存与验证**
    - **Validates: Requirements 5.1, 5.2, 5.3**

- [ ] 12. 安全与限流
  - [x] 12.1 实现速率限制
    - 配置 slowapi 中间件
    - 实现匿名/认证用户差异化限流
    - _Requirements: 6.2, 6.3_
  - [x] 12.2 实现输入验证和安全防护
    - 配置 Pydantic 输入验证
    - 添加 SQL 注入和 XSS 防护
    - _Requirements: 6.1_
  - [ ]* 12.3 编写安全模块属性测试
    - **Property 14: 速率限制生效**
    - **Property 15: 输入验证防护**
    - **Validates: Requirements 6.1, 6.2, 6.3**

- [ ] 13. 健康检查和监控
  - [x] 13.1 实现 /health 端点
    - 检查 MySQL、Neo4j、Redis 连接状态
    - 返回系统版本和组件状态
    - _Requirements: 7.1, 7.2, 7.3, 7.4_
  - [ ]* 13.2 编写健康检查属性测试
    - **Property 16: 健康检查响应**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [ ] 14. 全局中间件和异常处理
  - [x] 14.1 实现全局中间件
    - 配置 CORS 中间件
    - 实现请求日志中间件
    - 实现全局异常处理
    - _Requirements: 6.4_

- [x] 15. Final Checkpoint - 确保所有测试通过
  - 运行完整测试套件
  - 验证所有属性测试通过
  - 如有问题，请向用户确认

- [x] 16. 前端界面开发
  - [x] 16.1 创建 Vue 3 前端应用
    - 实现响应式布局和现代化 UI 设计
    - 集成医疗科技感设计风格
    - _Requirements: 3.1, 3.2, 3.3_
  - [x] 16.2 实现用户认证界面
    - 登录/注册模态框
    - 用户状态管理
    - Token 持久化存储
    - _Requirements: 1.1, 2.1, 2.2, 2.3_
  - [x] 16.3 实现智能问答界面
    - 聊天消息列表
    - 实体标签和引用来源展示
    - 快捷问题入口
    - _Requirements: 3.1, 3.2, 3.4_
  - [x] 16.4 实现对话历史界面
    - 历史记录列表和分页
    - 删除功能
    - _Requirements: 4.1, 4.2, 4.4, 4.5_
  - [x] 16.5 实现反馈功能
    - 评分和反馈类型选择
    - 反馈提交
    - _Requirements: 5.1, 5.2, 5.3_

- [x] 17. 前端与后端集成
  - [x] 17.1 配置静态文件服务
    - FastAPI 挂载前端静态文件
    - 配置前端页面路由
    - _Requirements: 3.1_

## Notes

- 任务标记 `*` 的为可选测试任务，可跳过以加快 MVP 开发
- 每个任务都引用了具体的需求，确保可追溯性
- Checkpoint 任务用于阶段性验证，确保增量开发的稳定性
- 属性测试使用 hypothesis 库，每个测试至少运行 100 次迭代
- 单元测试和属性测试互补，共同保证代码正确性
