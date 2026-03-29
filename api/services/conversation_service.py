"""
对话服务

处理对话历史的存储、查询和管理
"""

from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc

from api.models.conversation import ConversationHistory, Feedback, FeedbackType
from api.core.logger import logger



class ConversationService:
    """对话服务类"""
    
    def __init__(self, db: Session):
        """
        初始化对话服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def save_conversation(
        self,
        user_id: int,
        session_id: str,
        question: str,
        answer: Optional[str] = None,
        entities: Optional[List[dict]] = None,
        citations: Optional[List[dict]] = None,
        response_time: Optional[int] = None
    ) -> ConversationHistory:
        """
        保存对话记录
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            question: 用户问题
            answer: 系统回答
            entities: 识别的实体列表
            citations: 引用来源列表
            response_time: 响应时间（毫秒）
            
        Returns:
            保存的对话记录
        """
        conversation = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            question=question,
            answer=answer,
            related_entities=entities or [],
            citations=citations or [],
            response_time=response_time,
            is_deleted=False
        )
        
        self.db.add(conversation)
        self.db.commit()
        self.db.refresh(conversation)
        
        logger.bind(
            conversation_id=conversation.id,
            user_id=user_id,
            session_id=session_id,
            response_time=response_time
        ).debug("保存对话记录")
        return conversation
    
    def get_conversation_by_id(
        self,
        conversation_id: int,
        user_id: Optional[int] = None
    ) -> Optional[ConversationHistory]:
        """
        根据 ID 获取对话记录
        
        Args:
            conversation_id: 对话 ID
            user_id: 用户 ID（可选，用于权限验证）
            
        Returns:
            对话记录或 None
        """
        query = self.db.query(ConversationHistory).filter(
            ConversationHistory.id == conversation_id,
            ConversationHistory.is_deleted == False
        )
        
        if user_id is not None:
            query = query.filter(ConversationHistory.user_id == user_id)
        
        return query.first()
    
    def get_history(
        self,
        user_id: int,
        session_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[ConversationHistory], int]:
        """
        获取对话历史
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID（可选，用于过滤特定会话）
            page: 页码（从 1 开始）
            page_size: 每页数量
            
        Returns:
            (对话记录列表, 总数)
        """
        query = self.db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_deleted == False
        )
        
        if session_id:
            query = query.filter(ConversationHistory.session_id == session_id)
        
        # 按时间倒序排列
        query = query.order_by(desc(ConversationHistory.created_at))
        
        # 获取总数
        total = query.count()
        
        # 分页
        offset = (page - 1) * page_size
        conversations = query.offset(offset).limit(page_size).all()
        
        return conversations, total
    
    def get_sessions(self, user_id: int) -> List[dict]:
        """
        获取用户的所有会话信息
        
        Args:
            user_id: 用户 ID
            
        Returns:
            会话信息列表，包含 session_id 和 first_question
        """
        from sqlalchemy import func
        
        # 获取每个会话的第一条问题
        subquery = self.db.query(
            ConversationHistory.session_id,
            func.min(ConversationHistory.created_at).label('first_time')
        ).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_deleted == False
        ).group_by(ConversationHistory.session_id).subquery()
        
        # 获取每个会话的第一条记录
        sessions = self.db.query(
            ConversationHistory.session_id,
            ConversationHistory.question,
            ConversationHistory.created_at
        ).join(
            subquery,
            (ConversationHistory.session_id == subquery.c.session_id) &
            (ConversationHistory.created_at == subquery.c.first_time)
        ).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_deleted == False
        ).order_by(desc(ConversationHistory.created_at)).all()
        
        return [
            {
                "session_id": s.session_id,
                "first_question": s.question[:50] + "..." if len(s.question) > 50 else s.question,
                "created_at": s.created_at.isoformat()
            }
            for s in sessions
        ]
    
    def get_sessions_with_details(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> tuple[List[dict], int]:
        """
        获取用户的会话列表（带详细信息和分页）
        
        Args:
            user_id: 用户 ID
            page: 页码（从 1 开始）
            page_size: 每页数量
            
        Returns:
            (会话列表, 总数)
        """
        from sqlalchemy import func
        
        # 获取每个会话的统计信息
        session_stats = self.db.query(
            ConversationHistory.session_id,
            func.count(ConversationHistory.id).label('message_count'),
            func.avg(ConversationHistory.response_time).label('avg_response_time'),
            func.max(ConversationHistory.created_at).label('updated_at')
        ).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_deleted == False
        ).group_by(
            ConversationHistory.session_id
        ).order_by(
            desc('updated_at')
        )

        # 计算总数
        total = session_stats.count()

        # 分页
        offset = (page - 1) * page_size
        sessions = session_stats.offset(offset).limit(page_size).all()

        # 获取每个会话的第一条和最后一条问题
        result = []
        for session in sessions:
            first_conv = self.db.query(ConversationHistory).filter(
                ConversationHistory.user_id == user_id,
                ConversationHistory.session_id == session.session_id,
                ConversationHistory.is_deleted == False
            ).order_by(ConversationHistory.created_at).first()

            last_conv = self.db.query(ConversationHistory).filter(
                ConversationHistory.user_id == user_id,
                ConversationHistory.session_id == session.session_id,
                ConversationHistory.is_deleted == False
            ).order_by(desc(ConversationHistory.created_at)).first()

            title = first_conv.question[:30] + "..." if first_conv and len(first_conv.question) > 30 else (first_conv.question if first_conv else "医疗咨询")
            last_question = last_conv.question if last_conv else None

            result.append({
                "session_id": session.session_id,
                "title": title,
                "first_question": first_conv.question if first_conv else "医疗咨询",
                "created_at": first_conv.created_at.isoformat() if first_conv else session.updated_at.isoformat(),
                "message_count": session.message_count,
                "avg_response_time": int(session.avg_response_time) if session.avg_response_time else 0,
                "updated_at": session.updated_at.isoformat(),
                "last_question": last_question[:50] + "..." if last_question and len(last_question) > 50 else last_question
            })
        
        return result, total
    
    def get_session_conversations(
        self,
        user_id: int,
        session_id: str
    ) -> List[ConversationHistory]:
        """
        获取指定会话的所有对话（按时间顺序）
        
        Args:
            user_id: 用户 ID
            session_id: 会话 ID
            
        Returns:
            对话记录列表（按时间升序）
        """
        conversations = self.db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.session_id == session_id,
            ConversationHistory.is_deleted == False
        ).order_by(ConversationHistory.created_at).all()
        
        return conversations
    
    def soft_delete(
        self,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        软删除对话记录
        
        Args:
            conversation_id: 对话 ID
            user_id: 用户 ID（用于权限验证）
            
        Returns:
            是否成功
        """
        conversation = self.db.query(ConversationHistory).filter(
            ConversationHistory.id == conversation_id,
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_deleted == False
        ).first()
        
        if not conversation:
            return False
        
        conversation.is_deleted = True
        self.db.commit()
        
        logger.bind(
            conversation_id=conversation_id,
            user_id=user_id
        ).info("软删除对话记录")
        return True
    
    def delete_session(
        self,
        session_id: str,
        user_id: int
    ) -> bool:
        """
        软删除整个会话的所有对话记录
        
        Args:
            session_id: 会话 ID
            user_id: 用户 ID（用于权限验证）
            
        Returns:
            是否成功
        """
        conversations = self.db.query(ConversationHistory).filter(
            ConversationHistory.session_id == session_id,
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_deleted == False
        ).all()
        
        if not conversations:
            return False
        
        for conversation in conversations:
            conversation.is_deleted = True
        
        self.db.commit()
        
        logger.bind(
            session_id=session_id,
            user_id=user_id,
            count=len(conversations)
        ).info("软删除会话")
        return True
    
    def hard_delete(
        self,
        conversation_id: int,
        user_id: int
    ) -> bool:
        """
        物理删除对话记录（谨慎使用）
        
        Args:
            conversation_id: 对话 ID
            user_id: 用户 ID
            
        Returns:
            是否成功
        """
        result = self.db.query(ConversationHistory).filter(
            ConversationHistory.id == conversation_id,
            ConversationHistory.user_id == user_id
        ).delete()
        
        self.db.commit()
        return result > 0
    
    def save_feedback(
        self,
        user_id: int,
        conversation_id: int,
        rating: int,
        feedback_type: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Tuple[Optional[Feedback], Optional[str]]:
        """
        保存用户反馈
        
        Args:
            user_id: 用户 ID
            conversation_id: 对话 ID
            rating: 评分（1-5）
            feedback_type: 反馈类型
            comment: 评论内容
            
        Returns:
            (反馈对象, 错误信息)
        """
        # 验证评分范围
        if not 1 <= rating <= 5:
            return None, "评分必须在 1-5 之间"
        
        # 验证对话是否存在且属于该用户
        conversation = self.get_conversation_by_id(conversation_id, user_id)
        if not conversation:
            return None, "对话记录不存在"
        
        # 验证反馈类型
        feedback_type_enum = None
        if feedback_type:
            try:
                feedback_type_enum = FeedbackType(feedback_type)
            except ValueError:
                return None, f"无效的反馈类型: {feedback_type}"
        
        # 创建反馈
        feedback = Feedback(
            user_id=user_id,
            conversation_id=conversation_id,
            rating=rating,
            feedback_type=feedback_type_enum,
            comment=comment
        )
        
        self.db.add(feedback)
        self.db.commit()
        self.db.refresh(feedback)
        
        logger.bind(
            feedback_id=feedback.id,
            conversation_id=conversation_id,
            user_id=user_id,
            rating=rating,
            feedback_type=feedback_type
        ).success("保存反馈")
        return feedback, None
    
    def get_feedback_by_conversation(
        self,
        conversation_id: int,
        user_id: Optional[int] = None
    ) -> List[Feedback]:
        """
        获取对话的反馈
        
        Args:
            conversation_id: 对话 ID
            user_id: 用户 ID（可选）
            
        Returns:
            反馈列表
        """
        query = self.db.query(Feedback).filter(
            Feedback.conversation_id == conversation_id
        )
        
        if user_id is not None:
            query = query.filter(Feedback.user_id == user_id)
        
        return query.all()
    
    def get_user_stats(self, user_id: int) -> dict:
        """
        获取用户统计信息
        
        Args:
            user_id: 用户 ID
            
        Returns:
            统计信息字典
        """
        # 对话总数
        total_conversations = self.db.query(ConversationHistory).filter(
            ConversationHistory.user_id == user_id,
            ConversationHistory.is_deleted == False
        ).count()
        
        # 会话数
        total_sessions = len(self.get_sessions(user_id))
        
        # 反馈数
        total_feedbacks = self.db.query(Feedback).filter(
            Feedback.user_id == user_id
        ).count()
        
        return {
            "total_conversations": total_conversations,
            "total_sessions": total_sessions,
            "total_feedbacks": total_feedbacks
        }


def get_conversation_service(db: Session) -> ConversationService:
    """获取对话服务实例"""
    return ConversationService(db)
