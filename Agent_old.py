import os
from idlelib.rpc import response_queue

from langchain import tools
from langchain.agents import create_agent
from langchain_classic.memory import ConversationBufferMemory
from langchain_community.graphs import Neo4jGraph
from langchain_openai import ChatOpenAI
import dotenv
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.messages import HumanMessage
from langchain_community.embeddings import HuggingFaceEmbeddings
dotenv.load_dotenv()


graph = Neo4jGraph(
    url=os.getenv("NEO4J_HOST"),
    username=os.getenv("NEO4J_USER"),
    password=os.getenv("NEO4J_PASSWORD")
)



embedding_model = HuggingFaceEmbeddings(
    model_name=os.getenv("EMBEDDING_MODEL_PATH")
)


# 初始化LLM
llm = ChatOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    temperature=0)


system_prompt = """你是一个专业的医疗诊断助手。你可以：
1. 根据症状诊断可能的疾病
2. 查询疾病的详细信息
3. 提供治疗方案建议


请根据用户的问题，选择合适的工具进行查询，然后提供专业、准确的医疗建议。
所有回答必须基于工具返回的知识库信息，不要编造内容。
"""


# 创建 Agent
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
    middleware=[],
)

#  流式输出
def ask_question_stream(question: str):
    """流式输出答案"""
    for chunk in agent.stream({
        "messages": [
            HumanMessage(content=question)
        ]
    }):
        # 处理流式输出
        if "messages" in chunk:
            for msg in chunk["messages"]:
                if hasattr(msg, "content"):
                    print(msg.content, end="", flush=True)


