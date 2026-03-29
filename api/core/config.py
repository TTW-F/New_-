"""
应用配置管理

从环境变量加载配置，提供类型安全的配置访问
"""

import os
from api.core.logger import logger
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """应用配置"""
    
    # 使用 model_config 替代 Config 类（pydantic v2 推荐方式）
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )
    
    # 应用信息
    APP_NAME: str = "医疗诊断智能问答系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API 配置
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # JWT 配置
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # MySQL 配置
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "medical_qa"
    
    @property
    def DATABASE_URL(self) -> str:
        """构建 MySQL 连接 URL"""
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"
    
    # Neo4j 配置
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Redis 配置
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        """构建 Redis 连接 URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # DeepSeek API 配置
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"
    
    # 速率限制配置
    RATE_LIMIT_ANONYMOUS: str = "10/minute"
    RATE_LIMIT_AUTHENTICATED: str = "60/minute"
    
    # CORS 配置
    CORS_ORIGINS: list = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["*"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    settings = Settings()
    # 调试日志：确认 JWT_SECRET_KEY 是否正确加载
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"配置加载完成，JWT_SECRET_KEY 前缀: {settings.JWT_SECRET_KEY[:10]}...")
    return settings


# 导出配置实例
settings = get_settings()
