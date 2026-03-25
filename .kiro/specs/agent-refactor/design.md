# Design Document: Medical Agent Refactor

## Overview

本设计文档描述医疗诊断智能问答系统 Agent 模块的重构方案。采用原生 Python + DeepSeek Function Calling 实现，不依赖 LangChain 等重型框架，保持代码轻量和可控。

核心设计理念：
- **轻量化**：最小化外部依赖，仅使用 OpenAI SDK（DeepSeek 兼容）
- **可扩展**：工具注册机制，易于添加新工具
- **健壮性**：完善的错误处理和重试机制
- **可测试**：清晰的接口设计，便于单元测试

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     MedicalAgent                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                  Agent Loop                          │   │
│  │  ┌──────────┐    ┌──────────┐    ┌──────────┐      │   │
│  │  │  LLM     │───▶│  Tool    │───▶│ Response │      │   │
│  │  │  Call    │    │  Execute │    │ Generate │      │   │
│  │  └──────────┘    └──────────┘    └──────────┘      │   │
│  │       ▲               │                             │   │
│  │       └───────────────┘ (loop until done)          │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│  ┌────────────────────────┼────────────────────────────┐   │
│  │                        ▼                             │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐          │   │
│  │  │ Tool     │  │ Memory   │  │ Config   │          │   │
│  │  │ Registry │  │ Manager  │  │ Manager  │          │   │
│  │  └──────────┘  └──────────┘  └──────────┘          │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│ Neo4jService │   │ DeepSeek API │   │ GraphRAG     │
│              │   │              │   │ Service      │
└──────────────┘   └──────────────┘   └──────────────┘
```

## Components and Interfaces

### 1. MedicalAgent (主类)

```python
class MedicalAgent:
    """医疗诊断智能代理"""
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "deepseek-chat",
        max_iterations: int = 5,
        memory_limit: int = 10
    ):
        """初始化 Agent"""
        pass
    
    def chat(
        self, 
        message: str, 
        stream: bool = False
    ) -> Union[AgentResponse, Generator[str, None, None]]:
        """
        处理用户消息
        
        Args:
            message: 用户输入
            stream: 是否流式输出
            
        Returns:
            AgentResponse 或流式生成器
        """
        pass
    
    def clear_memory(self) -> None:
        """清空对话历史"""
        pass
    
    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        pass
```

### 2. ToolRegistry (工具注册器)

```python
class ToolRegistry:
    """工具注册和管理"""
    
    def register(
        self, 
        name: str, 
        func: Callable, 
        description: str, 
        parameters: Dict
    ) -> None:
        """注册工具"""
        pass
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        pass
    
    def get_all_tools_schema(self) -> List[Dict]:
        """获取所有工具的 OpenAI Function Schema"""
        pass
    
    def execute(self, name: str, arguments: Dict) -> str:
        """执行工具"""
        pass
```

### 3. ConversationMemory (对话记忆)

```python
class ConversationMemory:
    """对话记忆管理"""
    
    def __init__(self, max_messages: int = 10):
        """初始化，设置最大消息数"""
        pass
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息"""
        pass
    
    def add_tool_call(self, tool_call: Dict, result: str) -> None:
        """添加工具调用记录"""
        pass
    
    def get_messages(self) -> List[Dict]:
        """获取消息列表（OpenAI 格式）"""
        pass
    
    def clear(self) -> None:
        """清空记忆"""
        pass
```

### 4. AgentResponse (响应数据类)

```python
@dataclass
class AgentResponse:
    """Agent 响应"""
    answer: str                      # 最终答案
    tool_calls: List[ToolCall]       # 工具调用记录
    entities: List[Dict]             # 识别的实体
    citations: List[Dict]            # 引用来源
    error: Optional[str] = None      # 错误信息
```

## Data Models

### Tool Schema (OpenAI Function Calling 格式)

```python
TOOL_SCHEMA = {
    "type": "function",
    "function": {
        "name": "diagnose_by_symptoms",
        "description": "根据症状列表诊断可能的疾病",
        "parameters": {
            "type": "object",
            "properties": {
                "symptoms": {
                    "type": "string",
                    "description": "症状列表，用逗号分隔，如：头痛,发热,咳嗽"
                }
            },
            "required": ["symptoms"]
        }
    }
}
```

### Message Format (对话消息格式)

```python
# 用户消息
{"role": "user", "content": "我头痛发热，可能是什么病？"}

# 助手消息（带工具调用）
{
    "role": "assistant",
    "content": None,
    "tool_calls": [{
        "id": "call_xxx",
        "type": "function",
        "function": {
            "name": "diagnose_by_symptoms",
            "arguments": '{"symptoms": "头痛,发热"}'
        }
    }]
}

# 工具结果消息
{
    "role": "tool",
    "tool_call_id": "call_xxx",
    "content": '{"possible_diseases": [...]}'
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Tool Selection Correctness

*For any* user question about symptoms, diseases, or medications, the Medical_Agent SHALL select the appropriate tool based on question type:
- Symptom questions → diagnose_by_symptoms
- Disease questions → search_disease_info or get_treatment_plan  
- Medication questions → search_drugs

**Validates: Requirements 2.2, 2.3, 2.4**

### Property 2: Memory FIFO Behavior

*For any* sequence of N messages added to ConversationMemory where N > max_messages, the memory SHALL contain exactly max_messages messages, and the oldest (N - max_messages) messages SHALL be removed.

**Validates: Requirements 3.1, 3.4**

### Property 3: Error Handling Graceful Degradation

*For any* error condition (Neo4j failure, LLM failure, tool failure), the Medical_Agent SHALL return a valid AgentResponse with an appropriate error message, never raising an unhandled exception to the caller.

**Validates: Requirements 6.1, 6.2, 6.3, 6.5**

### Property 4: Drug Disclaimer Inclusion

*For any* response that mentions drug or medication recommendations, the response text SHALL contain a disclaimer phrase indicating users should consult a professional doctor.

**Validates: Requirements 4.3**

### Property 5: Streaming Chunk Validity

*For any* streaming response, each yielded chunk SHALL be a non-empty string, and the concatenation of all chunks SHALL equal the complete response.

**Validates: Requirements 5.2**

### Property 6: Tool Call Iteration Termination

*For any* user query, the Agent loop SHALL terminate within max_iterations iterations, either by producing a final answer or by reaching the iteration limit.

**Validates: Requirements 1.5**

## Error Handling

### 错误类型和处理策略

| 错误类型 | 处理策略 | 重试次数 |
|---------|---------|---------|
| Neo4j 连接失败 | 返回友好错误消息，建议稍后重试 | 0 |
| LLM API 调用失败 | 指数退避重试 | 3 |
| 工具执行失败 | 记录错误，继续尝试其他工具 | 1 |
| JSON 解析失败 | 使用默认值或跳过 | 0 |
| 超时 | 返回部分结果或错误消息 | 0 |

### 错误响应格式

```python
AgentResponse(
    answer="抱歉，系统暂时无法处理您的请求。请稍后重试。",
    tool_calls=[],
    entities=[],
    citations=[],
    error="Neo4j connection failed: Connection refused"
)
```

## Testing Strategy

### 单元测试

1. **ToolRegistry 测试**
   - 工具注册和获取
   - Schema 生成正确性
   - 工具执行

2. **ConversationMemory 测试**
   - 消息添加和获取
   - FIFO 行为验证
   - 清空功能

3. **MedicalAgent 测试**
   - 初始化配置
   - 工具选择逻辑（使用 Mock LLM）
   - 错误处理

### 属性测试 (Property-Based Testing)

使用 `hypothesis` 库进行属性测试：

1. **Property 1**: 工具选择正确性
   - 生成随机问题类型，验证工具选择

2. **Property 2**: 内存 FIFO 行为
   - 生成随机消息序列，验证内存限制

3. **Property 3**: 错误处理
   - 模拟各种错误条件，验证优雅降级

4. **Property 4**: 药品免责声明
   - 生成包含药品的响应，验证免责声明存在

### 集成测试

1. 与 Neo4jService 集成
2. 与现有 qa_cli.py 兼容性
3. 与 API 端点兼容性

## Implementation Notes

### 文件结构

```
medical_agent/
├── __init__.py
├── agent.py           # MedicalAgent 主类
├── tools.py           # 工具定义和注册
├── memory.py          # ConversationMemory
├── schemas.py         # 数据模型和 Schema
└── utils.py           # 工具函数
```

### 关键实现细节

1. **Agent Loop 实现**
```python
def _run_agent_loop(self, messages: List[Dict]) -> AgentResponse:
    for i in range(self.max_iterations):
        response = self._call_llm(messages)
        
        if not response.tool_calls:
            # 没有工具调用，返回最终答案
            return self._build_response(response.content)
        
        # 执行工具调用
        for tool_call in response.tool_calls:
            result = self._execute_tool(tool_call)
            messages.append({"role": "tool", ...})
        
        messages.append(response.to_dict())
    
    # 达到最大迭代次数
    return self._build_response("已达到最大推理次数")
```

2. **重试机制**
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    retry=retry_if_exception_type(APIError)
)
def _call_llm(self, messages: List[Dict]) -> ChatCompletion:
    return self.client.chat.completions.create(
        model=self.model,
        messages=messages,
        tools=self.tool_registry.get_all_tools_schema()
    )
```

3. **系统提示词**
```python
SYSTEM_PROMPT = """你是一个专业的医疗诊断助手。你可以使用以下工具来帮助用户：

1. diagnose_by_symptoms - 根据症状诊断可能的疾病
2. search_disease_info - 查询疾病详细信息
3. get_treatment_plan - 获取治疗方案
4. search_drugs - 查询推荐药物
5. fuzzy_search - 模糊搜索医疗实体

重要规则：
- 所有回答必须基于工具返回的知识库信息，不要编造内容
- 涉及用药建议时，必须提醒用户咨询专业医生
- 遇到紧急情况（如胸痛、呼吸困难），建议立即就医或拨打急救电话
- 使用专业但通俗易懂的语言
"""
```
