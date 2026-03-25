# Requirements Document

## Introduction

本文档定义了医疗诊断智能问答系统中 Agent 模块的重构需求。当前系统使用的是固定流程的 GraphRAG 服务，需要重构为具备自主决策能力的智能 Agent，以支持更灵活的多轮对话和工具调用。实现方式可以是 LangChain/LangGraph、原生 Function Calling，或其他 Agent 框架。

## Glossary

- **Medical_Agent**: 医疗诊断智能代理，能够自主选择工具、进行多轮推理的 AI 系统
- **Tool**: Agent 可调用的功能模块，如症状诊断、疾病查询、药品查询等
- **Function_Calling**: LLM 原生的函数调用能力，允许模型决定调用哪个函数
- **GraphRAG_Service**: 图谱检索增强生成服务，负责从知识图谱检索相关信息
- **Conversation_Memory**: 对话记忆模块，存储和管理多轮对话上下文
- **LLM**: 大语言模型，当前使用 DeepSeek（支持 Function Calling）

## Requirements

### Requirement 1: Agent 核心框架

**User Story:** As a developer, I want a properly structured intelligent Agent, so that the system can autonomously decide which tools to use based on user questions.

#### Acceptance Criteria

1. THE Medical_Agent SHALL support LLM Function Calling for tool selection (可选择使用 LangChain、LangGraph 或原生实现)
2. WHEN initialized, THE Medical_Agent SHALL register all available tools with their descriptions and parameters
3. THE Medical_Agent SHALL use a reasoning loop pattern (ReAct 或类似模式) for decision making
4. WHEN a tool call fails, THE Medical_Agent SHALL gracefully handle the error and provide a fallback response
5. THE Medical_Agent SHALL support iterative tool calling (多轮工具调用直到获得满意答案)

### Requirement 2: 工具集成

**User Story:** As a user, I want the agent to intelligently select appropriate tools, so that I can get accurate medical information based on my specific question type.

#### Acceptance Criteria

1. THE Medical_Agent SHALL have access to the following tools:
   - diagnose_by_symptoms: 根据症状诊断疾病
   - search_disease_info: 查询疾病详细信息
   - get_treatment_plan: 获取治疗方案
   - search_drugs: 查询推荐药物
   - fuzzy_search: 模糊搜索医疗实体
2. WHEN a user asks about symptoms, THE Medical_Agent SHALL prioritize using diagnose_by_symptoms tool
3. WHEN a user asks about a specific disease, THE Medical_Agent SHALL use search_disease_info or get_treatment_plan tool
4. WHEN a user asks about medication, THE Medical_Agent SHALL use search_drugs tool
5. THE Medical_Agent SHALL be able to chain multiple tool calls in a single response when needed

### Requirement 3: 对话记忆管理

**User Story:** As a user, I want the agent to remember our conversation context, so that I can have natural multi-turn conversations without repeating information.

#### Acceptance Criteria

1. THE Conversation_Memory SHALL store the last 10 conversation turns by default
2. WHEN a follow-up question references previous context, THE Medical_Agent SHALL use conversation history to understand the reference
3. THE Conversation_Memory SHALL support clearing history on user request
4. WHEN conversation history exceeds the limit, THE Conversation_Memory SHALL remove oldest messages first (FIFO)
5. THE Medical_Agent SHALL include relevant conversation context in its reasoning process

### Requirement 4: 系统提示词优化

**User Story:** As a medical professional, I want the agent to provide professional and safe medical advice, so that users receive accurate information with appropriate disclaimers.

#### Acceptance Criteria

1. THE Medical_Agent SHALL include a system prompt that defines its role as a medical assistant
2. THE Medical_Agent SHALL always base answers on knowledge graph data, not fabricated information
3. WHEN providing drug recommendations, THE Medical_Agent SHALL include a disclaimer to consult a professional doctor
4. THE Medical_Agent SHALL refuse to provide emergency medical advice and recommend calling emergency services instead
5. THE Medical_Agent SHALL use professional but understandable language suitable for patients

### Requirement 5: 流式输出支持

**User Story:** As a user, I want to see the agent's response as it's being generated, so that I don't have to wait for the complete response.

#### Acceptance Criteria

1. THE Medical_Agent SHALL support streaming output mode
2. WHEN streaming is enabled, THE Medical_Agent SHALL yield response chunks as they are generated
3. THE Medical_Agent SHALL also support non-streaming mode for API compatibility
4. WHEN an error occurs during streaming, THE Medical_Agent SHALL properly terminate the stream and report the error

### Requirement 6: 错误处理与降级

**User Story:** As a system administrator, I want robust error handling, so that the system remains stable even when components fail.

#### Acceptance Criteria

1. IF the Neo4j connection fails, THEN THE Medical_Agent SHALL return a graceful error message and suggest retrying
2. IF the LLM API call fails, THEN THE Medical_Agent SHALL retry up to 3 times with exponential backoff
3. IF no relevant entities are found in the knowledge graph, THEN THE Medical_Agent SHALL inform the user and suggest alternative queries
4. THE Medical_Agent SHALL log all errors with appropriate severity levels
5. IF all tools fail, THEN THE Medical_Agent SHALL provide a generic helpful response based on the LLM's knowledge with clear disclaimers

### Requirement 7: 与现有服务集成

**User Story:** As a developer, I want the new Agent to integrate with existing services, so that we can reuse the GraphRAG and Neo4j infrastructure.

#### Acceptance Criteria

1. THE Medical_Agent SHALL use the existing Neo4jService for knowledge graph queries
2. THE Medical_Agent SHALL optionally use GraphRAGService for complex retrieval tasks
3. THE Medical_Agent SHALL be compatible with the existing qa_cli.py interface
4. THE Medical_Agent SHALL be compatible with the existing API endpoints in api/services/qa_service.py
5. THE Medical_Agent SHALL use the same environment variables for configuration (DEEPSEEK_API_KEY, NEO4J_URI, etc.)

### Requirement 8: 实现方式灵活性

**User Story:** As a developer, I want flexibility in choosing the Agent implementation approach, so that I can select the most suitable technology for the project.

#### Acceptance Criteria

1. THE Medical_Agent MAY be implemented using one of the following approaches:
   - 原生 Python + OpenAI Function Calling API
   - LangChain/LangGraph Agent 框架
   - 其他轻量级 Agent 框架
2. THE Medical_Agent SHALL abstract the implementation details behind a unified interface
3. WHEN switching implementation approaches, THE Medical_Agent interface SHALL remain unchanged
4. THE Medical_Agent SHALL minimize external dependencies where possible
