"""
数据库连接管理

提供 MySQL 和 Redis 的连接管理
"""

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import redis

from api.core.config import settings
from api.core.logger import logger


# SQLAlchemy 配置
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
    echo=False  # 禁用 SQL 日志
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    获取数据库会话（FastAPI 依赖注入）
    
    Yields:
        Session: SQLAlchemy 数据库会话
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """
    获取数据库会话（上下文管理器）
    
    用于非 FastAPI 场景
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


# Redis 连接池
redis_pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL,
    decode_responses=True
)


def get_redis() -> redis.Redis:
    """
    获取 Redis 连接
    
    Returns:
        redis.Redis: Redis 客户端实例
    """
    return redis.Redis(connection_pool=redis_pool)


def init_db():
    """
    初始化数据库
    
    创建所有表（如果不存在）
    """
    from api.models import user, conversation  # 导入模型以注册
    Base.metadata.create_all(bind=engine)
    logger.info("数据库表初始化完成")


def check_db_connection() -> bool:
    """
    检查 MySQL 数据库连接
    
    Returns:
        bool: 连接是否正常
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"MySQL 连接检查失败: {e}")
        return False


def check_redis_connection() -> bool:
    """
    检查 Redis 连接
    
    Returns:
        bool: 连接是否正常
    """
    try:
        r = get_redis()
        r.ping()
        return True
    except Exception as e:
        logger.error(f"Redis 连接检查失败: {e}")
        return False
