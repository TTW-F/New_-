"""
数据模型和 Schema 定义
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class ToolCall:
    """工具调用记录"""
    id: str                          # 调用 ID
    name: str                        # 工具名称
    arguments: Dict[str, Any]        # 调用参数
    result: Optional[str] = None     # 执行结果
    error: Optional[str] = None      # 错误信息
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResponse:
    """Agent 响应"""
    answer: str                                    # 最终答案
    tool_calls: List[ToolCall] = field(default_factory=list)  # 工具调用记录
    entities: List[Dict] = field(default_factory=list)        # 识别的实体
    citations: List[Dict] = field(default_factory=list)       # 引用来源
    error: Optional[str] = None                    # 错误信息
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "answer": self.answer,
            "tool_calls": [
                {
                    "id": tc.id,
                    "name": tc.name,
                    "arguments": tc.arguments,
                    "result": tc.result,
                    "error": tc.error,
                    "timestamp": tc.timestamp
                }
                for tc in self.tool_calls
            ],
            "entities": self.entities,
            "citations": self.citations,
            "error": self.error
        }


@dataclass 
class Tool:
    """工具定义"""
    name: str                        # 工具名称
    description: str                 # 工具描述
    parameters: Dict[str, Any]       # 参数 Schema
    func: Any                        # 执行函数
    
    def to_openai_schema(self) -> Dict:
        """转换为 OpenAI Function Calling Schema"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }


# 系统提示词
SYSTEM_PROMPT = """你是一个专业的医疗诊断助手。你可以使用以下工具来帮助用户：

1. diagnose_by_symptoms - 根据症状诊断可能的疾病
2. search_disease_info - 查询疾病详细信息
3. get_treatment_plan - 获取治疗方案
4. search_drugs - 查询推荐药物
5. fuzzy_search - 模糊搜索医疗实体

重要规则：
- 所有回答必须基于工具返回的知识库信息，不要编造内容
- 涉及用药建议时，必须提醒用户咨询专业医生
- 遇到紧急情况（如胸痛、呼吸困难、大出血），建议立即就医或拨打急救电话
- 使用专业但通俗易懂的语言
- 如果用户描述的症状不明确，请先询问更多细节

请根据用户的问题，选择合适的工具进行查询，然后提供专业、准确的医疗建议。
"""

# 药品相关关键词（用于检测是否需要添加免责声明）
DRUG_KEYWORDS = [
    "药", "药物", "用药", "服药", "吃药", "药品", "处方", "剂量",
    "片", "胶囊", "注射", "口服", "外用", "滴剂"
]

# 紧急情况关键词
EMERGENCY_KEYWORDS = [
    "胸痛", "心脏病", "心梗", "中风", "脑溢血", "大出血", "呼吸困难",
    "窒息", "昏迷", "休克", "抽搐", "癫痫发作", "严重过敏", "自杀", "自残"
]

# 免责声明
DRUG_DISCLAIMER = "\n\n⚠️ 以上信息仅供参考，具体用药请咨询专业医生或药师。"

EMERGENCY_WARNING = "\n\n🚨 您描述的情况可能是紧急情况，请立即就医或拨打急救电话（120）！"
