"""
用户服务

处理用户注册、认证、密码管理等业务逻辑
"""

import re
import logging
import hashlib
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.models.user import User, UserType

logger = logging.getLogger(__name__)

# 使用 bcrypt 直接处理密码
try:
    import bcrypt
    USE_BCRYPT = True
except ImportError:
    USE_BCRYPT = False
    logger.warning("bcrypt not available, using hashlib fallback")


class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        """
        初始化用户服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
    
    def hash_password(self, password: str) -> str:
        """
        对密码进行哈希加密
        
        Args:
            password: 明文密码
            
        Returns:
            哈希后的密码
        """
        if USE_BCRYPT:
            # 截断到 72 字节（bcrypt 限制）
            password_bytes = password.encode('utf-8')[:72]
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password_bytes, salt).decode('utf-8')
        else:
            # fallback: 使用 SHA256 + salt
            salt = hashlib.sha256(str(id(password)).encode()).hexdigest()[:16]
            hashed = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"sha256${salt}${hashed}"
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """
        验证密码
        
        Args:
            plain_password: 明文密码
            hashed_password: 哈希密码
            
        Returns:
            密码是否匹配
        """
        if USE_BCRYPT and not hashed_password.startswith('sha256$'):
            password_bytes = plain_password.encode('utf-8')[:72]
            return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
        else:
            # fallback 验证
            parts = hashed_password.split('$')
            if len(parts) == 3 and parts[0] == 'sha256':
                salt = parts[1]
                expected = hashlib.sha256((plain_password + salt).encode()).hexdigest()
                return expected == parts[2]
            return False
    
    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        验证密码强度
        
        要求：
        - 至少 8 位
        - 包含数字
        - 包含字母
        
        Args:
            password: 待验证的密码
            
        Returns:
            (是否有效, 错误信息)
        """
        if len(password) < 8:
            return False, "密码长度至少为 8 位"
        
        if not re.search(r'\d', password):
            return False, "密码必须包含至少一个数字"
        
        if not re.search(r'[a-zA-Z]', password):
            return False, "密码必须包含至少一个字母"
        
        return True, ""
    
    def validate_username(self, username: str) -> Tuple[bool, str]:
        """
        验证用户名格式
        
        Args:
            username: 用户名
            
        Returns:
            (是否有效, 错误信息)
        """
        if len(username) < 3:
            return False, "用户名长度至少为 3 位"
        
        if len(username) > 50:
            return False, "用户名长度不能超过 50 位"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "用户名只能包含字母、数字和下划线"
        
        return True, ""
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        user_type: str = "patient"
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        注册新用户
        
        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            user_type: 用户类型
            
        Returns:
            (用户对象, 错误信息) - 成功时错误信息为 None
        """
        # 验证用户名
        valid, error = self.validate_username(username)
        if not valid:
            return None, error
        
        # 验证密码强度
        valid, error = self.validate_password_strength(password)
        if not valid:
            return None, error
        
        # 验证用户类型
        try:
            user_type_enum = UserType(user_type)
        except ValueError:
            return None, f"无效的用户类型: {user_type}，可选值: doctor, patient, admin"
        
        # 检查用户名是否已存在
        existing_user = self.db.query(User).filter(User.username == username).first()
        if existing_user:
            return None, "用户名已存在"
        
        # 检查邮箱是否已存在
        existing_email = self.db.query(User).filter(User.email == email).first()
        if existing_email:
            return None, "邮箱已被注册"
        
        # 创建用户
        try:
            user = User(
                username=username,
                email=email,
                password_hash=self.hash_password(password),
                user_type=user_type_enum,
                is_active=True
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"用户注册成功: {username}")
            return user, None
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"用户注册失败 (数据库错误): {e}")
            
            # 解析具体的冲突字段
            error_str = str(e.orig).lower()
            if "username" in error_str:
                return None, "用户名已存在"
            elif "email" in error_str:
                return None, "邮箱已被注册"
            else:
                return None, "注册失败，请稍后重试"
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"用户注册失败: {e}", exc_info=True)
            return None, "注册失败，请稍后重试"
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """
        验证用户凭据
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            验证成功返回用户对象，失败返回 None
        """
        # 查找用户
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            logger.debug(f"用户不存在: {username}")
            return None
        
        if not user.is_active:
            logger.debug(f"用户已禁用: {username}")
            return None
        
        # 验证密码
        if not self.verify_password(password, user.password_hash):
            logger.debug(f"密码错误: {username}")
            return None
        
        logger.info(f"用户认证成功: {username}")
        return user
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """
        根据 ID 获取用户
        
        Args:
            user_id: 用户 ID
            
        Returns:
            用户对象或 None
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """
        根据用户名获取用户
        
        Args:
            username: 用户名
            
        Returns:
            用户对象或 None
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        根据邮箱获取用户
        
        Args:
            email: 邮箱
            
        Returns:
            用户对象或 None
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(
        self,
        user_id: int,
        **kwargs
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        更新用户信息
        
        Args:
            user_id: 用户 ID
            **kwargs: 要更新的字段
            
        Returns:
            (用户对象, 错误信息)
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return None, "用户不存在"
        
        # 如果更新密码，需要验证强度并哈希
        if "password" in kwargs:
            valid, error = self.validate_password_strength(kwargs["password"])
            if not valid:
                return None, error
            kwargs["password_hash"] = self.hash_password(kwargs.pop("password"))
        
        # 更新字段
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return user, None
        except Exception as e:
            self.db.rollback()
            logger.error(f"更新用户失败: {e}", exc_info=True)
            return None, "更新失败"
    
    def deactivate_user(self, user_id: int) -> bool:
        """
        禁用用户
        
        Args:
            user_id: 用户 ID
            
        Returns:
            是否成功
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def verify_password(self, user: User, password: str) -> bool:
        """
        验证用户密码
        
        Args:
            user: 用户对象
            password: 明文密码
            
        Returns:
            密码是否正确
        """
        return self.verify_password(password, user.password_hash)
    
    def change_password(self, user: User, new_password: str) -> bool:
        """
        修改用户密码
        
        Args:
            user: 用户对象
            new_password: 新密码
            
        Returns:
            是否成功
        """
        try:
            user.password_hash = self.hash_password(new_password)
            self.db.commit()
            logger.info(f"用户密码已修改: {user.username}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"修改密码失败: {e}", exc_info=True)
            return False


def get_user_service(db: Session) -> UserService:
    """获取用户服务实例"""
    return UserService(db)
