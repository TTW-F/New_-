import os
import json
from typing import List, Dict, Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv
import logging
logger = logging.getLogger(__name__)

load_dotenv()

class Neo4jService:
    """Neo4j 知识图谱查询服务"""
    
    def __init__(self):
        """初始化 Neo4j 连接"""
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            logger.info(f"Neo4j 连接成功: {self.uri}")
        except Exception as e:
            logger.error(f"Neo4j 连接失败: {e}")
            raise


    def close(self):
        """关闭连接"""
        self.driver.close()
    
    def search_disease_by_name(self, disease_name: str) -> Optional[Dict]:
        """
        根据疾病名称精确查询疾病的详细信息。

        Args:
            disease_name: 疾病的精确名称，例如 "糖尿病"。

        Returns:
            一个包含疾病所有属性的字典，如果数据库中没有找到对应的疾病，则返回 None。
        """
        query = """
        MATCH (d:Disease {name: $name})
        RETURN d
        """
        # 使用上下文管理器创建会话
        with self.driver.session() as session:
            result = session.run(query, name=disease_name)
            record = result.single()
            
            if record:
                disease = dict(record["d"])
                return disease
            return None
        
    
    def find_diseases_by_symptoms(self, symptoms: List[str], top_k: int = 5) -> List[Dict]:
        """根据症状列表查找可能的疾病
        
        Args:
            symptoms: 症状名称列表
            top_k: 返回前 k 个最可能的疾病
            
        Returns:
            疾病列表，按匹配度排序
        """
        query = """
        MATCH (s:Symptom)<-[r:HAS_SYMPTOM]-(d:Disease)
        WHERE s.name IN $symptoms
        WITH d, SUM(r.weight) as total_weight, COUNT(s) as matched_symptoms
        RETURN d.name as name, 
               d.desc as description,
               total_weight,
               matched_symptoms
        ORDER BY total_weight DESC, matched_symptoms DESC
        LIMIT $top_k
        """
        
        with self.driver.session() as session:
            result = session.run(query, symptoms=symptoms, top_k=top_k)
            
            diseases = []
            for record in result:
                diseases.append({
                    "name": record["name"],
                    "description": record["description"],
                    "match_score": float(record["total_weight"]),
                    "matched_symptoms": record["matched_symptoms"]
                })
            
            return diseases
    
    def get_disease_full_context(self, disease_name: str) -> Dict:
        """获取疾病的完整上下文信息
        
        包括：症状、药品、检查、科室、饮食建议、并发症等
        
        Args:
            disease_name: 疾病名称
            
        Returns:
            完整的疾病上下文字典
        """
        query = """
        MATCH (d:Disease {name: $name})
        
        // 获取症状
        OPTIONAL MATCH (d)-[hs:HAS_SYMPTOM]->(s:Symptom)
        
        // 获取药品
        OPTIONAL MATCH (d)-[rd:RECOMMAND_DRUG]->(drug:Drug)
        
        // 获取检查
        OPTIONAL MATCH (d)-[nc:NEED_CHECK]->(check:Check)
        
        // 获取科室
        OPTIONAL MATCH (d)-[bd:BELONGS_DEPARTMENT]->(dept:Department)
        
        // 获取宜食食物
        OPTIONAL MATCH (d)-[se:SHOULD_EAT]->(food_good:Food)
        
        // 获取忌食食物
        OPTIONAL MATCH (d)-[sa:SHOULD_AVOID]->(food_bad:Food)
        
        // 获取并发症
        OPTIONAL MATCH (d)-[comp:COMPLICATION]->(comp_disease:Disease)
        
        RETURN d,
               collect(DISTINCT {name: s.name, weight: hs.weight}) as symptoms,
               collect(DISTINCT {name: drug.name, usage: rd.usage}) as drugs,
               collect(DISTINCT {name: check.name, priority: nc.priority}) as checks,
               collect(DISTINCT dept.name) as departments,
               collect(DISTINCT {name: food_good.name, reason: se.reason}) as good_foods,
               collect(DISTINCT {name: food_bad.name, reason: sa.reason}) as bad_foods,
               collect(DISTINCT {name: comp_disease.name, probability: comp.probability}) as complications
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=disease_name)
            record = result.single()
            
            if not record:
                return {"error": f"未找到疾病: {disease_name}"}
            
            disease = dict(record["d"])
            
            context = {
                "disease": disease,
                "symptoms": [s for s in record["symptoms"] if s["name"]],
                "drugs": [d for d in record["drugs"] if d["name"]],
                "checks": [c for c in record["checks"] if c["name"]],
                "departments": [dept for dept in record["departments"] if dept],
                "dietary_advice": {
                    "should_eat": [f for f in record["good_foods"] if f["name"]],
                    "should_avoid": [f for f in record["bad_foods"] if f["name"]]
                },
                "complications": [c for c in record["complications"] if c["name"]]
            }
            
            return context
    
    def search_drug_by_name(self, drug_name: str) -> Optional[Dict]:
        """根据药品名称查询药品详细信息（用于药品说明查询）
        
        此方法用于查询药品的详细信息，包括：
        - 药品描述和作用
        - 使用说明
        - 禁忌症
        - 副作用
        - 注意事项
        
        Args:
            drug_name: 药品名称
            
        Returns:
            药品信息字典，如果未找到则返回 None
        """
        query = """
        MATCH (drug:Drug {name: $name})
        RETURN drug
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, name=drug_name)
                record = result.single()
                
                if record:
                    drug = dict(record["drug"])
                    logger.debug(f"查询药品成功: {drug_name}")
                    return drug
                else:
                    logger.warning(f"未找到药品: {drug_name}")
                    return None
        except Exception as e:
            logger.error(f"查询药品失败 [{drug_name}]: {e}", exc_info=True)
            return None
    
    def search_drugs_by_disease(self, disease_name: str) -> List[Dict]:
        """查询疾病相关的药品（内部使用，用于疾病信息展示）
        
        注意：此方法仅用于在疾病信息中展示医学文献提及的药物，
        不构成用药建议或处方。
        
        Args:
            disease_name: 疾病名称
            
        Returns:
            药品列表
        """
        query = """
        MATCH (d:Disease {name: $name})-[r:RECOMMAND_DRUG]->(drug:Drug)
        RETURN drug.name as name, 
               drug.desc as description,
               r.usage as usage,
               r.frequency as frequency
        """
        
        with self.driver.session() as session:
            result = session.run(query, name=disease_name)
            
            drugs = []
            for record in result:
                drugs.append({
                    "name": record["name"],
                    "description": record.get("description"),
                    "usage": record.get("usage"),
                    "frequency": record.get("frequency")
                })
            
            return drugs
    
    def fuzzy_search_entity(self, keyword: str, entity_type: str = None, limit: int = 10) -> List[Dict]:
        """模糊搜索实体（疾病、症状、药品等）
        
        Args:
            keyword: 搜索关键词
            entity_type: 实体类型（Disease/Symptom/Drug/Check），None 表示搜索所有
            limit: 返回结果数量
            
        Returns:
            匹配的实体列表
        """
        if entity_type:
            query = f"""
            MATCH (n:{entity_type})
            WHERE n.name CONTAINS $keyword
            RETURN n.name as name, 
                   n.desc as description,
                   '{entity_type}' as type
            LIMIT $limit
            """
        else:
            query = """
            MATCH (n)
            WHERE n.name CONTAINS $keyword
            RETURN n.name as name, 
                   n.desc as description,
                   labels(n)[0] as type
            LIMIT $limit
            """
            
        
        with self.driver.session() as session:
            result = session.run(query, keyword=keyword, limit=limit)
            
            entities = []
            for record in result:
                entities.append({
                    "name": record["name"],
                    "description": record.get("description"),
                    "type": record["type"]
                })
            
            return entities


# 单例模式，避免重复创建连接
_neo4j_service_instance = None

def get_neo4j_service() -> Neo4jService:
    """获取 Neo4j 服务单例"""
    global _neo4j_service_instance
    if _neo4j_service_instance is None:
        _neo4j_service_instance = Neo4jService()
    return _neo4j_service_instance