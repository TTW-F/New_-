"""
问答相关的 Pydantic 模式
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class QARequest(BaseModel):
    """问答请求"""
    question: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="用户问题"
    )
    session_id: Optional[str] = Field(
        None,
        max_length=100,
        description="会话 ID（可选，用于关联多轮对话）"
    )


class EntityInfo(BaseModel):
    """实体信息"""
    name: str
    type: str
    confidence: Optional[float] = None


class CitationInfo(BaseModel):
    """引用信息"""
    type: str
    name: str
    description: Optional[str] = None


class QAResponse(BaseModel):
    """问答响应"""
    question_id: str = Field(..., description="问题 ID")
    session_id: str = Field(..., description="会话 ID")
    question: str = Field(..., description="用户问题")
    answer: str = Field(..., description="系统回答")
    entities: List[dict] = Field(default=[], description="识别的实体")
    citations: List[dict] = Field(default=[], description="引用来源")
    response_time_ms: int = Field(..., description="响应时间（毫秒）")


class QAErrorResponse(BaseModel):
    """问答错误响应"""
    status: str = "error"
    message: str
    question_id: Optional[str] = None
