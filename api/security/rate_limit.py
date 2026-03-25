"""
速率限制模块

基于 slowapi 实现请求速率限制
"""

import logging
from fastapi import Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.core.config import settings

logger = logging.getLogger(__name__)


def get_rate_limit_key(request: Request) -> str:
    """
    获取速率限制的键
    
    根据用户认证状态返回不同的键：
    - 认证用户：使用用户 ID
    - 匿名用户：使用 IP 地址
    """
    # 尝试从请求状态获取用户（需要在认证中间件之后）
    user = getattr(request.state, "user", None)
    
    if user:
        return f"user:{user.id}"
    else:
        return f"ip:{get_remote_address(request)}"


def get_dynamic_rate_limit(request: Request) -> str:
    """
    动态获取速率限制
    
    根据用户认证状态返回不同的限制：
    - 认证用户：60/minute
    - 匿名用户：10/minute
    """
    # 检查是否有认证头
    auth_header = request.headers.get("Authorization", "")
    
    if auth_header.startswith("Bearer "):
        return settings.RATE_LIMIT_AUTHENTICATED
    else:
        return settings.RATE_LIMIT_ANONYMOUS


# 创建限流器
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[settings.RATE_LIMIT_ANONYMOUS]
)


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    """
    速率限制超出处理器
    """
    logger.warning(f"速率限制超出: {get_rate_limit_key(request)}")
    
    # 解析重试时间
    retry_after = 60  # 默认 60 秒
    if hasattr(exc, "detail") and "retry after" in str(exc.detail).lower():
        try:
            # 尝试从错误信息中提取重试时间
            import re
            match = re.search(r'(\d+)\s*second', str(exc.detail))
            if match:
                retry_after = int(match.group(1))
        except:
            pass
    
    raise HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail={
            "status": "error",
            "message": "请求过于频繁，请稍后重试",
            "retry_after": retry_after
        },
        headers={"Retry-After": str(retry_after)}
    )


# 预定义的限流装饰器
def limit_anonymous(limit: str = None):
    """匿名用户限流装饰器"""
    return limiter.limit(limit or settings.RATE_LIMIT_ANONYMOUS)


def limit_authenticated(limit: str = None):
    """认证用户限流装饰器"""
    return limiter.limit(limit or settings.RATE_LIMIT_AUTHENTICATED)


def limit_dynamic():
    """动态限流装饰器（根据认证状态）"""
    return limiter.limit(get_dynamic_rate_limit)
