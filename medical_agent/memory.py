"""
对话记忆管理模块
"""

from typing import List, Dict, Any, Optional
from api.core.logger import logger
from datetime import datetime
from collections import deque



class ConversationMemory:
    """
    对话记忆管理
    
    使用 FIFO 策略管理对话历史，超出限制时自动移除最旧的消息。
    支持 OpenAI 消息格式。
    """
    
    def __init__(self, max_messages: int = 10):
        """
        初始化对话记忆
        
        Args:
            max_messages: 最大消息数量（默认 10 条）
        """
        self.max_messages = max_messages
        self._messages: deque = deque(maxlen=max_messages * 2)  # 预留空间给工具调用
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    @property
    def session_id(self) -> str:
        """获取会话 ID"""
        return self._session_id
    
    def add_message(self, role: str, content: str) -> None:
        """
        添加消息
        
        Args:
            role: 角色 (user/assistant/system)
            content: 消息内容
        """
        message = {
            "role": role,
            "content": content
        }
        self._messages.append(message)
        self._trim_messages()
        logger.debug(f"添加消息: role={role}, content={content[:50]}...")
    
    def add_assistant_message_with_tool_calls(
        self, 
        tool_calls: List[Dict[str, Any]],
        content: Optional[str] = None
    ) -> None:
        """
        添加带工具调用的助手消息
        
        Args:
            tool_calls: 工具调用列表
            content: 可选的文本内容
        """
        message = {
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls
        }
        self._messages.append(message)
        self._trim_messages()
    
    def add_tool_result(self, tool_call_id: str, result: str) -> None:
        """
        添加工具执行结果
        
        Args:
            tool_call_id: 工具调用 ID
            result: 执行结果
        """
        message = {
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": result
        }
        self._messages.append(message)
        # 工具结果不计入消息限制
    
    def get_messages(self) -> List[Dict[str, Any]]:
        """
        获取消息列表（OpenAI 格式）
        
        Returns:
            消息列表
        """
        return list(self._messages)
    
    def get_user_messages_count(self) -> int:
        """获取用户消息数量"""
        return sum(1 for m in self._messages if m.get("role") == "user")
    
    def clear(self) -> None:
        """清空记忆"""
        self._messages.clear()
        self._session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info("对话记忆已清空")
    
    def _trim_messages(self) -> None:
        """
        修剪消息，确保用户消息不超过限制
        
        策略：保留最近的 max_messages 轮对话
        """
        user_count = self.get_user_messages_count()
        
        while user_count > self.max_messages and len(self._messages) > 0:
            # 移除最旧的消息
            removed = self._messages.popleft()
            if removed.get("role") == "user":
                user_count -= 1
            logger.debug(f"移除旧消息: role={removed.get('role')}")
    
    def get_context_summary(self) -> str:
        """
        获取对话上下文摘要（用于调试）
        
        Returns:
            上下文摘要字符串
        """
        summary_parts = []
        for msg in self._messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if content:
                summary_parts.append(f"{role}: {content[:100]}...")
            elif msg.get("tool_calls"):
                tool_names = [tc.get("function", {}).get("name", "unknown") 
                             for tc in msg.get("tool_calls", [])]
                summary_parts.append(f"{role}: [调用工具: {', '.join(tool_names)}]")
        
        return "\n".join(summary_parts)
    
    def __len__(self) -> int:
        """返回消息数量"""
        return len(self._messages)
    
    def __bool__(self) -> bool:
        """是否有消息"""
        return len(self._messages) > 0
