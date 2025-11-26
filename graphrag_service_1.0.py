"""
基于 LangChain 1.0 的 GraphRAG 服务重构

使用 LangChain 1.0 核心特性：
1. 统一的 create_agent API
2. 中间件机制
3. 结构化输出
4. LCEL 声明式组合
"""

import os
import logging
from typing import List, Dict, Optional, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.agents import create_agent
from langchain.agents.middleware import before_model, wrap_tool_call
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from neo4j_service import get_neo4j_service

load_dotenv()
logger = logging.getLogger(__name__)

# 定义数据结构
class Entity(BaseModel):
    """实体数据结构"""
    name: str = Field(description="实体名称")
    type: str = Field(description="实体类型")
    confidence: float = Field(description="置信度", ge=0, le=1)

class Entities(BaseModel):
    """实体列表"""
    entities: List[Entity] = Field(description="识别的实体列表")

class GraphRAGResult(BaseModel):
    """GraphRAG 结果"""
    answer: str = Field(description="生成的答案")
    entities: List[Dict] = Field(description="识别到的实体")
    context_summary: str = Field(description="上下文摘要")
    citations: List[Dict] = Field(description="引用来源")

class GraphRAGServiceV1:
    """基于 LangChain 1.0 的 GraphRAG 服务"""

    def __init__(self):
        """初始化 GraphRAG 服务"""
        self.neo4j = get_neo4j_service()

        # 初始化 LLM
        self.llm = ChatOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
            model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            temperature=0.7
        )

        # 构建工具
        self.tools = [
            self._create_entity_extraction_tool(),
            self._create_subgraph_retrieval_tool(),
            self._create_answer_generation_tool()
        ]

        # 创建 Agent
        self.agent = self._build_agent()

        logger.info("GraphRAG 1.0 服务初始化完成")

    def _build_agent(self):
        """使用 create_agent 构建代理"""
        try:
            # LangChain 1.0 统一的 Agent 创建方式
            system_prompt = """你是一名专业的医疗诊断助手。请基于知识图谱信息回答用户的问题。

要求：
1. 基于知识库信息回答问题，不要编造不存在的内容
2. 如果知识库中没有相关信息，请明确说明
3. 在回答中引用具体的疾病名称、症状、药品等实体
4. 使用通俗易懂的语言，适合患者理解
5. 提供专业但谨慎的建议，提醒用户咨询专业医生
6. 如果涉及用药建议，请明确说明"以上信息仅供参考，具体用药请咨询专业医生"
"""
            return create_agent(
                tools=self.tools,
                model=self.llm,
                system_prompt=system_prompt,
                # 可以添加中间件配置
                # middleware=[...]
            )
        except Exception as e:
            logger.error(f"创建 Agent 失败: {e}")
            raise

    def _create_entity_extraction_tool(self):
        @tool("extract_entities",description="从问题中提取医疗实体并返回JSON格式")
        def extract_entities(question: str) -> Dict[str, Any]:
            try:
                entity_prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content="""你是专业医疗实体识别专家，从问题中提取医疗实体并返回 JSON 格式。

    实体类型：
    - Disease（疾病）：感冒、高血压等
    - Symptom（症状）：头痛、发热等
    - Drug（药品）：阿司匹林等
    - Check（检查项）：血常规等
    - Department（科室）：内科等

    要求：
    1. 实体名称用标准医学术语（如"鸡巴疼痛"→"阴茎疼痛"）
    2. 只返回 JSON，不要其他解释
    3. 包含 confidence 字段（0-1 之间）
    4. 无实体返回 {"entities": []}

    示例：
    问题：我头痛发热，可能是什么病？
    {"entities": [{"name": "头痛", "type": "Symptom", "confidence": 0.95}, {"name": "发热", "type": "Symptom", "confidence": 0.95}]}

    JSON 结果："""),
                    HumanMessage(content="{question}")
                ])

                entity_chain = entity_prompt | self.llm
                response = entity_chain.invoke({"question": question})
                content = response.content.strip()

                # 解析 JSON（处理 markdown 代码块）
                import json
                import re
                content = re.sub(r'```json\s*|\s*```', '', content)
                result = json.loads(content)
                raw_entities = result.get("entities", [])

                # 链接到 Neo4j
                linked_entities = self._link_entities_to_neo4j([Entity(**e) for e in raw_entities])

                return {"entities": linked_entities, "raw_entities": raw_entities}
            except Exception as e:
                logger.error(f"实体识别失败: {e}")
                return {"entities": [], "raw_entities": []}

        return extract_entities

    def _create_subgraph_retrieval_tool(self):
        """创建子图检索工具"""
        @tool
        def retrieve_subgraph(entities: List[Dict], max_hops: int = 2) -> Dict[str, Any]:
            """从知识图谱中检索相关子图"""
            try:
                subgraph = {
                    "diseases": [],
                    "symptoms": [],
                    "drugs": [],
                    "checks": [],
                    "departments": [],
                    "relationships": []
                }

                seen_entities = {
                    "diseases": set(),
                    "symptoms": set(),
                    "drugs": set(),
                    "checks": set(),
                    "departments": set()
                }

                for entity in entities:
                    entity_type = entity.get("type")
                    entity_name = entity.get("name")

                    if entity_type == "Symptom":
                        diseases = self.neo4j.find_diseases_by_symptoms([entity_name], top_k=10)
                        self._process_disease_context(diseases, subgraph, seen_entities)

                    elif entity_type == "Disease":
                        context = self.neo4j.get_disease_full_context(entity_name)
                        if context:
                            self._process_disease_context([{"name": entity_name}], subgraph, seen_entities)

                # 构建知识上下文
                context = self._build_knowledge_context(subgraph)

                return {
                    "subgraph": subgraph,
                    "context": context,
                    "summary": self._summarize_context(context)
                }

            except Exception as e:
                logger.error(f"子图检索失败: {e}")
                return {"subgraph": {}, "context": "", "summary": ""}

        return retrieve_subgraph

    def _create_answer_generation_tool(self):
        """创建答案生成工具"""
        @tool
        def generate_answer(question: str, context: str) -> Dict[str, Any]:
            """基于上下文生成答案"""
            try:
                prompt = ChatPromptTemplate.from_messages([
                    SystemMessage(content="""你是一名专业的医疗诊断助手。请基于知识库信息回答用户的问题。

要求：
1. 基于提供的知识库信息回答问题
2. 不要编造不存在的内容
3. 引用具体的疾病名称、症状、药品等实体
4. 使用通俗易懂的语言
5. 提醒用户咨询专业医生"""),
                    HumanMessage(content=f"""## 知识库信息：
{context}

## 用户问题：
{question}

请基于以上信息回答：""")
                ])

                response = (prompt | self.llm).invoke({"question": question, "context": context})

                return {
                    "answer": response.content,
                    "sources_used": len([line for line in context.split('\n') if line.strip()])
                }

            except Exception as e:
                logger.error(f"答案生成失败: {e}")
                return {"answer": f"抱歉，生成答案时出现错误: {str(e)}", "sources_used": 0}

        return generate_answer

    def _process_disease_context(self, diseases, subgraph, seen_entities):
        """处理疾病上下文信息"""
        for disease in diseases:
            disease_name = disease.get("name")
            if disease_name and disease_name not in seen_entities["diseases"]:
                seen_entities["diseases"].add(disease_name)
                subgraph["diseases"].append(disease)

                # 获取完整上下文
                context = self.neo4j.get_disease_full_context(disease_name)
                if context:
                    self._collect_related_entities(context, subgraph, seen_entities)

    def _collect_related_entities(self, context, subgraph, seen_entities):
        """收集相关实体"""
        # 收集症状
        for symptom in context.get("symptoms", [])[:10]:
            name = symptom.get("name")
            if name and name not in seen_entities["symptoms"]:
                seen_entities["symptoms"].add(name)
                subgraph["symptoms"].append(symptom)

        # 收集药品
        for drug in context.get("drugs", [])[:10]:
            name = drug.get("name")
            if name and name not in seen_entities["drugs"]:
                seen_entities["drugs"].add(name)
                subgraph["drugs"].append(drug)

        # 收集检查
        for check in context.get("checks", [])[:10]:
            name = check.get("name")
            if name and name not in seen_entities["checks"]:
                seen_entities["checks"].add(name)
                subgraph["checks"].append(check)

        # 收集科室
        for dept in context.get("departments", [])[:5]:
            if dept and dept not in seen_entities["departments"]:
                seen_entities["departments"].add(dept)
                subgraph["departments"].append({"name": dept})

    def _link_entities_to_neo4j(self, entities: List[Entity]) -> List[Dict]:
        """将实体链接到 Neo4j 知识图谱"""
        linked_entities = []
        seen_entities = set()

        for entity in entities:
            entity_name = entity.name
            entity_type = entity.type

            # 在 Neo4j 中搜索实体
            matches = self.neo4j.fuzzy_search_entity(
                keyword=entity_name,
                entity_type=entity_type,
                limit=3
            )

            for match in matches:
                entity_key = (match.get("name"), match.get("type"))
                if entity_key not in seen_entities:
                    seen_entities.add(entity_key)
                    match["llm_confidence"] = entity.confidence
                    linked_entities.append(match)

        return linked_entities

    def _build_knowledge_context(self, subgraph: Dict) -> str:
        """构建知识上下文"""
        context_parts = []

        if subgraph.get("diseases"):
            context_parts.append("## 相关疾病：")
            for disease in subgraph["diseases"][:5]:
                name = disease.get("name", "")
                desc = disease.get("description", disease.get("desc", ""))
                info = f"- {name}"
                if desc:
                    info += f": {desc}"
                context_parts.append(info)

        if subgraph.get("symptoms"):
            context_parts.append("\n## 相关症状：")
            for symptom in subgraph["symptoms"][:10]:
                context_parts.append(f"- {symptom.get('name', '')}")

        if subgraph.get("drugs"):
            context_parts.append("\n## 相关药品：")
            for drug in subgraph["drugs"][:10]:
                context_parts.append(f"- {drug.get('name', '')}")

        return "\n".join(context_parts) if context_parts else "未找到相关信息"

    def _summarize_context(self, context: str) -> str:
        """生成上下文摘要"""
        lines = [line for line in context.split('\n') if line.strip()]
        return "\n".join(lines[:10])

    def _extract_citations(self, subgraph: Dict) -> List[Dict]:
        """提取引用来源"""
        citations = []

        for disease in subgraph.get("diseases", [])[:5]:
            citations.append({
                "type": "Disease",
                "name": disease.get("name"),
                "description": disease.get("description", disease.get("desc", ""))
            })

        for symptom in subgraph.get("symptoms", [])[:5]:
            citations.append({
                "type": "Symptom",
                "name": symptom.get("name")
            })

        return citations

    def query(self, question: str, max_hops: int = 2) -> GraphRAGResult:

        """
        GraphRAG 查询流程

        Args:
            question: 用户问题
            max_hops: 最大跳数

        Returns:
            GraphRAGResult: 包含答案、实体、上下文和引用的结果
        """

        try:
            # 1. 调用 Agent，执行工具链
            agent_result = self.agent.invoke({"input": question, "max_hops": max_hops})

            # 2. 从 Agent 结果中提取 extract_entities 工具的返回值（关键修复）
            entities = []
            # 遍历所有工具调用记录
            for tool_call in agent_result.get("tool_calls", []):
                if tool_call.get("name") == "extract_entities":
                    # 工具返回的结果在 tool_call["output"] 中（JSON 字符串）
                    tool_output = tool_call.get("output", "{}")
                    import json
                    try:
                        output_data = json.loads(tool_output)
                        entities = output_data.get("entities", [])
                        break  # 找到实体提取工具的结果，退出循环
                    except json.JSONDecodeError:
                        logger.error("解析 extract_entities 工具输出失败")

            if not entities:
                return GraphRAGResult(
                    answer="抱歉，我无法从您的问题中识别出相关的医疗实体。请尝试使用更具体的疾病名称或症状描述。",
                    entities=[],
                    context_summary="",
                    citations=[]
                )

            # 检索子图
            subgraph_result = self.retrieve_subgraph.invoke({
                "entities": entities,
                "max_hops": max_hops
            })

            # 生成答案
            answer_result = self.generate_answer.invoke({
                "question": question,
                "context": subgraph_result["context"]
            })

            # 提取引用
            citations = self._extract_citations(subgraph_result["subgraph"])

            return GraphRAGResult(
                answer=answer_result["answer"],
                entities=entities,
                context_summary=subgraph_result["summary"],
                citations=citations
            )

        except Exception as e:
            logger.error(f"GraphRAG 查询失败: {e}")
            return GraphRAGResult(
                answer=f"抱歉，处理您的问题时出现错误: {str(e)}",
                entities=[],
                context_summary="",
                citations=[]
            )

# 中间件示例
@before_model
def log_model_calls(state, runtime):
    """记录模型调用日志"""
    logger.info(f"模型调用: {state.get('messages', [])[-1] if state.get('messages') else 'Unknown'}")
    return state

@wrap_tool_call
def validate_tool_inputs(req, handler):
    """验证工具输入"""
    logger.info(f"工具调用: {req.tool_name} with {req.tool_input}")
    return handler(req)

# 单例模式
_graphrag_service_v1_instance = None

def get_graphrag_service_v1() -> GraphRAGServiceV1:
    """获取 GraphRAG 1.0 服务单例"""
    global _graphrag_service_v1_instance
    if _graphrag_service_v1_instance is None:
        _graphrag_service_v1_instance = GraphRAGServiceV1()
    return _graphrag_service_v1_instance

# 测试代码
if __name__ == "__main__":
    import logging

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 测试服务
    service = get_graphrag_service_v1()

    test_questions = [
        "我脑袋痛，早上起床口干舌燥，可能是什么病？",
        "我四肢无力,整天都昏沉沉的,是什么病？",
        "我天天吃不好，睡不好，一有动静就醒了是什么病？"
    ]

    for question in test_questions:
        print(f"\n问题: {question}")
        print("-" * 50)

        result = service.query(question)

        print(f"答案: {result.answer}")
        print(f"识别实体: {len(result.entities)} 个")
        for entity in result.entities[:3]:
            print(f"  - {entity.get('name')} ({entity.get('type')})")

        print(f"引用: {len(result.citations)} 个")
        print("\n" + "=" * 50)