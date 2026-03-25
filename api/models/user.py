"""
用户数据模型

定义用户相关的数据库表结构
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.sql import func
from api.core.database import Base
import enum


class UserType(str, enum.Enum):
    """用户类型枚举"""
    doctor = "doctor"
    patient = "patient"
    admin = "admin"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True, comment="用户名")
    email = Column(String(100), unique=True, nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    user_type = Column(
        Enum(UserType),
        default=UserType.patient,
        nullable=False,
        comment="用户类型"
    )
    is_active = Column(Boolean, default=True, nullable=False, comment="是否激活")
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', type='{self.user_type}')>"
    
    def to_dict(self, include_sensitive: bool = False) -> dict:
        """
        转换为字典
        
        Args:
            include_sensitive: 是否包含敏感信息（密码哈希）
            
        Returns:
            用户信息字典
        """
        data = {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "user_type": self.user_type.value if self.user_type else None,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_sensitive:
            data["password_hash"] = self.password_hash
            
        return data


class TokenBlacklist(Base):
    """Token 黑名单表（用于登出）"""
    __tablename__ = "token_blacklist"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(500), nullable=False, index=True, comment="JWT Token")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    blacklisted_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="加入黑名单时间"
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Token 过期时间"
    )
    
    def __repr__(self):
        return f"<TokenBlacklist(id={self.id}, user_id={self.user_id})>"
