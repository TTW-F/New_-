"""
健康检查路由

提供系统健康状态监控端点
"""

import logging
from fastapi import APIRouter, status
from pydantic import BaseModel
from typing import Dict, Optional

from api.core.config import settings
from api.core.database import check_db_connection, check_redis_connection

logger = logging.getLogger(__name__)

router = APIRouter(tags=["健康检查"])


class ComponentStatus(BaseModel):
    """组件状态"""
    name: str
    status: str  # healthy, unhealthy, unknown
    message: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str  # healthy, degraded, unhealthy
    version: str
    components: Dict[str, ComponentStatus]


def check_neo4j_connection() -> bool:
    """检查 Neo4j 连接"""
    try:
        from neo4j_service import get_neo4j_service
        service = get_neo4j_service()
        # 执行简单查询测试连接
        with service.driver.session() as session:
            session.run("RETURN 1")
        return True
    except Exception as e:
        logger.error(f"Neo4j 连接检查失败: {e}")
        return False


def check_graphrag_service() -> bool:
    """检查 GraphRAG 服务"""
    try:
        from graphrag_service import get_graphrag_service
        service = get_graphrag_service()
        return service is not None
    except Exception as e:
        logger.error(f"GraphRAG 服务检查失败: {e}")
        return False


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {"description": "系统健康"},
        503: {"description": "系统不健康"}
    }
)
async def health_check():
    """
    系统健康检查
    
    检查所有关键组件的连接状态：
    - MySQL 数据库
    - Neo4j 图数据库
    - Redis 缓存
    - GraphRAG 服务
    
    返回各组件状态和系统整体健康状态。
    """
    components = {}
    all_healthy = True
    
    # 检查 MySQL
    mysql_healthy = check_db_connection()
    components["mysql"] = ComponentStatus(
        name="MySQL",
        status="healthy" if mysql_healthy else "unhealthy",
        message="连接正常" if mysql_healthy else "连接失败"
    )
    if not mysql_healthy:
        all_healthy = False
    
    # 检查 Redis
    redis_healthy = check_redis_connection()
    components["redis"] = ComponentStatus(
        name="Redis",
        status="healthy" if redis_healthy else "unhealthy",
        message="连接正常" if redis_healthy else "连接失败"
    )
    if not redis_healthy:
        all_healthy = False
    
    # 检查 Neo4j
    neo4j_healthy = check_neo4j_connection()
    components["neo4j"] = ComponentStatus(
        name="Neo4j",
        status="healthy" if neo4j_healthy else "unhealthy",
        message="连接正常" if neo4j_healthy else "连接失败"
    )
    if not neo4j_healthy:
        all_healthy = False
    
    # 检查 GraphRAG 服务
    graphrag_healthy = check_graphrag_service()
    components["graphrag"] = ComponentStatus(
        name="GraphRAG",
        status="healthy" if graphrag_healthy else "unhealthy",
        message="服务可用" if graphrag_healthy else "服务不可用"
    )
    if not graphrag_healthy:
        all_healthy = False
    
    # 确定整体状态
    unhealthy_count = sum(1 for c in components.values() if c.status == "unhealthy")
    
    if unhealthy_count == 0:
        overall_status = "healthy"
    elif unhealthy_count < len(components):
        overall_status = "degraded"
    else:
        overall_status = "unhealthy"
    
    response = HealthResponse(
        status=overall_status,
        version=settings.APP_VERSION,
        components=components
    )
    
    # 如果不健康，记录日志
    if overall_status != "healthy":
        logger.warning(f"健康检查: {overall_status}, 不健康组件: {[k for k, v in components.items() if v.status == 'unhealthy']}")
    
    return response


@router.get("/health/live")
async def liveness_check():
    """
    存活检查
    
    简单的存活探针，只要应用在运行就返回 200。
    用于 Kubernetes 等容器编排系统的存活检查。
    """
    return {"status": "alive"}


@router.get("/health/ready")
async def readiness_check():
    """
    就绪检查
    
    检查应用是否准备好接收流量。
    只有当关键组件（MySQL）可用时才返回 200。
    """
    mysql_healthy = check_db_connection()
    
    if mysql_healthy:
        return {"status": "ready"}
    else:
        return {"status": "not ready", "reason": "MySQL 连接失败"}
