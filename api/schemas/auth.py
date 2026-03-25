"""
认证相关的 Pydantic 模式

定义请求和响应的数据结构
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="用户名（3-50位，只能包含字母、数字和下划线）"
    )
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="密码（至少8位，必须包含字母和数字）"
    )
    user_type: str = Field(
        default="patient",
        description="用户类型：doctor/patient/admin"
    )
    
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError("用户名只能包含字母、数字和下划线")
        return v
    
    @field_validator("user_type")
    @classmethod
    def validate_user_type(cls, v: str) -> str:
        allowed = ["doctor", "patient", "admin"]
        if v not in allowed:
            raise ValueError(f"用户类型必须是: {', '.join(allowed)}")
        return v


class UserLoginRequest(BaseModel):
    """用户登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")


class UserResponse(BaseModel):
    """用户信息响应"""
    id: int
    username: str
    email: str
    user_type: str
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Token 响应"""
    access_token: str = Field(..., description="JWT Access Token")
    token_type: str = Field(default="bearer", description="Token 类型")
    expires_in: int = Field(..., description="过期时间（秒）")
    user: UserResponse = Field(..., description="用户信息")


class RegisterResponse(BaseModel):
    """注册响应"""
    status: str = "success"
    message: str = "注册成功"
    user: UserResponse


class LogoutResponse(BaseModel):
    """登出响应"""
    status: str = "success"
    message: str = "登出成功"


class ErrorResponse(BaseModel):
    """错误响应"""
    status: str = "error"
    message: str
    detail: Optional[str] = None
