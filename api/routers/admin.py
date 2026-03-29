"""
后台管理路由

提供系统管理相关的 API 接口
"""

from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from api.core.database import get_db
from api.models.user import User, UserType
from api.models.conversation import ConversationHistory, Feedback
from api.security.jwt import get_current_user
from api.core.logger import logger
from pydantic import BaseModel


router = APIRouter(prefix="/admin", tags=["admin"])


# ============ Pydantic 模型 ============

class StatsResponse(BaseModel):
    """统计数据响应"""
    total_users: int
    today_users: int
    total_conversations: int
    today_conversations: int
    total_entities: int
    system_status: str


class UserListItem(BaseModel):
    """用户列表项"""
    id: int
    username: str
    email: str
    user_type: str
    is_active: bool
    created_at: str


class ConversationListItem(BaseModel):
    """对话列表项"""
    id: int
    user_id: int
    username: str
    session_id: str
    title: str
    message_count: int
    created_at: str


class LogItem(BaseModel):
    """日志项"""
    id: int
    level: str
    message: str
    timestamp: str


# ============ 权限验证 ============

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """
    验证当前用户是否为管理员
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        管理员用户对象
        
    Raises:
        HTTPException: 如果不是管理员
    """
    if current_user.user_type != UserType.admin:
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user


# ============ API 端点 ============

@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    获取系统统计数据
    
    Returns:
        统计数据
    """
    try:
        # 总用户数
        total_users = db.query(User).count()
        
        # 今日新增用户
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_users = db.query(User).filter(
            User.created_at >= today_start
        ).count()
        
        # 对话总数
        total_conversations = db.query(ConversationHistory).filter(
            ConversationHistory.is_deleted == False
        ).count()
        
        # 今日对话数
        today_conversations = db.query(ConversationHistory).filter(
            ConversationHistory.created_at >= today_start,
            ConversationHistory.is_deleted == False
        ).count()
        
        # 知识库实体数（这里使用固定值，实际应该从 Neo4j 查询）
        total_entities = 18000
        
        return {
            "total_users": total_users,
            "today_users": today_users,
            "total_conversations": total_conversations,
            "today_conversations": today_conversations,
            "total_entities": total_entities,
            "system_status": "running"
        }
    except Exception as e:
        logger.bind(admin_id=_admin.id).exception("获取统计数据失败")
        raise HTTPException(status_code=500, detail="获取统计数据失败")


@router.get("/users")
async def get_users(
    search: Optional[str] = Query(None, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    获取用户列表
    
    Args:
        search: 搜索关键词（用户名或邮箱）
        page: 页码
        page_size: 每页数量
        
    Returns:
        用户列表和总数
    """
    try:
        query = db.query(User)
        
        # 搜索过滤
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                (User.username.like(search_pattern)) |
                (User.email.like(search_pattern))
            )
        
        # 获取总数
        total = query.count()
        
        # 分页 - ID 升序排列（小的在前）
        offset = (page - 1) * page_size
        users = query.order_by(User.id.asc()).offset(offset).limit(page_size).all()
        
        return {
            "users": [
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "user_type": user.user_type.value,
                    "is_active": user.is_active,
                    "created_at": user.created_at.isoformat()
                }
                for user in users
            ],
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.bind(admin_id=_admin.id).exception("获取用户列表失败")
        raise HTTPException(status_code=500, detail="获取用户列表失败")


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    获取用户详情
    
    Args:
        user_id: 用户 ID
        
    Returns:
        用户详细信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 获取用户统计
    conversation_count = db.query(ConversationHistory).filter(
        ConversationHistory.user_id == user_id,
        ConversationHistory.is_deleted == False
    ).count()
    
    feedback_count = db.query(Feedback).filter(
        Feedback.user_id == user_id
    ).count()
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type.value,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
        "stats": {
            "conversation_count": conversation_count,
            "feedback_count": feedback_count
        }
    }


@router.get("/conversations")
async def get_conversations(
    filter_type: str = Query("all", description="过滤类型: all, today, week"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    获取对话记录列表
    
    Args:
        filter_type: 过滤类型
        page: 页码
        page_size: 每页数量
        
    Returns:
        对话记录列表
    """
    try:
        # 按 session_id 分组，获取每个会话的信息
        from sqlalchemy import func
        
        # 子查询：获取每个 session 的第一条记录和消息数
        subquery = db.query(
            ConversationHistory.session_id,
            ConversationHistory.user_id,
            func.min(ConversationHistory.id).label('first_id'),
            func.count(ConversationHistory.id).label('message_count'),
            func.min(ConversationHistory.created_at).label('created_at')
        ).filter(
            ConversationHistory.is_deleted == False
        ).group_by(
            ConversationHistory.session_id,
            ConversationHistory.user_id
        ).subquery()
        
        # 时间过滤
        if filter_type == "today":
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            subquery = db.query(
                ConversationHistory.session_id,
                ConversationHistory.user_id,
                func.min(ConversationHistory.id).label('first_id'),
                func.count(ConversationHistory.id).label('message_count'),
                func.min(ConversationHistory.created_at).label('created_at')
            ).filter(
                ConversationHistory.is_deleted == False,
                ConversationHistory.created_at >= today_start
            ).group_by(
                ConversationHistory.session_id,
                ConversationHistory.user_id
            ).subquery()
        elif filter_type == "week":
            week_start = datetime.now() - timedelta(days=7)
            subquery = db.query(
                ConversationHistory.session_id,
                ConversationHistory.user_id,
                func.min(ConversationHistory.id).label('first_id'),
                func.count(ConversationHistory.id).label('message_count'),
                func.min(ConversationHistory.created_at).label('created_at')
            ).filter(
                ConversationHistory.is_deleted == False,
                ConversationHistory.created_at >= week_start
            ).group_by(
                ConversationHistory.session_id,
                ConversationHistory.user_id
            ).subquery()
        
        # 获取总数
        total = db.query(subquery).count()
        
        # 分页查询
        offset = (page - 1) * page_size
        sessions = db.query(subquery).order_by(
            desc(subquery.c.created_at)
        ).offset(offset).limit(page_size).all()
        
        # 获取每个会话的详细信息
        result = []
        for session in sessions:
            # 获取第一条消息作为标题
            first_conv = db.query(ConversationHistory).filter(
                ConversationHistory.id == session.first_id
            ).first()
            
            # 获取用户名
            user = db.query(User).filter(User.id == session.user_id).first()
            
            if first_conv and user:
                title = first_conv.question[:50] + "..." if len(first_conv.question) > 50 else first_conv.question
                result.append({
                    "id": session.first_id,
                    "user_id": session.user_id,
                    "username": user.username,
                    "session_id": session.session_id,
                    "title": title,
                    "message_count": session.message_count,
                    "created_at": session.created_at.isoformat()
                })
        
        return {
            "conversations": result,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.bind(admin_id=_admin.id).exception("获取对话列表失败")
        raise HTTPException(status_code=500, detail="获取对话列表失败")


@router.get("/conversations/{conversation_id}")
async def get_conversation_detail(
    conversation_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    获取对话详情
    
    Args:
        conversation_id: 对话 ID
        
    Returns:
        对话详细信息
    """
    conversation = db.query(ConversationHistory).filter(
        ConversationHistory.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="对话不存在")
    
    # 获取用户信息
    user = db.query(User).filter(User.id == conversation.user_id).first()
    
    # 获取该会话的所有消息
    session_messages = db.query(ConversationHistory).filter(
        ConversationHistory.session_id == conversation.session_id,
        ConversationHistory.is_deleted == False
    ).order_by(ConversationHistory.created_at).all()
    
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "username": user.username if user else "未知用户",
        "session_id": conversation.session_id,
        "question": conversation.question,
        "answer": conversation.answer,
        "entities": conversation.related_entities or [],
        "citations": conversation.citations or [],
        "response_time": conversation.response_time,
        "created_at": conversation.created_at.isoformat(),
        "session_messages": [
            {
                "id": msg.id,
                "question": msg.question,
                "answer": msg.answer,
                "created_at": msg.created_at.isoformat()
            }
            for msg in session_messages
        ]
    }


@router.get("/logs")
async def get_logs(
    level: str = Query("all", description="日志级别: all, info, warning, error"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量"),
    _admin: User = Depends(require_admin)
):
    """
    获取系统日志
    
    注意：这是一个简化版本，实际应该从日志文件或日志系统读取
    
    Args:
        level: 日志级别
        page: 页码
        page_size: 每页数量
        
    Returns:
        日志列表
    """
    # 这里返回模拟数据，实际应该从日志文件读取
    # 可以使用 logging 模块的 MemoryHandler 或读取日志文件
    
    logs = [
        {"id": 1, "level": "info", "message": "系统启动成功", "timestamp": datetime.now().isoformat()},
        {"id": 2, "level": "info", "message": "数据库连接成功", "timestamp": datetime.now().isoformat()},
        {"id": 3, "level": "warning", "message": "API 响应时间较长", "timestamp": datetime.now().isoformat()},
    ]
    
    # 级别过滤
    if level != "all":
        logs = [log for log in logs if log["level"] == level]
    
    return {
        "logs": logs,
        "total": len(logs),
        "page": page,
        "page_size": page_size
    }


@router.put("/users/{user_id}/toggle-status")
async def toggle_user_status(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin)
):
    """
    切换用户状态（启用/禁用）
    
    Args:
        user_id: 用户 ID
        
    Returns:
        更新后的用户信息
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不允许禁用自己
    if user.user_type == UserType.admin:
        raise HTTPException(status_code=403, detail="不能禁用管理员账号")
    
    # 切换状态
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    
    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "user_type": user.user_type.value,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat()
    }


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin)
):
    """
    删除用户
    
    Args:
        user_id: 用户 ID
        
    Returns:
        删除结果
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 不允许删除管理员
    if user.user_type == UserType.admin:
        raise HTTPException(status_code=403, detail="不能删除管理员账号")
    
    # 不允许删除自己
    if user.id == current_admin.id:
        raise HTTPException(status_code=403, detail="不能删除自己")
    
    # 删除用户
    db.delete(user)
    db.commit()
    
    return {
        "message": f"用户 {user.username} 已删除",
        "user_id": user_id
    }
