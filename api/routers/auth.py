"""
认证路由

处理用户注册、登录、登出等认证相关的 API 端点
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from api.core.config import settings
from api.core.database import get_db
from api.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    UserResponse,
    TokenResponse,
    RegisterResponse,
    LogoutResponse,
    ErrorResponse
)
from api.services.user_service import UserService
from api.security.jwt import (
    create_access_token,
    get_current_user,
    blacklist_token
)
from api.models.user import User
from api.core.logger import logger


router = APIRouter(prefix="/api/v1/auth", tags=["认证"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        409: {"model": ErrorResponse, "description": "用户名或邮箱已存在"}
    }
)
async def register(
    request: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    创建新用户账号，密码会进行安全哈希存储。
    
    - **username**: 用户名（3-50位，只能包含字母、数字和下划线）
    - **email**: 有效的邮箱地址
    - **password**: 密码（至少8位，必须包含字母和数字）
    - **user_type**: 用户类型（doctor/patient/admin，默认 patient）
    """
    user_service = UserService(db)
    
    user, error = user_service.register(
        username=request.username,
        email=request.email,
        password=request.password,
        user_type=request.user_type
    )
    
    if error:
        # 判断是冲突错误还是验证错误
        if "已存在" in error or "已被注册" in error:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error
            )
    
    return RegisterResponse(
        status="success",
        message="注册成功",
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            user_type=user.user_type.value,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "用户名或密码错误"}
    }
)
async def login(
    request: UserLoginRequest,
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    验证用户凭据并返回 JWT Token。
    
    - **username**: 用户名
    - **password**: 密码
    """
    user_service = UserService(db)
    
    user = user_service.authenticate(
        username=request.username,
        password=request.password
    )
    
    if not user:
        # 统一的错误信息，不泄露具体原因
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # 创建 Token
    access_token = create_access_token(data={"sub": user.id})
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600
    
    logger.bind(
        username=user.username,
        user_id=user.id,
        user_type=user.user_type.value
    ).success("用户登录成功")
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            user_type=user.user_type.value,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@router.post(
    "/login/form",
    response_model=TokenResponse,
    include_in_schema=False  # 隐藏在文档中，用于 OAuth2 表单登录
)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    OAuth2 表单登录（用于 Swagger UI 测试）
    """
    user_service = UserService(db)
    
    user = user_service.authenticate(
        username=form_data.username,
        password=form_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    access_token = create_access_token(data={"sub": user.id})
    expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS * 3600
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=expires_in,
        user=UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            user_type=user.user_type.value,
            is_active=user.is_active,
            created_at=user.created_at
        )
    )


@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    用户登出
    
    将当前 Token 加入黑名单，使其失效。
    需要在请求头中携带有效的 Bearer Token。
    """
    # 从请求头获取 Token
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header[7:]
        blacklist_token(db, token, current_user.id)
    
    logger.bind(
        username=current_user.username,
        user_id=current_user.id
    ).info("用户登出")
    
    return LogoutResponse(
        status="success",
        message="登出成功"
    )


@router.get(
    "/me",
    response_model=UserResponse,
    responses={
        401: {"model": ErrorResponse, "description": "未认证"}
    }
)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    获取当前用户信息
    
    返回当前认证用户的详细信息。
    需要在请求头中携带有效的 Bearer Token。
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        user_type=current_user.user_type.value,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )


@router.post(
    "/change-password",
    response_model=LogoutResponse,
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未认证或密码错误"}
    }
)
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码
    
    修改当前用户的密码。需要提供旧密码进行验证。
    
    - **old_password**: 当前密码
    - **new_password**: 新密码（至少6位）
    """
    user_service = UserService(db)
    
    # 验证旧密码
    if not user_service.verify_password(current_user, old_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="当前密码错误"
        )
    
    # 验证新密码
    if len(new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码至少需要6位"
        )
    
    # 修改密码
    success = user_service.change_password(current_user, new_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="密码修改失败"
        )
    
    logger.bind(
        username=current_user.username,
        user_id=current_user.id
    ).success("用户修改密码")
    
    return LogoutResponse(
        status="success",
        message="密码修改成功"
    )
