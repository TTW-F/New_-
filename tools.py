from langchain_core.tools import tool
import json
from neo4j_service import get_neo4j_service

# 获取 Neo4j 服务单例
neo4j_service = get_neo4j_service()

@tool
def search_disease_info(disease_name: str) -> str:
    
    """搜索指定疾病的详细信息，包括描述、症状、治疗方案等。
    
    使用此工具可以获取疾病的基本信息，包括：
    - 疾病描述
    - 医保状态
    - 患病比例
    - 易感人群
    - 治愈率
    - 治疗费用
    - 成因和预防措施
        
    Args:
        disease_name: 疾病名称，如"感冒"、"高血压"
        
    Returns:
        疾病的详细信息（JSON格式字符串）
        
    Examples:
        >>> search_disease_info("感冒")
    """
    result = neo4j_service.search_disease_by_name(disease_name)
    
    if result:
        return json.dumps(result, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "error": f"未找到疾病: {disease_name}",
            "suggestion": "请检查疾病名称或使用 fuzzy_search 工具"
        }, ensure_ascii=False)

@tool
def diagnose_by_symptoms(symptoms: str) -> str:
    """根据症状列表诊断可能的疾病。
    
    此工具会根据用户提供的症状，在知识图谱中查找最匹配的疾病。
    返回结果按照匹配度（权重总和）降序排列。
    
    Args:
        symptoms: 症状列表，多个症状用逗号分隔。
                 例如: "头痛,发热,咳嗽" 或 "头痛, 发热, 咳嗽"
        
    Returns:
        JSON 格式的可能疾病列表，包含疾病名称、描述、匹配分数等
        
    Examples:
        >>> diagnose_by_symptoms("头痛,发热")
    """
    symptom_list = [s.strip() for s in symptoms.split(',') if s.strip()]
    
    if not symptom_list:
        return json.dumps({
            "error": "症状列表为空",
            "suggestion": "请提供至少一个症状"
        }, ensure_ascii=False)
    
    diseases = neo4j_service.find_diseases_by_symptoms(symptom_list, top_k=5)
    
    if diseases:
        return json.dumps({
            "input_symptoms": symptom_list,
            "possible_diseases": diseases,
            "count": len(diseases)
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "input_symptoms": symptom_list,
            "possible_diseases": [],
            "message": "未找到匹配的疾病"
        }, ensure_ascii=False)

@tool
def get_treatment_plan(disease_name: str) -> str:
    """获取指定疾病的完整治疗方案。
    
    此工具返回疾病的全面治疗信息，包括：
    - 常见症状（带权重）
    - 推荐药物（带用法用量）
    - 必要检查（带优先级）
    - 就诊科室
    - 饮食建议（宜食和忌食）
    - 可能的并发症
    
    Args:
        disease_name: 疾病名称，例如 "感冒"
        
    Returns:
        JSON 格式的完整治疗方案信息
        
    Examples:
        >>> get_treatment_plan("感冒")
    """
    context = neo4j_service.get_disease_full_context(disease_name)
    return json.dumps(context, ensure_ascii=False, indent=2)

@tool
def search_drugs(disease_name: str) -> str:
    """查询指定疾病的推荐药物列表。
    
    此工具专门用于查询疾病的用药建议，包括药物名称、用法用量等。
    
    Args:
        disease_name: 疾病名称
        
    Returns:
        JSON 格式的药物列表
        
    Examples:
        >>> search_drugs("感冒")
    """
    drugs = neo4j_service.search_drugs_by_disease(disease_name)
    
    if drugs:
        return json.dumps({
            "disease": disease_name,
            "drugs": drugs,
            "count": len(drugs)
        }, ensure_ascii=False, indent=2)
    else:
        return json.dumps({
            "disease": disease_name,
            "drugs": [],
            "message": "未找到该疾病的推荐药物"
        }, ensure_ascii=False)

@tool
def fuzzy_search(keyword: str, entity_type: str = "") -> str:
    """模糊搜索医疗实体（疾病、症状、药品等）。
    
    当用户不确定准确的实体名称时，使用此工具进行模糊匹配。
    
    Args:
        keyword: 搜索关键词，支持部分匹配
        entity_type: 可选，限定实体类型。可选值: "Disease", "Symptom", "Drug", "Check"
                    留空则搜索所有类型
        
    Returns:
        JSON 格式的匹配实体列表
        
    Examples:
        >>> fuzzy_search("头", "Symptom")
    """
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