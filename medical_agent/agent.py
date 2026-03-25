"""
医疗诊断智能 Agent 核心实现

基于原生 Python + DeepSeek Function Calling
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Generator, Any
from datetime import datetime

from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .schemas import (
    AgentResponse, ToolCall, 
    SYSTEM_PROMPT, DRUG_KEYWORDS, EMERGENCY_KEYWORDS,
    DRUG_DISCLAIMER, EMERGENCY_WARNING
)
from .tools import ToolRegistry, create_default_registry
from .memory import ConversationMemory

logger = logging.getLogger(__name__)


class MedicalAgent:
    """
    医疗诊断智能代理
    
    基于 DeepSeek Function Calling 实现的智能问答 Agent，
    支持多轮对话、工具调用、流式输出。
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "deepseek-chat",
        max_iterations: int = 5,
        memory_limit: int = 10,
        tool_registry: Optional[ToolRegistry] = None
    ):
        """
        初始化 Agent
        
        Args:
            api_key: DeepSeek API Key（默认从环境变量读取）
            base_url: API Base URL（默认从环境变量读取）
            model: 模型名称
            max_iterations: 最大推理迭代次数
            memory_limit: 对话记忆最大消息数
            tool_registry: 工具注册器（默认使用内置工具）
        """
        # 配置
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.base_url = base_url or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        self.model = model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.max_iterations = max_iterations
        
        # 验证 API Key
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY 未设置")
        
        # 初始化 OpenAI 客户端（DeepSeek 兼容）
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # 初始化工具注册器
        self.tool_registry = tool_registry or create_default_registry()
        
        # 初始化对话记忆
        self.memory = ConversationMemory(max_messages=memory_limit)
        
        logger.info(f"MedicalAgent 初始化完成: model={self.model}, tools={len(self.tool_registry)}")
    
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
        # 检查紧急情况
        if self._is_emergency(message):
            emergency_response = self._handle_emergency(message)
            self.memory.add_message("user", message)
            self.memory.add_message("assistant", emergency_response.answer)
            return emergency_response
        
        # 添加用户消息到记忆
        self.memory.add_message("user", message)
        
        try:
            if stream:
                return self._chat_stream(message)
            else:
                return self._chat_sync(message)
        except Exception as e:
            logger.error(f"Agent 处理失败: {e}", exc_info=True)
            error_response = AgentResponse(
                answer=f"抱歉，处理您的问题时出现错误。请稍后重试。",
                error=str(e)
            )
            self.memory.add_message("assistant", error_response.answer)
            return error_response
    
    def _chat_sync(self, message: str) -> AgentResponse:
        """同步处理消息"""
        # 构建消息列表
        messages = self._build_messages()
        
        # 运行 Agent Loop
        response = self._run_agent_loop(messages)
        
        # 添加响应到记忆
        self.memory.add_message("assistant", response.answer)
        
        return response
    
    def _chat_stream(self, message: str) -> Generator[str, None, None]:
        """流式处理消息（简单模式，仅返回文本）"""
        for event in self._chat_stream_events(message):
            if event.get("type") == "chunk":
                yield event.get("content", "")
    
    def chat_stream_events(
        self,
        message: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        流式处理消息（事件模式，返回结构化事件）
        
        事件类型:
        - {"type": "tool_start", "tool_id": "...", "tool_name": "...", "arguments": {...}}
        - {"type": "tool_end", "tool_id": "...", "status": "success|error", "result": "...", "error": "..."}
        - {"type": "chunk", "content": "..."}
        - {"type": "meta", "entities": [...], "tool_calls": [...]}
        - {"type": "error", "message": "..."}
        """
        # 检查紧急情况
        if self._is_emergency(message):
            emergency_response = self._handle_emergency(message)
            self.memory.add_message("user", message)
            self.memory.add_message("assistant", emergency_response.answer)
            yield {"type": "chunk", "content": emergency_response.answer}
            yield {"type": "meta", "entities": [], "tool_calls": []}
            return
        
        self.memory.add_message("user", message)
        
        for event in self._chat_stream_events(message):
            yield event
    
    def _chat_stream_events(self, message: str) -> Generator[Dict[str, Any], None, None]:
        """内部流式事件生成器"""
        messages = self._build_messages()
        tool_calls_history = []
        entities = []
        
        try:
            # 工具调用阶段
            for iteration in range(self.max_iterations):
                response = self._call_llm(messages)
                
                if not response.choices[0].message.tool_calls:
                    break
                
                assistant_message = response.choices[0].message
                tool_calls = assistant_message.tool_calls
                
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in tool_calls
                    ]
                })
                
                for tool_call in tool_calls:
                    tool_name = tool_call.function.name
                    tool_id = tool_call.id
                    try:
                        arguments = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                    
                    # 发送工具开始事件（包含 tool_id）
                    yield {
                        "type": "tool_start",
                        "tool_id": tool_id,
                        "tool_name": tool_name,
                        "arguments": arguments
                    }
                    
                    tc_record = ToolCall(
                        id=tool_id,
                        name=tool_name,
                        arguments=arguments
                    )
                    
                    try:
                        result = self.tool_registry.execute(tool_name, arguments)
                        tc_record.result = result
                        
                        # 提取实体
                        tool_entities = []
                        self._extract_entities(result, tool_entities)
                        entities.extend(tool_entities)
                        
                        # 发送工具结束事件（成功）- 发送完整结果，前端负责显示截断
                        yield {
                            "type": "tool_end",
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "status": "success",
                            "result": result,
                            "entities": tool_entities
                        }
                        
                    except Exception as e:
                        logger.error(f"工具执行失败: {e}")
                        result = json.dumps({
                            "error": str(e),
                            "message": "工具执行失败"
                        }, ensure_ascii=False)
                        tc_record.error = str(e)
                        
                        # 发送工具结束事件（失败）
                        yield {
                            "type": "tool_end",
                            "tool_id": tool_id,
                            "tool_name": tool_name,
                            "status": "error",
                            "error": str(e)
                        }
                    
                    tool_calls_history.append(tc_record)
                    
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": result
                    })
            
            # 流式生成最终回答
            full_response = ""
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    yield {"type": "chunk", "content": content}
            
            # 添加免责声明
            if self._needs_drug_disclaimer(full_response):
                yield {"type": "chunk", "content": DRUG_DISCLAIMER}
                full_response += DRUG_DISCLAIMER
            
            # 保存到记忆
            self.memory.add_message("assistant", full_response)
            
            # 发送元数据事件（替代 done）
            yield {
                "type": "meta",
                "entities": entities,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "name": tc.name,
                        "arguments": tc.arguments,
                        "result": tc.result[:200] + "..." if tc.result and len(tc.result) > 200 else tc.result,
                        "error": tc.error
                    }
                    for tc in tool_calls_history
                ]
            }
            
        except Exception as e:
            logger.error(f"流式输出失败: {e}", exc_info=True)
            yield {"type": "error", "message": str(e)}
            self.memory.add_message("assistant", f"抱歉，生成回答时出现错误: {str(e)}")
    
    def _build_messages(self) -> List[Dict[str, Any]]:
        """构建消息列表"""
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(self.memory.get_messages())
        return messages
    
    def _run_agent_loop(self, messages: List[Dict]) -> AgentResponse:
        """
        运行 Agent 推理循环
        
        Args:
            messages: 消息列表
            
        Returns:
            AgentResponse
        """
        tool_calls_history: List[ToolCall] = []
        entities: List[Dict] = []
        
        for iteration in range(self.max_iterations):
            logger.debug(f"Agent Loop 迭代 {iteration + 1}/{self.max_iterations}")
            
            # 调用 LLM
            response = self._call_llm(messages)
            
            # 检查是否有工具调用
            if not response.choices[0].message.tool_calls:
                # 没有工具调用，生成最终答案
                answer = response.choices[0].message.content or ""
                
                # 添加免责声明
                if self._needs_drug_disclaimer(answer):
                    answer += DRUG_DISCLAIMER
                
                return AgentResponse(
                    answer=answer,
                    tool_calls=tool_calls_history,
                    entities=entities
                )
            
            # 处理工具调用
            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls
            
            # 添加助手消息到消息列表
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })
            
            # 执行每个工具调用
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                logger.info(f"执行工具: {tool_name}, 参数: {arguments}")
                
                # 记录工具调用
                tc_record = ToolCall(
                    id=tool_call.id,
                    name=tool_name,
                    arguments=arguments
                )
                
                try:
                    result = self.tool_registry.execute(tool_name, arguments)
                    tc_record.result = result
                    
                    # 提取实体信息
                    self._extract_entities(result, entities)
                    
                except Exception as e:
                    logger.error(f"工具执行失败: {e}")
                    result = json.dumps({
                        "error": str(e),
                        "message": "工具执行失败，请尝试其他方式"
                    }, ensure_ascii=False)
                    tc_record.error = str(e)
                
                tool_calls_history.append(tc_record)
                
                # 添加工具结果到消息列表
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        # 达到最大迭代次数
        logger.warning(f"达到最大迭代次数 {self.max_iterations}")
        return AgentResponse(
            answer="抱歉，我需要更多信息来回答您的问题。请尝试提供更具体的症状或疾病名称。",
            tool_calls=tool_calls_history,
            entities=entities,
            error="达到最大推理次数"
        )
    
    def _run_tool_calls_phase(self, messages: List[Dict]) -> Dict:
        """
        执行工具调用阶段（用于流式输出前的准备）
        
        Returns:
            {"has_tool_calls": bool, "messages": List[Dict]}
        """
        has_tool_calls = False
        
        for iteration in range(self.max_iterations):
            response = self._call_llm(messages)
            
            if not response.choices[0].message.tool_calls:
                break
            
            has_tool_calls = True
            assistant_message = response.choices[0].message
            tool_calls = assistant_message.tool_calls
            
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in tool_calls
                ]
            })
            
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                try:
                    arguments = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    arguments = {}
                
                try:
                    result = self.tool_registry.execute(tool_name, arguments)
                except Exception as e:
                    result = json.dumps({"error": str(e)}, ensure_ascii=False)
                
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })
        
        return {"has_tool_calls": has_tool_calls, "messages": messages}
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(Exception),
        reraise=True
    )
    def _call_llm(self, messages: List[Dict]):
        """
        调用 LLM（带重试）
        
        Args:
            messages: 消息列表
            
        Returns:
            ChatCompletion 响应
        """
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=self.tool_registry.get_all_tools_schema(),
            tool_choice="auto"
        )
    
    def _extract_entities(self, result: str, entities: List[Dict]) -> None:
        """从工具结果中提取实体"""
        try:
            data = json.loads(result)
            
            # 提取疾病
            if "possible_diseases" in data:
                for disease in data["possible_diseases"]:
                    entities.append({
                        "type": "Disease",
                        "name": disease.get("name"),
                        "score": disease.get("match_score")
                    })
            
            # 提取症状
            if "input_symptoms" in data:
                for symptom in data["input_symptoms"]:
                    entities.append({
                        "type": "Symptom",
                        "name": symptom
                    })
            
            # 提取药品
            if "drugs" in data:
                for drug in data["drugs"]:
                    entities.append({
                        "type": "Drug",
                        "name": drug.get("name")
                    })
                    
        except (json.JSONDecodeError, KeyError):
            pass
    
    def _is_emergency(self, message: str) -> bool:
        """检查是否是紧急情况"""
        return any(keyword in message for keyword in EMERGENCY_KEYWORDS)
    
    def _handle_emergency(self, message: str) -> AgentResponse:
        """处理紧急情况"""
        answer = f"""🚨 **紧急情况提醒**

您描述的情况可能需要紧急医疗处理。请立即采取以下措施：

1. **拨打急救电话 120**
2. 如果在医院附近，请立即前往急诊室
3. 在等待救援时，保持冷静，不要独自一人

{EMERGENCY_WARNING}

如果这不是紧急情况，请重新描述您的症状，我会尽力帮助您。"""
        
        return AgentResponse(answer=answer)
    
    def _needs_drug_disclaimer(self, text: str) -> bool:
        """检查是否需要添加药品免责声明"""
        return any(keyword in text for keyword in DRUG_KEYWORDS)
    
    def clear_memory(self) -> None:
        """清空对话历史"""
        self.memory.clear()
        logger.info("对话历史已清空")
    
    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return self.memory.get_messages()


# 单例模式
_agent_instance: Optional[MedicalAgent] = None


def get_medical_agent() -> MedicalAgent:
    """获取 MedicalAgent 单例"""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = MedicalAgent()
    return _agent_instance
