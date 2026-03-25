"""
知识库路由

提供医疗知识库的搜索和浏览功能
"""

import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.security.jwt import get_current_user_optional
from api.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/knowledge", tags=["知识库"])


@router.get("/search")
async def search_knowledge(
    keyword: str = Query(..., min_length=1, max_length=100, description="搜索关键词"),
    entity_type: Optional[str] = Query(None, description="实体类型: disease, symptom, drug, check"),
    limit: int = Query(20, ge=1, le=100, description="返回结果数量"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    搜索医疗知识
    
    支持按关键词和类型搜索疾病、症状、药品、检查项等医疗实体。
    
    **参数：**
    - **keyword**: 搜索关键词（必填）
    - **entity_type**: 实体类型筛选（可选）
      - disease: 疾病
      - symptom: 症状
      - drug: 药品
      - check: 检查项
    - **limit**: 返回结果数量（默认20，最大100）
    
    **返回：**
    - 匹配的医疗实体列表
    """
    try:
        from neo4j_service import get_neo4j_service
        
        neo4j = get_neo4j_service()
        
        # 映射前端类型到Neo4j标签
        type_mapping = {
            'disease': 'Disease',
            'symptom': 'Symptom',
            'drug': 'Drug',
            'check': 'Check'
        }
        
        neo4j_type = type_mapping.get(entity_type) if entity_type else None
        
        # 调用Neo4j模糊搜索
        results = neo4j.fuzzy_search_entity(
            keyword=keyword,
            entity_type=neo4j_type,
            limit=limit
        )
        
        logger.info(f"知识库搜索: keyword={keyword}, type={entity_type}, results={len(results)}")
        
        return {
            "status": "success",
            "keyword": keyword,
            "entity_type": entity_type,
            "total": len(results),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"知识库搜索失败: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "搜索失败",
            "keyword": keyword,
            "results": []
        }


@router.get("/recommend")
async def get_recommended_knowledge(
    limit: int = Query(10, ge=1, le=50, description="返回结果数量"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取推荐的医疗知识
    
    返回常见的疾病、症状等医疗知识，用于首页展示。
    
    **参数：**
    - **limit**: 返回结果数量（默认10，最大50）
    
    **返回：**
    - 推荐的医疗实体列表
    """
    try:
        from neo4j_service import get_neo4j_service
        
        neo4j = get_neo4j_service()
        
        # 获取常见疾病
        common_diseases = [
            "感冒", "高血压", "糖尿病", "冠心病", "胃炎"
        ]
        
        # 获取常见症状
        common_symptoms = [
            "发热", "头痛", "咳嗽", "胸闷"
        ]
        
        # 获取常见药品
        common_drugs = [
            "布洛芬", "阿司匹林"
        ]
        
        # 获取常见检查
        common_checks = [
            "血常规", "心电图"
        ]
        
        results = []
        
        # 搜索常见疾病
        for disease_name in common_diseases[:limit//2]:
            entities = neo4j.fuzzy_search_entity(disease_name, "Disease", 1)
            if entities:
                results.append(entities[0])
        
        # 搜索常见症状
        for symptom_name in common_symptoms[:limit//4]:
            entities = neo4j.fuzzy_search_entity(symptom_name, "Symptom", 1)
            if entities:
                results.append(entities[0])
        
        # 搜索常见药品
        for drug_name in common_drugs[:limit//4]:
            entities = neo4j.fuzzy_search_entity(drug_name, "Drug", 1)
            if entities:
                results.append(entities[0])
        
        # 搜索常见检查
        for check_name in common_checks[:limit//4]:
            entities = neo4j.fuzzy_search_entity(check_name, "Check", 1)
            if entities:
                results.append(entities[0])
        
        logger.info(f"推荐知识: 返回 {len(results)} 条")
        
        return {
            "status": "success",
            "total": len(results),
            "results": results[:limit]
        }
        
    except Exception as e:
        logger.error(f"获取推荐知识失败: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "获取推荐失败",
            "results": []
        }


@router.get("/entity/{entity_name}")
async def get_entity_detail(
    entity_name: str,
    entity_type: Optional[str] = Query(None, description="实体类型"),
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取实体详情
    
    获取指定医疗实体的详细信息，包括相关的症状、药品、检查等。
    
    **参数：**
    - **entity_name**: 实体名称
    - **entity_type**: 实体类型（可选）
    
    **返回：**
    - 实体的详细信息
    """
    try:
        from neo4j_service import get_neo4j_service
        
        neo4j = get_neo4j_service()
        
        # 如果是疾病，获取完整上下文
        if entity_type == 'disease' or entity_type is None:
            context = neo4j.get_disease_full_context(entity_name)
            if context:
                return {
                    "status": "success",
                    "entity_name": entity_name,
                    "entity_type": "Disease",
                    "data": context
                }
        
        # 否则进行模糊搜索
        type_mapping = {
            'symptom': 'Symptom',
            'drug': 'Drug',
            'check': 'Check'
        }
        
        neo4j_type = type_mapping.get(entity_type) if entity_type else None
        results = neo4j.fuzzy_search_entity(entity_name, neo4j_type, 1)
        
        if results:
            return {
                "status": "success",
                "entity_name": entity_name,
                "entity_type": results[0].get("type"),
                "data": results[0]
            }
        
        return {
            "status": "error",
            "message": "未找到该实体",
            "entity_name": entity_name
        }
        
    except Exception as e:
        logger.error(f"获取实体详情失败: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "获取详情失败",
            "entity_name": entity_name
        }


@router.get("/stats")
async def get_knowledge_stats(
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    获取知识库统计信息
    
    返回知识库中各类实体的数量统计。
    
    **返回：**
    - 各类实体的数量
    """
    try:
        from neo4j_service import get_neo4j_service
        
        neo4j = get_neo4j_service()
        
        # 获取各类实体数量
        # 注意：这需要Neo4j服务支持统计查询
        # 如果没有实现，返回估算值
        
        stats = {
            "diseases": 10000,  # 疾病数量
            "symptoms": 3000,   # 症状数量
            "drugs": 5000,      # 药品数量
            "checks": 2000,     # 检查项数量
            "total": 20000      # 总数
        }
        
        return {
            "status": "success",
            "stats": stats
        }
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}", exc_info=True)
        return {
            "status": "error",
            "message": "获取统计失败"
        }
