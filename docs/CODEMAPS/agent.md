# Agent系统架构文档

**最后更新**: 2026-03-25  
**核心模块**: `medical_agent/`  
**LLM**: DeepSeek Chat (deepseek-chat)

---

## 📋 目录

- [架构概览](#架构概览)
- [目录结构](#目录结构)
- [核心组件](#核心组件)
- [工具系统](#工具系统)
- [对话记忆](#对话记忆)
- [数据模式](#数据模式)
- [Agent循环](#agent循环)
- [流式输出](#流式输出)
- [错误处理](#错误处理)
- [性能优化](#性能优化)

---

## 🏗️ 架构概览

MedicalAgent 是一个基于 DeepSeek Function Calling 的智能医疗诊断Agent，能够自主选择工具完成复杂的医疗查询任务。

```
┌─────────────────────────────────────────────────────────────┐
│                    MedicalAgent 核心                         │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Agent Loop (最多5轮迭代)                            │  │
│  │  ┌────────────────────────────────────────────────┐ │  │
│  │  │  1. 构建消息 (System + History + User)        │ │  │
│  │  │  2. 调用 LLM (Function Calling)               │ │  │
│  │  │  3. 解析响应 (Text / Tool Calls)              │ │  │
│  │  │  4. 执行工具 (ToolRegistry)                   │ │  │
│  │  │  5. 整合结果 (继续循环或返回)                  │ │  │
│  │  └────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    工具注册器 (ToolRegistry)                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • diagnose_by_symptoms    - 症状诊断               │  │
│  │  • search_disease_info     - 疾病查询               │  │
│  │  • get_treatment_plan      - 治疗方案               │  │
│  │  • search_drugs            - 药物查询               │  │
│  │  • fuzzy_search            - 模糊搜索               │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                 对话记忆 (ConversationMemory)                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  • 会话级别记忆 (session_id)                        │  │
│  │  • 消息历史管理 (最多10条)                          │  │
│  │  • 上下文窗口控制                                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Neo4j 知识图谱服务                         │
│  医疗知识查询和推理                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 目录结构

```
medical_agent/
├── agent.py          # MedicalAgent 核心类
│   └── class MedicalAgent
│       ├── __init__()              - 初始化Agent
│       ├── chat()                  - 同步问答入口
│       ├── _chat_sync()            - 同步问答实现
│       └── _chat_stream()          - 流式问答实现
│
├── tools.py          # 工具注册器
│   └── class ToolRegistry
│       ├── register()              - 注册工具
│       ├── get_tool()              - 获取工具
│       └── get_all_tools()         - 获取所有工具
│
├── memory.py         # 对话记忆管理
│   └── class ConversationMemory
│       ├── add_message()           - 添加消息
│       ├── add_assistant_message_with_tool_calls()
│       ├── get_messages()          - 获取消息历史
│       └── clear()                 - 清空记忆
│
├── schemas.py        # 数据模式定义
│   ├── class ToolCall              - 工具调用模式
│   ├── class AgentResponse         - Agent响应模式
│   └── class Tool                  - 工具定义模式
│
└── __init__.py
```

---

## 🔑 核心组件

### 1. MedicalAgent (agent.py)

**职责**: Agent核心逻辑，协调LLM、工具和记忆

**初始化**:
```python
class MedicalAgent:
    def __init__(
        self,
        api_key: str = None,
        base_url: str = None,
        model: str = "deepseek-chat",
        session_id: str = None,
        max_iterations: int = 5
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = model
        self.memory = ConversationMemory(session_id=session_id)
        self.tool_registry = ToolRegistry()
        self.max_iterations = max_iterations
        
        # 注册所有工具
        self._register_tools()
```

**核心方法**:

#### chat() - 问答入口
```python
def chat(self, message: str, stream: bool = False):
    """
    问答入口方法
    
    Args:
        message: 用户问题
        stream: 是否流式输出
        
    Returns:
        AgentResponse (同步) 或 Generator (流式)
    """
    if stream:
        return self._chat_stream(message)
    else:
        return self._chat_sync(message)
```

#### _chat_sync() - 同步问答
```python
def _chat_sync(self, message: str) -> AgentResponse:
    """
    同步问答实现
    
    流程:
    1. 添加用户消息到记忆
    2. 进入Agent循环 (最多5轮)
    3. 调用LLM获取响应
    4. 如果有工具调用，执行工具
    5. 将工具结果添加到记忆
    6. 继续循环直到LLM返回文本响应
    7. 返回最终结果
    """
    self.memory.add_message("user", message)
    
    for iteration in range(self.max_iterations):
        # 构建消息
        messages = self._build_messages()
        
        # 调用LLM
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_registry.get_openai_tools(),
            temperature=0.7
        )
        
        choice = response.choices[0]
        
        # 如果有工具调用
        if choice.message.tool_calls:
            # 执行工具
            tool_results = self._execute_tools(choice.message.tool_calls)
            
            # 添加到记忆
            self.memory.add_assistant_message_with_tool_calls(
                choice.message.tool_calls
            )
            for result in tool_results:
                self.memory.add_message("tool", result)
            
            continue
        
        # 返回文本响应
        answer = choice.message.content
        self.memory.add_message("assistant", answer)
        
        return AgentResponse(
            answer=answer,
            tool_calls=self._get_all_tool_calls(),
            session_id=self.memory.session_id
        )
    
    # 达到最大迭代次数
    return AgentResponse(
        answer="抱歉，我需要更多时间来处理您的问题。",
        tool_calls=[],
        session_id=self.memory.session_id
    )
```

#### _chat_stream() - 流式问答
```python
def _chat_stream(self, message: str) -> Generator:
    """
    流式问答实现
    
    Yields:
        事件字典:
        - {"type": "tool_start", "tool_id": "...", "tool_name": "...", "arguments": {...}}
        - {"type": "tool_end", "tool_id": "...", "status": "success", "result": "..."}
        - {"type": "chunk", "content": "..."}
        - {"type": "meta", "entities": [...], "session_id": "..."}
    """
    self.memory.add_message("user", message)
    
    all_tool_calls = []
    
    for iteration in range(self.max_iterations):
        messages = self._build_messages()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_registry.get_openai_tools(),
            stream=True
        )
        
        # 处理流式响应
        for chunk in response:
            delta = chunk.choices[0].delta
            
            # 工具调用
            if delta.tool_calls:
                for tool_call in delta.tool_calls:
                    yield {
                        "type": "tool_start",
                        "tool_id": tool_call.id,
                        "tool_name": tool_call.function.name,
                        "arguments": json.loads(tool_call.function.arguments)
                    }
                    
                    # 执行工具
                    result = self._execute_tool(tool_call)
                    
                    yield {
                        "type": "tool_end",
                        "tool_id": tool_call.id,
                        "status": "success",
                        "result": result
                    }
                    
                    all_tool_calls.append(tool_call)
                
                continue
            
            # 文本内容
            if delta.content:
                yield {
                    "type": "chunk",
                    "content": delta.content
                }
        
        # 如果没有更多工具调用，结束
        if not delta.tool_calls:
            break
    
    # 发送元数据
    yield {
        "type": "meta",
        "entities": self._extract_entities(),
        "session_id": self.memory.session_id
    }
```

---

## 🔧 工具系统

### ToolRegistry (tools.py)

**职责**: 工具注册、管理和执行

**工具注册**:
```python
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict
    ):
        """
        注册工具
        
        Args:
            name: 工具名称
            func: 工具函数
            description: 工具描述
            parameters: 参数Schema (JSON Schema格式)
        """
        tool = Tool(
            name=name,
            func=func,
            description=description,
            parameters=parameters
        )
        self.tools[name] = tool
```

### 内置工具列表

#### 1. diagnose_by_symptoms
**功能**: 根据症状列表诊断可能的疾病

**参数**:
```json
{
  "symptoms": ["头痛", "发热", "咳嗽"],
  "top_k": 5
}
```

**返回**:
```json
[
  {
    "name": "感冒",
    "description": "...",
    "match_score": 0.85,
    "matched_symptoms": 3
  }
]
```

#### 2. search_disease_info
**功能**: 查询疾病的详细信息

**参数**:
```json
{
  "disease_name": "糖尿病"
}
```

**返回**:
```json
{
  "disease": {
    "name": "糖尿病",
    "desc": "...",
    "cause": "...",
    "prevent": "..."
  },
  "symptoms": [...],
  "departments": [...]
}
```

#### 3. get_treatment_plan
**功能**: 获取疾病的治疗方案

**参数**:
```json
{
  "disease_name": "高血压"
}
```

**返回**:
```json
{
  "cure_way": "...",
  "cure_lasttime": "...",
  "cured_prob": "..."
}
```

#### 4. search_drugs
**功能**: 查询疾病相关的药物

**参数**:
```json
{
  "disease_name": "感冒"
}
```

**返回**:
```json
[
  {
    "name": "感冒灵",
    "description": "...",
    "usage": "口服",
    "frequency": "一日三次"
  }
]
```

#### 5. fuzzy_search
**功能**: 模糊搜索医疗实体

**参数**:
```json
{
  "keyword": "糖",
  "entity_type": "Disease",
  "limit": 10
}
```

**返回**:
```json
[
  {
    "name": "糖尿病",
    "type": "Disease",
    "description": "..."
  }
]
```

---

## 💾 对话记忆

### ConversationMemory (memory.py)

**职责**: 管理会话级别的对话历史

**核心功能**:

```python
class ConversationMemory:
    def __init__(self, session_id: str = None, max_messages: int = 10):
        self._session_id = session_id or str(uuid.uuid4())
        self.max_messages = max_messages
        self.messages: List[Dict] = []
    
    def add_message(self, role: str, content: str):
        """
        添加消息
        
        Args:
            role: user / assistant / tool / system
            content: 消息内容
        """
        self.messages.append({
            "role": role,
            "content": content
        })
        
        # 保持消息数量在限制内
        if len(self.messages) > self.max_messages:
            # 保留系统消息，删除最旧的用户/助手消息
            self.messages = self._trim_messages()
    
    def add_assistant_message_with_tool_calls(self, tool_calls: List):
        """添加包含工具调用的助手消息"""
        self.messages.append({
            "role": "assistant",
            "content": None,
            "tool_calls": tool_calls
        })
    
    def get_messages(self) -> List[Dict]:
        """获取所有消息"""
        return self.messages
    
    def clear(self):
        """清空记忆"""
        self.messages = []
```

**记忆管理策略**:
- 保留最近10条消息
- 系统消息始终保留
- 超出限制时删除最旧的用户/助手消息
- 工具调用和结果成对保留

---

## 📊 数据模式

### schemas.py

#### ToolCall - 工具调用
```python
@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict
    result: Optional[str] = None
    status: str = "pending"  # pending / success / failed
```

#### AgentResponse - Agent响应
```python
@dataclass
class AgentResponse:
    answer: str
    tool_calls: List[ToolCall]
    session_id: str
    entities: List[Dict] = None
    response_time_ms: int = 0
    
    def to_dict(self) -> Dict:
        return {
            "answer": self.answer,
            "tool_calls": [asdict(tc) for tc in self.tool_calls],
            "session_id": self.session_id,
            "entities": self.entities,
            "response_time_ms": self.response_time_ms
        }
```

#### Tool - 工具定义
```python
@dataclass
class Tool:
    name: str
    func: Callable
    description: str
    parameters: Dict
    
    def to_openai_schema(self) -> Dict:
        """转换为OpenAI Function Calling格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }
```

---

## 🔄 Agent循环

### 循环流程

```
开始
  ↓
添加用户消息到记忆
  ↓
┌─────────────────────────────────┐
│  Agent Loop (最多5轮)           │
│  ┌───────────────────────────┐ │
│  │ 1. 构建消息列表            │ │
│  │    - System Prompt        │ │
│  │    - 历史消息              │ │
│  │    - 当前用户消息          │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 2. 调用LLM                │ │
│  │    - 传入工具列表          │ │
│  │    - 获取响应              │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 3. 解析响应                │ │
│  │    - 文本内容？→ 返回     │ │
│  │    - 工具调用？→ 继续     │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 4. 执行工具                │ │
│  │    - 解析参数              │ │
│  │    - 调用工具函数          │ │
│  │    - 获取结果              │ │
│  └───────────────────────────┘ │
│  ┌───────────────────────────┐ │
│  │ 5. 添加结果到记忆          │ │
│  │    - 工具调用消息          │ │
│  │    - 工具结果消息          │ │
│  └───────────────────────────┘ │
│  ↓                             │
│  回到步骤1 (下一轮迭代)        │
└─────────────────────────────────┘
  ↓
返回最终答案
```

### 终止条件

1. **正常终止**: LLM返回文本内容（不再调用工具）
2. **达到最大迭代次数**: 5轮后强制终止
3. **工具执行失败**: 返回错误信息

---

## 📡 流式输出

### 事件类型

| 事件类型 | 说明 | 数据 |
|---------|------|------|
| `tool_start` | 工具开始执行 | tool_id, tool_name, arguments |
| `tool_end` | 工具执行完成 | tool_id, status, result |
| `chunk` | 文本内容块 | content |
| `meta` | 元数据 | entities, session_id |

### 事件示例

```json
// 工具开始
{
  "type": "tool_start",
  "tool_id": "call_abc123",
  "tool_name": "search_disease_info",
  "arguments": {"disease_name": "糖尿病"}
}

// 工具结束
{
  "type": "tool_end",
  "tool_id": "call_abc123",
  "status": "success",
  "result": "{\"disease\": {...}}"
}

// 文本块
{
  "type": "chunk",
  "content": "糖尿病是一种"
}

// 元数据
{
  "type": "meta",
  "entities": [
    {"type": "Disease", "name": "糖尿病"}
  ],
  "session_id": "session-123"
}
```

---

## ⚠️ 错误处理

### 工具执行错误

```python
def _execute_tool(self, tool_call):
    try:
        tool = self.tool_registry.get_tool(tool_call.function.name)
        if not tool:
            return {"error": f"工具不存在: {tool_call.function.name}"}
        
        args = json.loads(tool_call.function.arguments)
        result = tool.func(**args)
        
        return result
    except Exception as e:
        logger.error(f"工具执行失败: {e}")
        return {"error": str(e)}
```

### LLM调用错误

```python
try:
    response = self.client.chat.completions.create(...)
except OpenAIError as e:
    logger.error(f"LLM调用失败: {e}")
    return AgentResponse(
        answer="抱歉，服务暂时不可用，请稍后再试。",
        tool_calls=[],
        session_id=self.memory.session_id
    )
```

---

## 🚀 性能优化

### 1. 会话级别Agent缓存
在QAService中缓存Agent实例，避免重复初始化。

### 2. 工具结果缓存
对于相同的工具调用参数，缓存结果避免重复查询。

### 3. 记忆窗口控制
限制记忆中的消息数量，控制Token消耗。

### 4. 并行工具执行
当有多个独立的工具调用时，可以并行执行。

---

## 📝 最佳实践

1. **工具设计要单一职责**：每个工具只做一件事
2. **工具描述要清晰**：让LLM能准确理解工具用途
3. **参数验证要严格**：防止无效参数导致错误
4. **错误信息要友好**：返回用户可理解的错误提示
5. **记忆管理要合理**：平衡上下文和Token消耗

---

*本文档由 doc-updater agent 生成 @ 2026-03-25*
