"""
JWT 认证模块

处理 JWT Token 的创建、验证和管理
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from api.core.config import settings
from api.core.database import get_db
from api.models.user import User, TokenBlacklist
from api.core.logger import logger


# OAuth2 密码流
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login",
    auto_error=True
)

# 可选的 OAuth2（允许匿名访问）
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_PREFIX}/auth/login",
    auto_error=False
)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    创建 JWT Access Token
    
    Args:
        data: 要编码的数据（通常包含 user_id）
        expires_delta: 过期时间增量
        
    Returns:
        JWT Token 字符串
    """
    to_encode = data.copy()
    
    # 确保 sub 是字符串类型（JWT 标准要求）
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    解码 JWT Token
    
    Args:
        token: JWT Token 字符串
        
    Returns:
        解码后的数据字典，失败返回 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.warning(f"Token 解码失败: {e}, 使用的密钥前缀: {settings.JWT_SECRET_KEY[:10]}...")
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    获取 Token 过期时间
    
    Args:
        token: JWT Token
        
    Returns:
        过期时间或 None
    """
    payload = decode_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None


def is_token_blacklisted(db: Session, token: str) -> bool:
    """
    检查 Token 是否在黑名单中
    
    Args:
        db: 数据库会话
        token: JWT Token
        
    Returns:
        是否在黑名单中
    """
    blacklisted = db.query(TokenBlacklist).filter(
        TokenBlacklist.token == token
    ).first()
    return blacklisted is not None


def blacklist_token(db: Session, token: str, user_id: int) -> bool:
    """
    将 Token 加入黑名单
    
    Args:
        db: 数据库会话
        token: JWT Token
        user_id: 用户 ID
        
    Returns:
        是否成功
    """
    try:
        expires_at = get_token_expiry(token)
        if not expires_at:
            expires_at = datetime.utcnow() + timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS)
        
        blacklist_entry = TokenBlacklist(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        db.add(blacklist_entry)
        db.commit()
        
        logger.info(f"Token 已加入黑名单: user_id={user_id}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Token 加入黑名单失败: {e}")
        return False


def cleanup_expired_tokens(db: Session) -> int:
    """
    清理过期的黑名单 Token
    
    Args:
        db: 数据库会话
        
    Returns:
        清理的数量
    """
    try:
        result = db.query(TokenBlacklist).filter(
            TokenBlacklist.expires_at < datetime.utcnow()
        ).delete()
        db.commit()
        
        if result > 0:
            logger.info(f"清理了 {result} 个过期的黑名单 Token")
        
        return result
        
    except Exception as e:
        db.rollback()
        logger.error(f"清理过期 Token 失败: {e}")
        return 0


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    获取当前认证用户（FastAPI 依赖注入）
    
    Args:
        token: JWT Token（从请求头自动提取）
        db: 数据库会话
        
    Returns:
        当前用户对象
        
    Raises:
        HTTPException: 认证失败时抛出 401 错误
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="认证失败",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # 检查 Token 是否在黑名单中
    if is_token_blacklisted(db, token):
        logger.debug("Token 已在黑名单中")
        raise credentials_exception
    
    # 解码 Token
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    # 获取用户 ID（sub 是字符串，需要转换为整数）
    sub = payload.get("sub")
    if sub is None:
        raise credentials_exception
    
    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise credentials_exception
    
    # 查询用户
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已被禁用"
        )
    
    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    获取当前用户（可选，允许匿名访问）
    
    Args:
        token: JWT Token（可选）
        db: 数据库会话
        
    Returns:
        用户对象或 None（匿名用户）
    """
    if not token:
        return None
    
    try:
        return await get_current_user(token, db)
    except HTTPException:
        return None


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户
    
    Args:
        current_user: 当前用户
        
    Returns:
        活跃用户对象
        
    Raises:
        HTTPException: 用户未激活时抛出 400 错误
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活"
        )
    return current_user
