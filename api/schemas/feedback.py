"""
反馈相关的 Pydantic 模式
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class FeedbackRequest(BaseModel):
    """反馈请求"""
    conversation_id: int = Field(..., description="对话 ID")
    rating: int = Field(..., ge=1, le=5, description="评分（1-5）")
    feedback_type: Optional[str] = Field(
        None,
        description="反馈类型：helpful/incorrect/unclear/other"
    )
    comment: Optional[str] = Field(
        None,
        max_length=1000,
        description="评论内容"
    )
    
    @field_validator("feedback_type")
    @classmethod
    def validate_feedback_type(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = ["helpful", "incorrect", "unclear", "other"]
            if v not in allowed:
                raise ValueError(f"反馈类型必须是: {', '.join(allowed)}")
        return v


class FeedbackResponse(BaseModel):
    """反馈响应"""
    id: int
    conversation_id: int
    rating: int
    feedback_type: Optional[str]
    comment: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackCreateResponse(BaseModel):
    """反馈创建响应"""
    status: str = "success"
    message: str = "反馈提交成功"
    feedback: FeedbackResponse
