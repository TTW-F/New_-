"""
对话历史路由

处理对话历史查询和管理的 API 端点
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
import math

from api.core.database import get_db
from api.schemas.history import (
    ConversationResponse,
    HistoryListResponse,
    SessionListResponse,
    DeleteResponse,
    UserStatsResponse
)
from api.schemas.auth import ErrorResponse
from api.services.conversation_service import ConversationService
from api.security.jwt import get_current_user
from api.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/history", tags=["对话历史"])


@router.get(
    "",
    response_model=HistoryListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
async def get_history(
    session_id: Optional[str] = Query(None, description="会话 ID（可选，用于过滤特定会话）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取对话历史
    
    获取当前用户的对话历史记录，支持分页和按会话过滤。
    
    - **session_id**: 会话 ID（可选，用于过滤特定会话的对话）
    - **page**: 页码（从 1 开始）
    - **page_size**: 每页数量（1-100，默认 20）
    
    返回按时间倒序排列的对话记录。
    """
    conversation_service = ConversationService(db)
    
    conversations, total = conversation_service.get_history(
        user_id=current_user.id,
        session_id=session_id,
        page=page,
        page_size=page_size
    )
    
    # 计算总页数
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    
    # 转换为响应格式
    data = []
    for conv in conversations:
        data.append(ConversationResponse(
            id=conv.id,
            session_id=conv.session_id,
            question=conv.question,
            answer=conv.answer,
            entities=conv.related_entities or [],
            citations=conv.citations or [],
            response_time_ms=conv.response_time,
            created_at=conv.created_at
        ))
    
    return HistoryListResponse(
        status="success",
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get(
    "/sessions",
    response_model=SessionListResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
async def get_sessions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取会话列表（带详细信息和分页）
    
    获取当前用户的所有会话列表，包含消息数量、平均响应时间等统计信息。
    
    - **page**: 页码（从 1 开始）
    - **page_size**: 每页数量（1-100，默认 10）
    """
    conversation_service = ConversationService(db)
    
    sessions, total = conversation_service.get_sessions_with_details(
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )
    
    return SessionListResponse(
        status="success",
        sessions=sessions,
        total=total
    )


@router.get(
    "/stats",
    response_model=UserStatsResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息
    
    获取当前用户的对话统计数据。
    """
    conversation_service = ConversationService(db)
    
    stats = conversation_service.get_user_stats(current_user.id)
    
    return UserStatsResponse(**stats)


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "对话不存在"}
    }
)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取单条对话记录
    
    根据对话 ID 获取详细信息。
    """
    conversation_service = ConversationService(db)
    
    conversation = conversation_service.get_conversation_by_id(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话记录不存在"
        )
    
    return ConversationResponse(
        id=conversation.id,
        session_id=conversation.session_id,
        question=conversation.question,
        answer=conversation.answer,
        entities=conversation.related_entities or [],
        citations=conversation.citations or [],
        response_time_ms=conversation.response_time,
        created_at=conversation.created_at
    )


@router.delete(
    "/sessions/{session_id}",
    response_model=DeleteResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "会话不存在"}
    }
)
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除会话
    
    软删除指定会话的所有对话记录（标记为已删除但不物理删除）。
    """
    conversation_service = ConversationService(db)
    
    success = conversation_service.delete_session(
        session_id=session_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="会话不存在"
        )
    
    return DeleteResponse(
        status="success",
        message="删除成功"
    )


@router.delete(
    "/{conversation_id}",
    response_model=DeleteResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"},
        404: {"model": ErrorResponse, "description": "对话不存在"}
    }
)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除对话记录
    
    软删除指定的对话记录（标记为已删除但不物理删除）。
    """
    conversation_service = ConversationService(db)
    
    success = conversation_service.soft_delete(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="对话记录不存在"
        )
    
    return DeleteResponse(
        status="success",
        message="删除成功"
    )
