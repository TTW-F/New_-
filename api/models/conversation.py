"""
对话数据模型

定义对话历史和反馈相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from api.core.database import Base
import enum


class FeedbackType(str, enum.Enum):
    """反馈类型枚举"""
    HELPFUL = "helpful"
    INCORRECT = "incorrect"
    UNCLEAR = "unclear"
    OTHER = "other"


class ConversationHistory(Base):
    """对话历史表"""
    __tablename__ = "conversation_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    session_id = Column(
        String(100),
        nullable=False,
        index=True,
        comment="会话ID"
    )
    question = Column(Text, nullable=False, comment="用户问题")
    answer = Column(Text, nullable=True, comment="系统回答")
    related_entities = Column(JSON, nullable=True, comment="识别的实体")
    citations = Column(JSON, nullable=True, comment="引用来源")
    response_time = Column(Integer, nullable=True, comment="响应时间(毫秒)")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
        comment="创建时间"
    )
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否已删除(软删除)"
    )
    
    # 关系
    feedbacks = relationship("Feedback", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ConversationHistory(id={self.id}, user_id={self.user_id}, session='{self.session_id}')>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "question": self.question,
            "answer": self.answer,
            "entities": self.related_entities or [],
            "citations": self.citations or [],
            "response_time_ms": self.response_time,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


class Feedback(Base):
    """用户反馈表"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="用户ID"
    )
    conversation_id = Column(
        Integer,
        ForeignKey("conversation_history.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="对话ID"
    )
    rating = Column(
        Integer,
        nullable=False,
        comment="评分(1-5)"
    )
    feedback_type = Column(
        Enum(FeedbackType),
        nullable=True,
        comment="反馈类型"
    )
    comment = Column(Text, nullable=True, comment="评论内容")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    
    # 关系
    conversation = relationship("ConversationHistory", back_populates="feedbacks")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, conversation_id={self.conversation_id}, rating={self.rating})>"
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "rating": self.rating,
            "feedback_type": self.feedback_type.value if self.feedback_type else None,
            "comment": self.comment,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
