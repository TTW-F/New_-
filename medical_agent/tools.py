"""
工具注册器和工具定义
"""

import json
from api.core.logger import logger
from typing import Dict, List, Optional, Callable, Any

from .schemas import Tool



class ToolRegistry:
    """工具注册和管理"""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
    
    def register(
        self,
        name: str,
        func: Callable,
        description: str,
        parameters: Dict[str, Any]
    ) -> None:
        """
        注册工具
        
        Args:
            name: 工具名称
            func: 执行函数
            description: 工具描述
            parameters: 参数 Schema (JSON Schema 格式)
        """
        tool = Tool(
            name=name,
            description=description,
            parameters=parameters,
            func=func
        )
        self._tools[name] = tool
        logger.debug(f"注册工具: {name}")
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """获取工具"""
        return self._tools.get(name)
    
    def get_all_tools(self) -> List[Tool]:
        """获取所有工具"""
        return list(self._tools.values())
    
    def get_all_tools_schema(self) -> List[Dict]:
        """
        获取所有工具的 OpenAI Function Schema
        
        Returns:
            OpenAI tools 格式的 Schema 列表
        """
        return [tool.to_openai_schema() for tool in self._tools.values()]
    
    def execute(self, name: str, arguments: Dict[str, Any]) -> str:
        """
        执行工具
        
        Args:
            name: 工具名称
            arguments: 调用参数
            
        Returns:
            执行结果（字符串）
            
        Raises:
            ValueError: 工具不存在
            Exception: 工具执行失败
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"工具不存在: {name}")
        
        try:
            result = tool.func(**arguments)
            # 确保返回字符串
            if isinstance(result, str):
                return result
            return json.dumps(result, ensure_ascii=False)
        except Exception as e:
            logger.error(f"工具执行失败 [{name}]: {e}", exc_info=True)
            raise
    
    def __len__(self) -> int:
        return len(self._tools)
    
    def __contains__(self, name: str) -> bool:
        return name in self._tools


def create_default_registry() -> ToolRegistry:
    """
    创建默认的工具注册器，注册所有医疗工具
    
    Returns:
        配置好的 ToolRegistry 实例
    """
    from neo4j_service import get_neo4j_service
    
    registry = ToolRegistry()
    neo4j_service = get_neo4j_service()
    
    # 1. 症状诊断工具
    def diagnose_by_symptoms(symptoms: str) -> str:
        """根据症状诊断疾病"""
        symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
        if not symptom_list:
            return json.dumps({
                "error": "症状列表为空",
                "suggestion": "请提供至少一个症状"
            }, ensure_ascii=False)
        
        diseases = neo4j_service.find_diseases_by_symptoms(symptom_list, top_k=5)
        return json.dumps({
            "input_symptoms": symptom_list,
            "possible_diseases": diseases,
            "count": len(diseases)
        }, ensure_ascii=False, indent=2)
    
    registry.register(
        name="diagnose_by_symptoms",
        func=diagnose_by_symptoms,
        description="根据症状列表诊断可能的疾病。返回按匹配度排序的疾病列表。",
        parameters={
            "type": "object",
            "properties": {
                "symptoms": {
                    "type": "string",
                    "description": "症状列表，多个症状用逗号分隔，如：头痛,发热,咳嗽"
                }
            },
            "required": ["symptoms"]
        }
    )
    
    # 2. 疾病信息查询工具
    def search_disease_info(disease_name: str) -> str:
        """查询疾病详细信息"""
        result = neo4j_service.search_disease_by_name(disease_name)
        if result:
            return json.dumps(result, ensure_ascii=False, indent=2)
        return json.dumps({
            "error": f"未找到疾病: {disease_name}",
            "suggestion": "请检查疾病名称或使用 fuzzy_search 工具"
        }, ensure_ascii=False)
    
    registry.register(
        name="search_disease_info",
        func=search_disease_info,
        description="搜索指定疾病的详细信息，包括描述、医保状态、患病比例、易感人群、治愈率等。",
        parameters={
            "type": "object",
            "properties": {
                "disease_name": {
                    "type": "string",
                    "description": "疾病名称，如：感冒、高血压、糖尿病"
                }
            },
            "required": ["disease_name"]
        }
    )
    
    # 3. 治疗方案查询工具
    def get_treatment_plan(disease_name: str) -> str:
        """获取疾病的完整治疗方案"""
        context = neo4j_service.get_disease_full_context(disease_name)
        return json.dumps(context, ensure_ascii=False, indent=2)
    
    registry.register(
        name="get_treatment_plan",
        func=get_treatment_plan,
        description="获取指定疾病的完整治疗方案，包括症状、推荐药物、检查项目、就诊科室、饮食建议等。",
        parameters={
            "type": "object",
            "properties": {
                "disease_name": {
                    "type": "string",
                    "description": "疾病名称"
                }
            },
            "required": ["disease_name"]
        }
    )
    
    # 4. 药物查询工具
    def search_drugs(disease_name: str) -> str:
        """查询疾病的推荐药物"""
        drugs = neo4j_service.search_drugs_by_disease(disease_name)
        if drugs:
            return json.dumps({
                "disease": disease_name,
                "drugs": drugs,
                "count": len(drugs)
            }, ensure_ascii=False, indent=2)
        return json.dumps({
            "disease": disease_name,
            "drugs": [],
            "message": "未找到该疾病的推荐药物"
        }, ensure_ascii=False)
    
    registry.register(
        name="search_drugs",
        func=search_drugs,
        description="查询指定疾病的推荐药物列表，包括药物名称、用法用量等。",
        parameters={
            "type": "object",
            "properties": {
                "disease_name": {
                    "type": "string",
                    "description": "疾病名称"
                }
            },
            "required": ["disease_name"]
        }
    )
    
    # 5. 模糊搜索工具
    def fuzzy_search(keyword: str, entity_type: str = "") -> str:
        """模糊搜索医疗实体"""
        entity_type_param = entity_type if entity_type else None
        entities = neo4j_service.fuzzy_search_entity(
            keyword=keyword,
            entity_type=entity_type_param,
            limit=10
        )
        return json.dumps({
            "keyword": keyword,
            "entity_type": entity_type or "全部",
            "results": entities,
            "count": len(entities)
        }, ensure_ascii=False, indent=2)
    
    registry.register(
        name="fuzzy_search",
        func=fuzzy_search,
        description="模糊搜索医疗实体（疾病、症状、药品等）。当不确定准确名称时使用。",
        parameters={
            "type": "object",
            "properties": {
                "keyword": {
                    "type": "string",
                    "description": "搜索关键词"
                },
                "entity_type": {
                    "type": "string",
                    "description": "实体类型，可选值：Disease, Symptom, Drug, Check。留空搜索所有类型。",
                    "enum": ["", "Disease", "Symptom", "Drug", "Check"]
                }
            },
            "required": ["keyword"]
        }
    )
    
    logger.info(f"已注册 {len(registry)} 个工具")
    return registry
