"""
自实现的 GraphRAG 服务

实现标准的 GraphRAG 流程：
1. 实体识别与链接 (Entity Linking)
2. 子图检索 (Subgraph Retrieval)
3. 上下文构建 (Context Building)
4. 提示词构建 (Prompt Construction)
5. LLM 生成答案
"""

import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from neo4j_service import get_neo4j_service

load_dotenv()
logger = logging.getLogger(__name__)


class GraphRAGService:

    def __init__(self):
        """初始化 GraphRAG 服务"""
        self.neo4j = get_neo4j_service()

        # 初始化 LLM（DeepSeek）
        self.llm = ChatOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            temperature=0.7
        )

        logger.info("GraphRAG 服务初始化完成")

    def query(self, question: str, max_hops: int = 2) -> Dict:
        """
        GraphRAG 完整查询流程

        Args:
            question: 用户问题
            max_hops: 最大跳数（默认 2 跳）

        Returns:
            {
                "answer": "生成的答案",
                "entities": [...],  # 识别到的实体
                "context_summary": "...",  # 构建的上下文摘要
                "citations": [...]  # 引用来源
            }
        """
        try:
            # 1. 实体识别与链接
            entities = self._extract_and_link_entities(question)

            if not entities:
                return {
                    "answer": "抱歉，我无法从您的问题中识别出相关的医疗实体。请尝试使用更具体的疾病名称或症状描述。",
                    "entities": [],
                    "context_summary": "",
                    "citations": []
                }

            # 2. 子图检索
            subgraph = self._retrieve_subgraph(entities, max_hops)
            logger.info(f"子图检索: 疾病 {len(subgraph.get('diseases', []))} 个, "
                       f"症状 {len(subgraph.get('symptoms', []))} 个, "
                       f"药品 {len(subgraph.get('drugs', []))} 个")

            # 3. 上下文构建
            context = self._build_knowledge_context(subgraph)

            # 4. 提示词构建
            prompt = self._build_rag_prompt(question, context)

            # 5. LLM 生成
            answer = self._generate_answer(prompt)

            # 6. 提取引用
            citations = self._extract_citations(subgraph)

            return {
                "answer": answer,
                "entities": entities,
                "context_summary": self._summarize_context(context),
                "citations": citations
            }

        except Exception as e:
            logger.error(f"GraphRAG 查询失败: {e}", exc_info=True)
            return {
                "answer": f"抱歉，处理您的问题时出现错误: {str(e)}",
                "entities": [],
                "context_summary": "",
                "citations": []
            }

    def _extract_and_link_entities(self, question: str) -> List[Dict]:
        """
        实体识别与链接（智能版本）

        新策略：优先使用 LLM 进行实体识别，规则匹配作为补充
        优势：
        1. LLM 可以理解上下文和语义
        2. 能识别同义词、口语化表达、缩写等
        3. 能识别复杂问题中的多个实体
        4. 规则匹配作为快速补充，提高召回率
        """
        # 策略1: 优先使用 LLM 进行智能实体识别
        llm_entities = self._llm_extract_entities_structured(question)

        if llm_entities:
            # 在 Neo4j 中链接这些实体
            linked_entities = self._link_entities_to_neo4j(llm_entities)

            if linked_entities:
                logger.info(f"实体识别: LLM识别到 {len(llm_entities)} 个实体，成功链接 {len(linked_entities)} 个到知识图谱")
                return linked_entities

        # 策略2: 如果 LLM 识别失败，使用规则匹配作为备选
        rule_entities = self._rule_based_entity_extraction(question)

        if rule_entities:
            logger.info(f"实体识别: 规则匹配找到 {len(rule_entities)} 个实体")
            return rule_entities

        logger.warning("实体识别: 所有方法均未找到实体")
        return []

    def _llm_extract_entities_structured(self, question: str) -> List[Dict]:
        """
        使用 LLM 进行结构化实体识别（主要方法）

        返回格式：包含实体名称和类型的字典列表
        """
        try:
            prompt = f"""你是一名专业的医疗实体识别专家。请从以下医疗问题中提取所有医疗实体，并判断每个实体的类型。

问题：{question}

请识别以下类型的医疗实体：
- Disease（疾病）：如感冒、高血压、糖尿病等
- Symptom（症状）：如头痛、发热、咳嗽、胸闷等
- Drug（药品）：如阿司匹林、布洛芬等
- Check（检查项）：如血常规、CT检查等
- Department（科室）：如内科、外科等

请以 JSON 格式返回结果，格式如下：
{{
  "entities": [
    {{"name": "实体名称", "type": "实体类型", "confidence": 0.9}},
    ...
  ]
}}

要求：
1. 只提取明确的医疗实体，不要提取疑问词、语气词等
2. 实体名称使用标准医学术语
3. 如果问题中没有医疗实体，返回 {{"entities": []}}
4. 只返回 JSON，不要其他解释

示例1：
问题：我头痛发热，可能是什么病？
{{
  "entities": [
    {{"name": "头痛", "type": "Symptom", "confidence": 0.95}},
    {{"name": "发热", "type": "Symptom", "confidence": 0.95}}
  ]
}}

示例2：
问题：感冒有什么症状？
{{
  "entities": [
    {{"name": "感冒", "type": "Disease", "confidence": 0.98}}
  ]
}}

示例3：
问题：高血压应该吃什么药？
{{
  "entities": [
    {{"name": "高血压", "type": "Disease", "confidence": 0.98}}
  ]
}}

JSON 结果："""

            # 使用 HumanMessage 符合 LangChain 0.3 API 规范
            response = self.llm.invoke([HumanMessage(content=prompt)])
            content = response.content.strip()

            # 尝试解析 JSON（可能包含 markdown 代码块）
            import json
            import re

            # 移除可能的 markdown 代码块标记
            content = re.sub(r'```json\s*', '', content)
            content = re.sub(r'```\s*', '', content)
            content = content.strip()

            # 尝试提取 JSON 部分
            json_match = re.search(r'\{[^{}]*"entities"[^{}]*\}', content, re.DOTALL)
            if json_match:
                content = json_match.group(0)

            try:
                result = json.loads(content)
                entities = result.get("entities", [])

                # 验证和清理实体数据
                valid_entities = []
                for entity in entities:
                    if isinstance(entity, dict) and "name" in entity and "type" in entity:
                        valid_entities.append({
                            "name": entity["name"].strip(),
                            "type": entity["type"].strip(),
                            "confidence": entity.get("confidence", 0.8)
                        })

                # 只在 DEBUG 模式下输出详细信息
                if logger.isEnabledFor(logging.DEBUG):
                    logger.debug(f"LLM 识别到 {len(valid_entities)} 个实体: {[e['name'] for e in valid_entities]}")
                return valid_entities

            except json.JSONDecodeError as e:
                logger.warning(f"LLM 返回的 JSON 解析失败: {e}, 原始内容: {content[:200]}")
                # 尝试回退到简单文本解析
                return self._fallback_text_parsing(content)

        except Exception as e:
            logger.error(f"LLM 实体识别失败: {e}", exc_info=True)
            return []

    def _fallback_text_parsing(self, content: str) -> List[Dict]:
        """当 JSON 解析失败时的回退方案：简单文本解析"""
        entities = []
        lines = content.split('\n')

        for line in lines:
            line = line.strip()
            if not line or line.startswith('{') or line.startswith('['):
                continue

            # 尝试提取实体名称（简单模式）
            # 假设格式可能是：实体名称 (类型) 或 实体名称: 类型
            import re
            match = re.search(r'["\']?([^"\']+)["\']?\s*[:\-]?\s*(\w+)', line)
            if match:
                name = match.group(1).strip()
                entity_type = match.group(2).strip()
                if len(name) >= 2:
                    entities.append({
                        "name": name,
                        "type": entity_type,
                        "confidence": 0.7
                    })

        return entities

    def _link_entities_to_neo4j(self, entities: List[Dict]) -> List[Dict]:
        """
        将 LLM 识别的实体链接到 Neo4j 知识图谱

        策略：
        1. 先尝试精确匹配（实体名称完全匹配）
        2. 如果失败，尝试模糊匹配
        3. 按实体类型优先级搜索
        """
        linked_entities = []
        seen_entities = set()

        for entity in entities:
            entity_name = entity.get("name", "").strip()
            entity_type = entity.get("type", "").strip()
            confidence = entity.get("confidence", 0.8)

            if not entity_name:
                continue

            # 映射 LLM 返回的类型到 Neo4j 标签
            type_mapping = {
                "Disease": "Disease",
                "Symptom": "Symptom",
                "Drug": "Drug",
                "Check": "Check",
                "Department": "Department"
            }

            neo4j_type = type_mapping.get(entity_type)

            # 策略1: 如果知道类型，先尝试精确匹配
            if neo4j_type:
                # 尝试精确匹配
                exact_match = self.neo4j.fuzzy_search_entity(
                    keyword=entity_name,
                    entity_type=neo4j_type,
                    limit=1
                )

                if exact_match:
                    matched = exact_match[0]
                    entity_key = (matched.get("name"), matched.get("type"))
                    if entity_key not in seen_entities:
                        seen_entities.add(entity_key)
                        matched["llm_confidence"] = confidence
                        linked_entities.append(matched)
                        # 只在 DEBUG 模式下输出详细信息
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"精确匹配: {entity_name} -> {matched.get('name')} ({matched.get('type')})")
                        continue

            # 策略2: 模糊匹配（所有类型）
            fuzzy_matches = self.neo4j.fuzzy_search_entity(
                keyword=entity_name,
                entity_type=None,
                limit=5
            )

            # 如果知道类型，优先选择匹配类型的实体
            if neo4j_type and fuzzy_matches:
                for match in fuzzy_matches:
                    if match.get("type") == neo4j_type:
                        entity_key = (match.get("name"), match.get("type"))
                        if entity_key not in seen_entities:
                            seen_entities.add(entity_key)
                            match["llm_confidence"] = confidence
                            linked_entities.append(match)
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(f"类型匹配: {entity_name} -> {match.get('name')} ({match.get('type')})")
                            break
                else:
                    # 如果没找到匹配类型的，使用第一个结果
                    if fuzzy_matches:
                        match = fuzzy_matches[0]
                        entity_key = (match.get("name"), match.get("type"))
                        if entity_key not in seen_entities:
                            seen_entities.add(entity_key)
                            match["llm_confidence"] = confidence
                            linked_entities.append(match)
                            if logger.isEnabledFor(logging.DEBUG):
                                logger.debug(f"模糊匹配: {entity_name} -> {match.get('name')} ({match.get('type')})")
            elif fuzzy_matches:
                # 不知道类型，使用第一个结果
                match = fuzzy_matches[0]
                entity_key = (match.get("name"), match.get("type"))
                if entity_key not in seen_entities:
                    seen_entities.add(entity_key)
                    match["llm_confidence"] = confidence
                    linked_entities.append(match)
                    logger.debug(f"模糊匹配: {entity_name} -> {match.get('name')} ({match.get('type')})")

        return linked_entities

    def _rule_based_entity_extraction(self, question: str) -> List[Dict]:
        """
        基于规则的实体提取（备选方案）

        当 LLM 识别失败时使用，作为快速补充
        """
        keywords = self._extract_keywords(question)
        # 只在 DEBUG 模式下输出详细信息
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"规则提取的关键词: {keywords}")

        if not keywords:
            return []

        linked_entities = []
        seen_entities = set()

        # 按优先级搜索
        entity_types_priority = ["Symptom", "Disease", "Drug", "Check", "Department"]

        for keyword in keywords:
            for entity_type in entity_types_priority:
                entities = self.neo4j.fuzzy_search_entity(
                    keyword=keyword,
                    entity_type=entity_type,
                    limit=3
                )

                for entity in entities:
                    entity_key = (entity.get("name"), entity.get("type"))
                    if entity_key not in seen_entities:
                        seen_entities.add(entity_key)
                        linked_entities.append(entity)
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"规则匹配: {entity.get('name')} ({entity.get('type')}) - 关键词: {keyword}")

        return linked_entities

    def _extract_keywords(self, question: str) -> List[str]:
        """
        从问题中提取关键词

        改进策略：
        1. 提取所有可能的医疗实体关键词（2-4字）
        2. 尝试提取完整短语（如"头痛发热"）
        3. 返回多种长度的关键词组合
        """
        import re

        # 移除常见停用词
        stop_words = {"的", "了", "是", "我", "有", "什么", "怎么", "如何", "应该", "可能", "怎么办", "会", "能", "要", "吗", "呢"}

        # 提取所有中文词
        words = re.findall(r'[\u4e00-\u9fa5]+', question)

        # 过滤停用词和单字，保留2-4字的词
        keywords = []
        for w in words:
            if w not in stop_words and 2 <= len(w) <= 4:
                keywords.append(w)

        # 策略1: 提取2-3字的组合词（如"头痛发热" -> ["头痛", "发热", "头痛发热"]）
        if len(words) >= 2:
            # 尝试提取相邻词的组合（2-3词组合）
            for i in range(len(words) - 1):
                if words[i] not in stop_words and words[i+1] not in stop_words:
                    combo2 = words[i] + words[i+1]
                    if 2 <= len(combo2) <= 4:
                        keywords.append(combo2)

                    # 3词组合
                    if i + 2 < len(words) and words[i+2] not in stop_words:
                        combo3 = words[i] + words[i+1] + words[i+2]
                        if 3 <= len(combo3) <= 6:
                            keywords.append(combo3)

        # 去重并保持顺序
        seen = set()
        unique_keywords = []
        for kw in keywords:
            if kw not in seen:
                seen.add(kw)
                unique_keywords.append(kw)

        # 按长度排序，优先使用较长的关键词（更精确）
        unique_keywords.sort(key=len, reverse=True)

        return unique_keywords

    def _retrieve_subgraph(self, entities: List[Dict], max_hops: int) -> Dict:
        """
        检索知识子图

        从实体节点出发，检索多跳关系，收集相关节点
        """
        subgraph = {
            "diseases": [],
            "symptoms": [],
            "drugs": [],
            "checks": [],
            "departments": [],
            "relationships": []
        }

        seen_diseases = set()
        seen_symptoms = set()
        seen_drugs = set()
        seen_checks = set()
        seen_departments = set()

        for entity in entities:
            entity_type = entity.get("type")
            entity_name = entity.get("name")

            if entity_type == "Symptom":
                # 从症状出发，查找相关疾病
                diseases = self.neo4j.find_diseases_by_symptoms([entity_name], top_k=10)

                for disease in diseases:
                    if disease["name"] not in seen_diseases:
                        seen_diseases.add(disease["name"])
                        subgraph["diseases"].append(disease)

                        # 获取疾病的完整上下文（1跳）
                        context = self.neo4j.get_disease_full_context(disease["name"])
                        if context:
                            # 收集相关症状
                            for symptom in context.get("symptoms", [])[:10]:
                                if symptom.get("name") and symptom.get("name") not in seen_symptoms:
                                    seen_symptoms.add(symptom["name"])
                                    subgraph["symptoms"].append(symptom)

                            # 收集药品
                            for drug in context.get("drugs", [])[:10]:
                                if drug.get("name") and drug.get("name") not in seen_drugs:
                                    seen_drugs.add(drug["name"])
                                    subgraph["drugs"].append(drug)

                            # 收集检查
                            for check in context.get("checks", [])[:10]:
                                if check.get("name") and check.get("name") not in seen_checks:
                                    seen_checks.add(check["name"])
                                    subgraph["checks"].append(check)

                            # 收集科室
                            for dept in context.get("departments", [])[:5]:
                                if dept and dept not in seen_departments:
                                    seen_departments.add(dept)
                                    subgraph["departments"].append({"name": dept})

            elif entity_type == "Disease":
                # 获取疾病的完整上下文
                context = self.neo4j.get_disease_full_context(entity_name)
                if context:
                    if entity_name not in seen_diseases:
                        seen_diseases.add(entity_name)
                        disease_info = context.get("disease", {})
                        subgraph["diseases"].append({
                            "name": entity_name,
                            "description": disease_info.get("desc", "")
                        })

                    # 收集相关症状
                    for symptom in context.get("symptoms", [])[:10]:
                        if symptom.get("name") and symptom.get("name") not in seen_symptoms:
                            seen_symptoms.add(symptom["name"])
                            subgraph["symptoms"].append(symptom)

                    # 收集药品
                    for drug in context.get("drugs", [])[:10]:
                        if drug.get("name") and drug.get("name") not in seen_drugs:
                            seen_drugs.add(drug["name"])
                            subgraph["drugs"].append(drug)

                    # 收集检查
                    for check in context.get("checks", [])[:10]:
                        if check.get("name") and check.get("name") not in seen_checks:
                            seen_checks.add(check["name"])
                            subgraph["checks"].append(check)

                    # 收集科室
                    for dept in context.get("departments", [])[:5]:
                        if dept and dept not in seen_departments:
                            seen_departments.add(dept)
                            subgraph["departments"].append({"name": dept})

            elif entity_type == "Drug":
                # 从药品出发，查找相关疾病（反向查询）
                # 注意：neo4j_service 可能没有这个方法，这里简化处理
                # 可以后续扩展
                pass

        return subgraph

    def _build_knowledge_context(self, subgraph: Dict) -> str:
        """
        将子图转换为结构化的知识上下文
        """
        context_parts = []

        # 疾病信息
        if subgraph.get("diseases"):
            context_parts.append("## 相关疾病：")
            for disease in subgraph["diseases"][:5]:
                name = disease.get("name", "")
                desc = disease.get("description", disease.get("desc", ""))
                match_score = disease.get("match_score", "")

                disease_info = f"- {name}"
                if desc:
                    disease_info += f": {desc}"
                if match_score:
                    disease_info += f" (匹配度: {match_score:.2f})"

                context_parts.append(disease_info)

        # 症状信息
        if subgraph.get("symptoms"):
            context_parts.append("\n## 相关症状：")
            for symptom in subgraph["symptoms"][:10]:
                name = symptom.get("name", "")
                weight = symptom.get("weight", "")

                symptom_info = f"- {name}"
                if weight:
                    symptom_info += f" (相关性: {weight})"

                context_parts.append(symptom_info)

        # 药品信息
        if subgraph.get("drugs"):
            context_parts.append("\n## 相关药品：")
            for drug in subgraph["drugs"][:10]:
                name = drug.get("name", "")
                usage = drug.get("usage", "")

                drug_info = f"- {name}"
                if usage:
                    drug_info += f" (用法: {usage})"

                context_parts.append(drug_info)

        # 检查信息
        if subgraph.get("checks"):
            context_parts.append("\n## 相关检查：")
            for check in subgraph["checks"][:10]:
                name = check.get("name", "")
                priority = check.get("priority", "")

                check_info = f"- {name}"
                if priority:
                    check_info += f" (优先级: {priority})"

                context_parts.append(check_info)

        # 科室信息
        if subgraph.get("departments"):
            context_parts.append("\n## 相关科室：")
            for dept in subgraph["departments"][:5]:
                name = dept.get("name", "")
                if name:
                    context_parts.append(f"- {name}")

        return "\n".join(context_parts) if context_parts else "未找到相关信息"

    def _build_rag_prompt(self, question: str, context: str) -> str:
        """
        构建 RAG 提示词
        """
        prompt = f"""你是一名专业的医疗诊断助手。请基于以下知识库信息回答用户的问题。

## 知识库信息：
{context}

## 用户问题：
{question}

## 要求：
1. 请基于上述知识库信息回答问题，不要编造不存在的内容
2. 如果知识库中没有相关信息，请明确说明"根据现有知识库，未找到相关信息"
3. 在回答中引用具体的疾病名称、症状、药品等实体
4. 使用通俗易懂的语言，适合患者理解
5. 提供专业但谨慎的建议，提醒用户咨询专业医生
6. 如果涉及用药建议，请明确说明"以上信息仅供参考，具体用药请咨询专业医生"

## 回答：
"""
        return prompt

    def _generate_answer(self, prompt: str) -> str:
        """
        调用 LLM 生成答案

        使用 LangChain 0.3 标准的消息格式
        """
        try:
            # 使用 HumanMessage 符合 LangChain 0.3 API 规范
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.error(f"LLM 生成失败: {e}", exc_info=True)
            return f"抱歉，生成答案时出现错误: {str(e)}"

    def _extract_citations(self, subgraph: Dict) -> List[Dict]:
        """
        提取引用来源
        """
        citations = []

        # 提取疾病引用
        for disease in subgraph.get("diseases", [])[:5]:
            citations.append({
                "type": "Disease",
                "name": disease.get("name"),
                "description": disease.get("description", disease.get("desc", ""))
            })

        # 提取症状引用
        for symptom in subgraph.get("symptoms", [])[:5]:
            citations.append({
                "type": "Symptom",
                "name": symptom.get("name"),
                "weight": symptom.get("weight")
            })

        return citations

    def _summarize_context(self, context: str) -> str:
        """
        生成上下文摘要（用于调试和日志）
        """
        lines = context.split("\n")
        summary_lines = []

        for line in lines[:10]:  # 只取前10行
            if line.strip():
                summary_lines.append(line)

        return "\n".join(summary_lines)


# 单例模式
_graphrag_service_instance = None

def get_graphrag_service() -> GraphRAGService:
    """获取 GraphRAG 服务单例"""
    global _graphrag_service_instance
    if _graphrag_service_instance is None:
        _graphrag_service_instance = GraphRAGService()
    return _graphrag_service_instance


# 测试代码
if __name__ == "__main__":
    import logging
    # 设置日志级别为 INFO，只显示重要信息
    # 禁用第三方库的详细日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 禁用第三方库的详细日志（减少噪音）
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    # 禁用 Neo4j 的 notifications 警告（这些是属性不存在的警告，不影响功能）
    logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

    # 测试服务初始化
    print("=" * 50)
    print("测试 GraphRAG 服务")
    print("=" * 50)

    service = get_graphrag_service()

    # 测试查询
    test_questions = [
        "我脑袋痛，早上起床口干舌燥，可能是什么病？",
        "我四肢无力,整天都昏沉沉的,是什么病？",
        "我天天吃不好，睡不好，一有动静就醒了是什么病？"
    ]

    for question in test_questions:
        print(f"\n问题: {question}")
        print("-" * 50)

        result = service.query(question, max_hops=2)

        print(f"答案: {result['answer']}")
        print(f"\n识别到的实体: {len(result['entities'])} 个")
        for entity in result['entities'][:3]:
            print(f"  - {entity.get('name')} ({entity.get('type')})")

        print(f"\n引用来源: {len(result['citations'])} 个")
        for citation in result['citations'][:3]:
            print(f"  - {citation.get('name')} ({citation.get('type')})")

        print("\n" + "=" * 50)