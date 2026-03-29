"""
问答服务

集成 MedicalAgent 服务，处理问答请求
支持会话级别的 Agent 实例管理和真正的流式输出
"""

import time
import uuid
from typing import Optional, Dict, Any, Generator
from sqlalchemy.orm import Session

from api.services.conversation_service import ConversationService
from api.core.logger import logger



# 会话级别的 Agent 实例缓存
_session_agents: Dict[str, "MedicalAgent"] = {}


class QAService:
    """问答服务类"""
    
    def __init__(self, db: Session):
        """
        初始化问答服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.conversation_service = ConversationService(db)
    
    def _get_agent(self, session_id: str) -> "MedicalAgent":
        """
        获取或创建会话对应的 Agent 实例
        
        Args:
            session_id: 会话 ID
            
        Returns:
            MedicalAgent 实例
        """
        global _session_agents
        
        if session_id not in _session_agents:
            try:
                from medical_agent import MedicalAgent
                from api.core.config import settings
                
                # 使用 API 配置中的 DeepSeek 设置
                _session_agents[session_id] = MedicalAgent(
                    api_key=settings.DEEPSEEK_API_KEY,
                    base_url=settings.DEEPSEEK_BASE_URL,
                    model=settings.DEEPSEEK_MODEL
                )
                # 使用结构化日志记录会话创建
                logger.bind(
                    session_id=session_id,
                    agent_count=len(_session_agents)
                ).success(f"创建新的 MedicalAgent 实例")
            except Exception as e:
                logger.bind(session_id=session_id).error(f"MedicalAgent 初始化失败: {e}")
                raise RuntimeError(f"问答服务不可用: {e}")
        
        return _session_agents[session_id]
    
    def restore_session_context(
        self,
        session_id: str,
        user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        恢复会话上下文
        
        从数据库加载历史对话并恢复到 Agent 的记忆中
        
        Args:
            session_id: 会话 ID
            user_id: 用户 ID（可选）
            
        Returns:
            恢复结果
        """
        try:
            # 获取或创建 Agent
            agent = self._get_agent(session_id)
            
            # 清空当前记忆
            agent.clear_memory()
            
            # 从数据库加载历史对话
            if user_id:
                conversations = self.conversation_service.get_session_conversations(
                    user_id=user_id,
                    session_id=session_id
                )
                
                # 按时间顺序恢复对话
                for conv in conversations:
                    # 添加用户消息
                    agent.memory.add_message("user", conv.question)
                    # 添加助手回答
                    agent.memory.add_message("assistant", conv.answer)
                
                logger.info(f"已为会话 {session_id} 恢复 {len(conversations)} 轮对话")
                
                return {
                    "success": True,
                    "session_id": session_id,
                    "restored_count": len(conversations),
                    "message": f"已恢复 {len(conversations)} 轮对话"
                }
            else:
                return {
                    "success": False,
                    "session_id": session_id,
                    "message": "需要用户 ID 才能恢复历史对话"
                }
                
        except Exception as e:
            logger.error(f"恢复会话上下文失败: {e}", exc_info=True)
            return {
                "success": False,
                "session_id": session_id,
                "message": f"恢复失败: {str(e)}"
            }
    
    def process_question(
        self,
        question: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        处理问答请求（同步模式）
        
        Args:
            question: 用户问题
            user_id: 用户 ID（可选，用于保存对话历史）
            session_id: 会话 ID（可选）
            
        Returns:
            问答结果字典
        """
        start_time = time.time()
        
        # 生成问题 ID
        question_id = str(uuid.uuid4())[:8]
        
        # 如果没有提供 session_id，生成一个新的
        if not session_id:
            session_id = str(uuid.uuid4())[:16]
        
        # 创建带上下文的日志记录器
        req_logger = logger.bind(
            question_id=question_id,
            session_id=session_id,
            user_id=user_id
        )
        
        req_logger.info(f"收到问答请求: {question[:50]}...")
        
        try:
            # 获取会话对应的 Agent
            agent = self._get_agent(session_id)
            
            # 调用 Agent 处理问题
            req_logger.debug("调用 MedicalAgent 处理问题")
            result = agent.chat(question, stream=False)
            
            # 计算响应时间
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 转换实体格式
            entities = [
                {"type": e.get("type", ""), "name": e.get("name", "")}
                for e in result.entities
            ] if result.entities else []
            
            # 构建引用信息
            citations = []
            for tc in result.tool_calls:
                if tc.result:
                    citations.append({
                        "tool": tc.name,
                        "query": tc.arguments
                    })
            
            # 构建响应
            response = {
                "question_id": question_id,
                "session_id": session_id,
                "question": question,
                "answer": result.answer,
                "entities": entities,
                "citations": citations,
                "tool_calls": [
                    {
                        "name": tc.name,
                        "arguments": tc.arguments,
                        "result": tc.result[:200] + "..." if tc.result and len(tc.result) > 200 else tc.result
                    }
                    for tc in result.tool_calls
                ],
                "response_time_ms": response_time_ms
            }
            
            # 如果有错误，添加到响应
            if result.error:
                response["error"] = result.error
            
            # 如果有用户 ID，保存对话历史
            if user_id:
                self._save_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    question=question,
                    response=response
                )
            
            req_logger.bind(
                response_time_ms=response_time_ms,
                entities_count=len(entities),
                tool_calls_count=len(result.tool_calls)
            ).success(f"问答处理完成")
            return response
            
        except Exception as e:
            req_logger.exception(f"问答处理失败: {e}")
            
            # 计算响应时间
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return {
                "question_id": question_id,
                "session_id": session_id,
                "question": question,
                "answer": f"抱歉，处理您的问题时出现错误。请稍后重试。",
                "entities": [],
                "citations": [],
                "tool_calls": [],
                "response_time_ms": response_time_ms,
                "error": str(e)
            }
    
    def process_question_stream(
        self,
        question: str,
        user_id: Optional[int] = None,
        session_id: Optional[str] = None
    ) -> Generator[Dict[str, Any], None, None]:
        """
        处理问答请求（流式模式）
        
        Args:
            question: 用户问题
            user_id: 用户 ID（可选）
            session_id: 会话 ID（可选）
            
        Yields:
            流式响应事件:
            - {"type": "tool_start", "tool_id": "...", "tool_name": "...", "arguments": {...}}
            - {"type": "tool_end", "tool_id": "...", "tool_name": "...", "status": "success|error", "result": "...", "error": "..."}
            - {"type": "chunk", "content": "..."}
            - {"type": "meta", "question_id": "...", "session_id": "...", "entities": [...], "response_time_ms": ...}
            - {"type": "error", "message": "..."}
        """
        start_time = time.time()
        question_id = str(uuid.uuid4())[:8]
        
        if not session_id:
            session_id = str(uuid.uuid4())[:16]
        
        try:
            agent = self._get_agent(session_id)
            
            # 使用 Agent 的事件流式输出
            full_answer = ""
            all_entities = []
            all_tool_calls = []
            
            for event in agent.chat_stream_events(question):
                event_type = event.get("type")
                
                if event_type == "tool_start":
                    # 转发工具开始事件（包含 tool_id）
                    yield {
                        "type": "tool_start",
                        "tool_id": event.get("tool_id"),
                        "tool_name": event.get("tool_name"),
                        "arguments": event.get("arguments", {})
                    }
                    
                elif event_type == "tool_end":
                    # 转发工具结束事件（包含 tool_id 和 status）
                    tool_end_event = {
                        "type": "tool_end",
                        "tool_id": event.get("tool_id"),
                        "tool_name": event.get("tool_name"),
                        "status": event.get("status", "success")
                    }
                    if event.get("result"):
                        tool_end_event["result"] = event.get("result")
                    if event.get("error"):
                        tool_end_event["error"] = event.get("error")
                    if event.get("entities"):
                        tool_end_event["entities"] = event.get("entities")
                        all_entities.extend(event.get("entities"))
                    yield tool_end_event
                    
                elif event_type == "chunk":
                    content = event.get("content", "")
                    full_answer += content
                    yield {"type": "chunk", "content": content}
                    
                elif event_type == "meta":
                    # Agent 发送的 meta 事件
                    all_entities = event.get("entities", all_entities)
                    all_tool_calls = event.get("tool_calls", [])
                    
                elif event_type == "error":
                    yield {"type": "error", "message": event.get("message")}
                    return
            
            # 计算响应时间
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 发送元数据
            yield {
                "type": "meta",
                "question_id": question_id,
                "session_id": session_id,
                "response_time_ms": response_time_ms,
                "entities": all_entities,
                "tool_calls": all_tool_calls,
                "citations": []
            }
            
            # 保存对话历史
            if user_id:
                self._save_conversation(
                    user_id=user_id,
                    session_id=session_id,
                    question=question,
                    response={
                        "answer": full_answer,
                        "entities": all_entities,
                        "citations": [],
                        "response_time_ms": response_time_ms
                    }
                )
                
        except Exception as e:
            logger.error(f"流式问答失败: {e}", exc_info=True)
            yield {"type": "error", "message": str(e)}
    
    def clear_session(self, session_id: str) -> bool:
        """
        清空会话历史
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否成功
        """
        global _session_agents
        
        if session_id in _session_agents:
            _session_agents[session_id].clear_memory()
            logger.info(f"已清空会话 {session_id} 的对话历史")
            return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """
        删除会话（释放 Agent 实例）
        
        Args:
            session_id: 会话 ID
            
        Returns:
            是否成功
        """
        global _session_agents
        
        if session_id in _session_agents:
            del _session_agents[session_id]
            logger.info(f"已删除会话 {session_id}")
            return True
        return False
    
    def _save_conversation(
        self,
        user_id: int,
        session_id: str,
        question: str,
        response: Dict[str, Any]
    ):
        """
        保存对话记录
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            question: 用户问题
            response: 问答响应
        """
        try:
            self.conversation_service.save_conversation(
                user_id=user_id,
                session_id=session_id,
                question=question,
                answer=response.get("answer"),
                entities=response.get("entities"),
                citations=response.get("citations"),
                response_time=response.get("response_time_ms")
            )
        except Exception as e:
            logger.error(f"保存对话记录失败: {e}", exc_info=True)


def get_qa_service(db: Session) -> QAService:
    """获取问答服务实例"""
    return QAService(db)
