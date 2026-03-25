# Requirements Document

## Introduction

本需求文档定义了医疗诊断智能问答系统的用户管理和 API 服务模块。该模块将为现有的 GraphRAG 问答核心提供用户认证、会话管理、对话历史持久化和 RESTful API 接口，使系统能够支持多用户并发访问和 Web 前端集成。

## Glossary

- **User_Manager**: 用户管理服务，负责用户注册、登录、认证和权限管理
- **Session_Manager**: 会话管理服务，负责用户会话的创建、维护和过期处理
- **Conversation_Service**: 对话服务，负责对话历史的存储、检索和管理
- **API_Server**: RESTful API 服务器，提供 HTTP 接口供前端调用
- **GraphRAG_Service**: 现有的图谱检索增强生成服务（已实现）
- **JWT_Token**: JSON Web Token，用于用户身份认证的令牌
- **User_Type**: 用户类型，包括 doctor（医生）、patient（患者）、admin（管理员）

## Requirements

### Requirement 1: 用户注册

**User Story:** As a 新用户, I want 注册账号, so that 我可以使用医疗问答系统并保存我的对话历史。

#### Acceptance Criteria

1. WHEN 用户提交注册信息（用户名、邮箱、密码、用户类型）THEN THE User_Manager SHALL 验证信息格式并创建新用户账号
2. WHEN 用户名或邮箱已存在 THEN THE User_Manager SHALL 返回明确的错误信息，说明冲突字段
3. WHEN 密码不符合安全要求（少于8位或缺少数字/字母组合）THEN THE User_Manager SHALL 拒绝注册并返回密码要求说明
4. WHEN 注册成功 THEN THE User_Manager SHALL 对密码进行哈希加密后存储到 MySQL 数据库
5. WHEN 注册成功 THEN THE User_Manager SHALL 返回用户基本信息（不含密码）和成功状态

### Requirement 2: 用户登录与认证

**User Story:** As a 已注册用户, I want 登录系统, so that 我可以访问我的对话历史和个性化服务。

#### Acceptance Criteria

1. WHEN 用户提交正确的用户名和密码 THEN THE User_Manager SHALL 验证凭据并生成 JWT_Token
2. WHEN 用户名或密码错误 THEN THE User_Manager SHALL 返回统一的"用户名或密码错误"信息，不泄露具体错误原因
3. WHEN 登录成功 THEN THE Session_Manager SHALL 创建用户会话并返回 JWT_Token 和用户信息
4. WHEN JWT_Token 过期（默认24小时）THEN THE API_Server SHALL 拒绝请求并返回 401 状态码
5. WHEN 用户请求退出登录 THEN THE Session_Manager SHALL 使当前 JWT_Token 失效

### Requirement 3: 问答 API 接口

**User Story:** As a 前端开发者, I want 调用问答 API, so that 我可以在 Web 界面中集成医疗问答功能。

#### Acceptance Criteria

1. WHEN 用户提交问题到 /api/v1/qa 端点 THEN THE API_Server SHALL 调用 GraphRAG_Service 处理问题并返回答案
2. WHEN 请求包含有效的 JWT_Token THEN THE API_Server SHALL 将对话记录保存到用户的对话历史
3. WHEN 请求不包含 JWT_Token THEN THE API_Server SHALL 允许匿名查询但不保存对话历史
4. THE API_Server SHALL 在响应中包含答案、识别的实体、引用来源和响应时间
5. WHEN GraphRAG_Service 处理失败 THEN THE API_Server SHALL 返回 500 状态码和错误描述

### Requirement 4: 对话历史管理

**User Story:** As a 登录用户, I want 查看和管理我的对话历史, so that 我可以回顾之前的问诊记录。

#### Acceptance Criteria

1. WHEN 用户请求对话历史 THEN THE Conversation_Service SHALL 返回该用户的所有对话记录，按时间倒序排列
2. WHEN 用户指定 session_id THEN THE Conversation_Service SHALL 只返回该会话的对话记录
3. WHEN 保存对话记录 THEN THE Conversation_Service SHALL 存储问题、答案、识别的实体、引用来源和响应时间
4. WHEN 用户请求删除对话记录 THEN THE Conversation_Service SHALL 软删除指定记录（标记为已删除但不物理删除）
5. THE Conversation_Service SHALL 支持分页查询，默认每页20条记录

### Requirement 5: 用户反馈

**User Story:** As a 用户, I want 对问答结果提供反馈, so that 系统可以不断改进回答质量。

#### Acceptance Criteria

1. WHEN 用户提交反馈（评分1-5、反馈类型、评论）THEN THE Conversation_Service SHALL 保存反馈到数据库
2. WHEN 反馈关联的对话不存在 THEN THE Conversation_Service SHALL 返回 404 错误
3. THE Conversation_Service SHALL 支持的反馈类型包括：helpful（有帮助）、incorrect（不准确）、unclear（不清晰）、other（其他）

### Requirement 6: API 安全与限流

**User Story:** As a 系统管理员, I want API 具备安全防护, so that 系统不会被滥用或攻击。

#### Acceptance Criteria

1. THE API_Server SHALL 对所有请求进行输入验证，防止 SQL 注入和 XSS 攻击
2. THE API_Server SHALL 实现请求速率限制，匿名用户每分钟最多10次请求，登录用户每分钟最多60次请求
3. WHEN 请求超过速率限制 THEN THE API_Server SHALL 返回 429 状态码和重试时间
4. THE API_Server SHALL 记录所有请求日志，包括请求时间、用户ID、端点、响应状态和响应时间
5. THE API_Server SHALL 使用 HTTPS 传输（生产环境）

### Requirement 7: 健康检查与监控

**User Story:** As a 运维人员, I want 监控系统健康状态, so that 我可以及时发现和处理问题。

#### Acceptance Criteria

1. THE API_Server SHALL 提供 /health 端点返回系统健康状态
2. WHEN 健康检查请求到达 THEN THE API_Server SHALL 检查 MySQL、Neo4j、Redis 连接状态
3. THE API_Server SHALL 在健康检查响应中包含各组件状态和系统版本信息
4. WHEN 任一组件不可用 THEN THE API_Server SHALL 返回 503 状态码和具体不可用组件信息
