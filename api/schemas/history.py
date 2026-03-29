"""
对话历史相关的 Pydantic 模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationResponse(BaseModel):
    """对话记录响应"""
    id: int
    session_id: str
    question: str
    answer: Optional[str]
    entities: List[dict] = []
    citations: List[dict] = []
    response_time_ms: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class HistoryListResponse(BaseModel):
    """对话历史列表响应"""
    status: str = "success"
    data: List[ConversationResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class SessionInfo(BaseModel):
    """会话信息"""
    session_id: str
    title: str
    first_question: str
    created_at: str
    message_count: int
    avg_response_time: int
    updated_at: str
    last_question: Optional[str]


class SessionListResponse(BaseModel):
    """会话列表响应"""
    status: str = "success"
    sessions: List[SessionInfo]
    total: int


class DeleteResponse(BaseModel):
    """删除响应"""
    status: str = "success"
    message: str = "删除成功"


class UserStatsResponse(BaseModel):
    """用户统计响应"""
    total_conversations: int
    total_sessions: int
    total_feedbacks: int
