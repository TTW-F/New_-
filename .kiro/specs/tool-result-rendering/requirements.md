# Requirements Document

## Introduction

本文档定义了智能医疗问答系统中工具调用结果渲染优化的需求。当前系统在流式响应中返回的工具调用结果（如症状诊断、疾病查询等）以原始JSON格式显示，用户难以阅读。目标是将这些JSON数据转换为用户友好的可读格式，提升用户体验。

## Glossary

- **Tool_Result**: 工具调用返回的结果数据，通常为JSON格式
- **Tool_Card**: 前端显示工具调用状态和结果的卡片组件
- **Result_Renderer**: 工具结果渲染器，将JSON数据转换为可读HTML
- **Symptom_Diagnosis**: 症状诊断工具，返回可能的疾病列表
- **Disease_Search**: 疾病查询工具，返回疾病详细信息
- **Drug_Search**: 药品查询工具，返回药品信息
- **Fuzzy_Search**: 模糊搜索工具，返回匹配的医疗实体

## Requirements

### Requirement 1: 症状诊断结果渲染

**User Story:** As a user, I want to see symptom diagnosis results in a readable format, so that I can easily understand the possible diseases and their match scores.

#### Acceptance Criteria

1. WHEN the Symptom_Diagnosis tool returns results, THE Result_Renderer SHALL display input symptoms as a tag list
2. WHEN displaying possible diseases, THE Result_Renderer SHALL show each disease with its name, description, and match score
3. THE Result_Renderer SHALL display match scores as percentage bars or badges
4. WHEN a disease has matched symptoms, THE Result_Renderer SHALL highlight them
5. IF the result contains no possible diseases, THEN THE Result_Renderer SHALL display a friendly "未找到匹配疾病" message

### Requirement 2: 疾病查询结果渲染

**User Story:** As a user, I want to see disease information in a structured format, so that I can quickly understand the disease details.

#### Acceptance Criteria

1. WHEN the Disease_Search tool returns results, THE Result_Renderer SHALL display disease name prominently
2. THE Result_Renderer SHALL show disease description in a readable paragraph format
3. WHEN the result includes symptoms, THE Result_Renderer SHALL display them as a tag list
4. WHEN the result includes treatments, THE Result_Renderer SHALL display them in a structured list
5. IF the disease is not found, THEN THE Result_Renderer SHALL display a "未找到该疾病信息" message

### Requirement 3: 模糊搜索结果渲染

**User Story:** As a user, I want to see fuzzy search results in an organized list, so that I can browse and understand the matched entities.

#### Acceptance Criteria

1. WHEN the Fuzzy_Search tool returns results, THE Result_Renderer SHALL display the search keyword and entity type
2. THE Result_Renderer SHALL display each result item with its name, type, and description
3. THE Result_Renderer SHALL limit description length and provide truncation with ellipsis
4. WHEN multiple results are returned, THE Result_Renderer SHALL display them in a scrollable list
5. IF no results are found, THEN THE Result_Renderer SHALL display a "未找到相关结果" message

### Requirement 4: 药品查询结果渲染

**User Story:** As a user, I want to see drug information in a clear format, so that I can understand the medication details.

#### Acceptance Criteria

1. WHEN the Drug_Search tool returns results, THE Result_Renderer SHALL display drug name prominently
2. THE Result_Renderer SHALL show drug usage, dosage, and contraindications in separate sections
3. WHEN the result includes side effects, THE Result_Renderer SHALL display them as warning items
4. IF the drug is not found, THEN THE Result_Renderer SHALL display a "未找到该药品信息" message

### Requirement 5: 通用渲染降级

**User Story:** As a developer, I want a fallback rendering mechanism, so that unknown tool results are still displayed in a readable format.

#### Acceptance Criteria

1. WHEN an unknown tool type returns results, THE Result_Renderer SHALL attempt to render it as formatted JSON
2. THE Result_Renderer SHALL use syntax highlighting for JSON display
3. THE Result_Renderer SHALL collapse long JSON content with an expand/collapse toggle
4. IF JSON parsing fails, THEN THE Result_Renderer SHALL display the raw text content

### Requirement 6: 工具卡片折叠功能

**User Story:** As a user, I want to collapse and expand tool result cards, so that I can focus on the information I need.

#### Acceptance Criteria

1. THE Tool_Card SHALL have a clickable header to toggle collapse/expand state
2. WHEN a tool is running, THE Tool_Card SHALL be expanded by default
3. WHEN a tool completes, THE Tool_Card SHALL remain expanded until user collapses it
4. THE Tool_Card SHALL remember collapse state during the current session
5. WHEN collapsed, THE Tool_Card SHALL show only the tool name and status badge

