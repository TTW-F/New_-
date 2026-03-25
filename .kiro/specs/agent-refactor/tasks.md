# Implementation Plan: Medical Agent Refactor

## Overview

基于原生 Python + DeepSeek Function Calling 实现医疗诊断智能 Agent，替换当前无法运行的 Agent.py。采用增量开发方式，先实现核心功能，再逐步完善。

## Tasks

- [x] 1. 创建项目结构和基础模块
  - 创建 `medical_agent/` 目录结构
  - 创建 `__init__.py`、`schemas.py` 基础文件
  - 定义 AgentResponse、ToolCall 等数据类
  - _Requirements: 1.1, 1.2_

- [x] 2. 实现 ToolRegistry 工具注册器
  - [x] 2.1 实现 ToolRegistry 类
    - 实现 register()、get_tool()、get_all_tools_schema() 方法
    - 实现 execute() 方法执行工具
    - _Requirements: 1.2, 2.1_
  - [ ]* 2.2 编写 ToolRegistry 单元测试
    - 测试工具注册和获取
    - 测试 Schema 生成正确性
    - _Requirements: 1.2_

- [x] 3. 实现 ConversationMemory 对话记忆
  - [x] 3.1 实现 ConversationMemory 类
    - 实现 add_message()、get_messages()、clear() 方法
    - 实现 FIFO 消息管理（默认 10 条）
    - _Requirements: 3.1, 3.3, 3.4_
  - [ ]* 3.2 编写属性测试：Memory FIFO 行为
    - **Property 2: Memory FIFO Behavior**
    - **Validates: Requirements 3.1, 3.4**

- [x] 4. 实现 MedicalAgent 核心类
  - [x] 4.1 实现 Agent 初始化和配置
    - 初始化 DeepSeek 客户端
    - 注册所有医疗工具
    - 设置系统提示词
    - _Requirements: 1.1, 1.2, 4.1_
  - [x] 4.2 实现 Agent Loop 推理循环
    - 实现 _run_agent_loop() 方法
    - 支持多轮工具调用
    - 实现最大迭代次数限制
    - _Requirements: 1.3, 1.5, 2.5_
  - [x] 4.3 实现 chat() 主方法
    - 支持同步和流式输出
    - 集成对话记忆
    - _Requirements: 5.1, 5.2, 5.3_
  - [ ]* 4.4 编写属性测试：Agent 循环终止保证
    - **Property 6: Tool Call Iteration Termination**
    - **Validates: Requirements 1.5**

- [x] 5. Checkpoint - 核心功能验证
  - 确保所有测试通过
  - 验证基本问答功能可用
  - 如有问题请询问用户

- [x] 6. 实现错误处理和重试机制
  - [x] 6.1 实现 LLM 调用重试
    - 使用 tenacity 库实现指数退避重试
    - 最多重试 3 次
    - _Requirements: 6.2_
  - [x] 6.2 实现工具执行错误处理
    - 捕获工具执行异常
    - 返回友好错误消息
    - _Requirements: 1.4, 6.1, 6.3_
  - [ ]* 6.3 编写属性测试：错误处理优雅降级
    - **Property 3: Error Handling Graceful Degradation**
    - **Validates: Requirements 6.1, 6.2, 6.3, 6.5**

- [x] 7. 注册医疗工具
  - [x] 7.1 适配现有工具到新 Agent
    - 注册 diagnose_by_symptoms
    - 注册 search_disease_info
    - 注册 get_treatment_plan
    - 注册 search_drugs
    - 注册 fuzzy_search
    - _Requirements: 2.1_
  - [ ]* 7.2 编写属性测试：工具选择正确性
    - **Property 1: Tool Selection Correctness**
    - **Validates: Requirements 2.2, 2.3, 2.4**

- [x] 8. 实现安全和免责声明
  - [x] 8.1 添加药品免责声明逻辑
    - 检测响应中的药品相关内容
    - 自动添加免责声明
    - _Requirements: 4.3_
  - [x] 8.2 添加紧急情况处理
    - 检测紧急关键词
    - 建议立即就医
    - _Requirements: 4.4_
  - [ ]* 8.3 编写属性测试：药品免责声明
    - **Property 4: Drug Disclaimer Inclusion**
    - **Validates: Requirements 4.3**

- [x] 9. Checkpoint - 功能完整性验证
  - 确保所有测试通过
  - 验证错误处理和安全功能
  - 如有问题请询问用户

- [x] 10. 集成现有服务
  - [x] 10.1 集成 Neo4jService
    - 确保工具使用现有 Neo4jService
    - _Requirements: 7.1_
  - [x] 10.2 更新 qa_cli.py 使用新 Agent
    - 替换 GraphRAGService 为 MedicalAgent
    - 保持 CLI 接口不变
    - _Requirements: 7.3_
  - [ ]* 10.3 编写集成测试
    - 测试与 Neo4jService 集成
    - 测试 CLI 兼容性
    - _Requirements: 7.1, 7.3_

- [x] 11. 流式输出完善
  - [x] 11.1 实现流式输出
    - 实现 chat(stream=True) 模式
    - 正确处理流式错误
    - _Requirements: 5.1, 5.2, 5.4_
  - [ ]* 11.2 编写属性测试：流式输出有效性
    - **Property 5: Streaming Chunk Validity**
    - **Validates: Requirements 5.2**

- [x] 12. 清理和文档
  - [x] 12.1 删除或重命名旧 Agent.py
    - 备份旧文件
    - 创建新的入口点
    - _Requirements: 7.5_
  - [x] 12.2 更新 README 文档
    - 添加新 Agent 使用说明
    - 更新配置说明

- [x] 13. Final Checkpoint - 完整功能验证
  - 确保所有测试通过
  - 验证与现有系统兼容
  - 如有问题请询问用户

- [x] 14. 集成新 Agent 到 API QA 服务
  - [x] 14.1 重构 qa_service.py 使用 MedicalAgent
    - 替换 GraphRAGService 为 MedicalAgent
    - 支持会话级别的 Agent 实例管理
    - 保持响应格式兼容
    - _Requirements: 7.4_
  - [x] 14.2 更新 qa.py 路由支持真正的流式输出
    - 使用 MedicalAgent 的原生流式输出
    - 更新健康检查端点
    - _Requirements: 5.1, 5.2, 7.4_
  - [x] 14.3 添加会话管理支持
    - 按 session_id 管理 Agent 实例
    - 支持清空对话历史 API
    - _Requirements: 3.2, 3.3_

- [ ] 15. Final Checkpoint - API 集成验证
  - 确保 API 端点正常工作
  - 验证流式输出功能
  - 如有问题请询问用户

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
