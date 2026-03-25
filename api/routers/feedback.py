"""
反馈路由

处理用户反馈相关的 API 端点
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.schemas.feedback import (
    FeedbackRequest,
    FeedbackResponse,
    FeedbackCreateResponse
)
from api.schemas.auth import ErrorResponse
from api.services.conversation_service import ConversationService
from api.security.jwt import get_current_user
from api.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/feedback", tags=["反馈"])


@router.post(
    "",
    response_model=FeedbackCreateResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "对话不存在"}
    }
)
async def submit_feedback(
    request: FeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    提交反馈
    
    对指定的对话记录提交反馈评价。
    
    - **conversation_id**: 对话 ID
    - **rating**: 评分（1-5）
    - **feedback_type**: 反馈类型（helpful/incorrect/unclear/other）
    - **comment**: 评论内容（可选）
    """
    conversation_service = ConversationService(db)
    
    feedback, error = conversation_service.save_feedback(
        user_id=current_user.id,
        conversation_id=request.conversation_id,
        rating=request.rating,
        feedback_type=request.feedback_type,
        comment=request.comment
    )
    
    if error:
        if "不存在" in error:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
    
    logger.info(f"用户 {current_user.username} 提交反馈: conversation_id={request.conversation_id}, rating={request.rating}")
    
    return FeedbackCreateResponse(
        status="success",
        message="反馈提交成功",
        feedback=FeedbackResponse(
            id=feedback.id,
            conversation_id=feedback.conversation_id,
            rating=feedback.rating,
            feedback_type=feedback.feedback_type.value if feedback.feedback_type else None,
            comment=feedback.comment,
            created_at=feedback.created_at
        )
    )


@router.get(
    "/conversation/{conversation_id}",
    response_model=list[FeedbackResponse],
    responses={
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
async def get_conversation_feedback(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取对话的反馈
    
    获取指定对话的所有反馈记录。
    """
    conversation_service = ConversationService(db)
    
    feedbacks = conversation_service.get_feedback_by_conversation(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    return [
        FeedbackResponse(
            id=f.id,
            conversation_id=f.conversation_id,
            rating=f.rating,
            feedback_type=f.feedback_type.value if f.feedback_type else None,
            comment=f.comment,
            created_at=f.created_at
        )
        for f in feedbacks
    ]
