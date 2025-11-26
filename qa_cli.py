"""
交互式医疗问答 CLI 程序

支持连续对话、历史记录、多轮对话等功能
"""

import os
import sys
import logging
from typing import List, Dict, Optional
from datetime import datetime
from dotenv import load_dotenv
from graphrag_service import get_graphrag_service

load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("neo4j.notifications").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)


class QAConversation:
    """对话会话管理"""
    
    def __init__(self):
        self.history: List[Dict[str, str]] = []
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def add_message(self, role: str, content: str):
        """添加消息到历史"""
        self.history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
    
    def get_conversation_context(self, max_messages: int = 5) -> str:
        """获取最近的对话上下文"""
        if not self.history:
            return ""
        
        recent_messages = self.history[-max_messages:]
        context_parts = []
        for msg in recent_messages:
            role_label = "用户" if msg["role"] == "user" else "助手"
            context_parts.append(f"{role_label}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    def clear_history(self):
        """清空对话历史"""
        self.history.clear()
        logger.info("对话历史已清空")
    
    def print_history(self):
        """打印对话历史"""
        if not self.history:
            print("暂无对话历史")
            return
        
        print("\n" + "=" * 60)
        print("对话历史")
        print("=" * 60)
        for i, msg in enumerate(self.history, 1):
            role_label = "用户" if msg["role"] == "user" else "助手"
            print(f"\n[{i}] {role_label} ({msg.get('timestamp', '')[:19]}):")
            print(f"    {msg['content']}")
        print("=" * 60 + "\n")


class InteractiveQA:
    """交互式问答主程序"""
    
    def __init__(self):
        self.service = get_graphrag_service()
        self.conversation = QAConversation()
        self.running = True
    
    def print_welcome(self):
        """打印欢迎信息"""
        print("\n" + "=" * 60)
        print("🏥 医疗诊断智能问答系统 (GraphRAG)")
        print("=" * 60)
        print("\n使用说明:")
        print("  - 直接输入您的问题，按回车提交")
        print("  - 输入 'quit' 或 'exit' 退出程序")
        print("  - 输入 'clear' 清空对话历史")
        print("  - 输入 'history' 查看对话历史")
        print("  - 输入 'help' 显示帮助信息")
        print("  - 输入 'about' 查看系统信息")
        print("\n提示: 可以连续提问，系统会基于上下文回答")
        print("=" * 60 + "\n")
    
    def print_help(self):
        """打印帮助信息"""
        print("\n" + "=" * 60)
        print("帮助信息")
        print("=" * 60)
        print("\n可用命令:")
        print("  help       - 显示此帮助信息")
        print("  history    - 显示对话历史")
        print("  clear      - 清空对话历史")
        print("  about      - 显示系统信息")
        print("  quit/exit  - 退出程序")
        print("\n使用示例:")
        print("  问题: 我头痛发热，可能是什么病？")
        print("  问题: 这种病需要做什么检查？")
        print("  问题: 应该吃什么药？")
        print("=" * 60 + "\n")
    
    def print_about(self):
        """打印系统信息"""
        print("\n" + "=" * 60)
        print("系统信息")
        print("=" * 60)
        print("\n系统名称: 医疗诊断智能问答系统")
        print("核心技术: GraphRAG (图谱检索增强生成)")
        print("知识图谱: Neo4j")
        print("LLM 模型: DeepSeek")
        print("\n功能特性:")
        print("  ✓ 智能实体识别")
        print("  ✓ 知识图谱检索")
        print("  ✓ 上下文感知回答")
        print("  ✓ 引用来源追踪")
        print("=" * 60 + "\n")
    
    def process_question(self, question: str) -> Optional[Dict]:
        """处理用户问题"""
        if not question.strip():
            return None
        
        print("\n🤔 正在思考...")
        
        try:
            # 获取最近的对话上下文（如果有）
            context = self.conversation.get_conversation_context()
            
            # 如果有上下文，增强问题
            enhanced_question = question
            if context:
                enhanced_question = f"{context}\n\n当前问题: {question}"
            
            # 调用 GraphRAG 服务
            result = self.service.query(question, max_hops=2)
            
            return result
            
        except Exception as e:
            logger.error(f"处理问题失败: {e}", exc_info=True)
            return {
                "answer": f"抱歉，处理您的问题时出现错误: {str(e)}",
                "entities": [],
                "context_summary": "",
                "citations": []
            }
    
    def display_answer(self, result: Dict):
        """显示答案和相关信息"""
        answer = result.get("answer", "抱歉，无法生成答案")
        entities = result.get("entities", [])
        citations = result.get("citations", [])
        
        # 显示答案
        print("\n" + "=" * 60)
        print("💡 回答:")
        print("=" * 60)
        print(answer)
        print("=" * 60)
        
        # 显示识别的实体
        if entities:
            print(f"\n📋 识别到 {len(entities)} 个医疗实体:")
            for entity in entities[:5]:  # 最多显示5个
                name = entity.get("name", "")
                entity_type = entity.get("type", "")
                type_map = {
                    "Disease": "疾病",
                    "Symptom": "症状",
                    "Drug": "药品",
                    "Check": "检查",
                    "Department": "科室"
                }
                type_label = type_map.get(entity_type, entity_type)
                print(f"  • {name} ({type_label})")
        
        # 显示引用来源
        if citations:
            print(f"\n📚 引用来源 ({len(citations)} 个):")
            for citation in citations[:3]:  # 最多显示3个
                name = citation.get("name", "")
                citation_type = citation.get("type", "")
                type_map = {
                    "Disease": "疾病",
                    "Symptom": "症状",
                    "Drug": "药品",
                    "Check": "检查"
                }
                type_label = type_map.get(citation_type, citation_type)
                print(f"  • {name} ({type_label})")
        
        print()  # 空行
    
    def handle_command(self, command: str) -> bool:
        """处理特殊命令，返回 True 表示已处理"""
        command = command.strip().lower()
        
        if command in ['quit', 'exit', 'q']:
            print("\n👋 感谢使用，再见！\n")
            self.running = False
            return True
        
        elif command == 'help':
            self.print_help()
            return True
        
        elif command == 'clear':
            self.conversation.clear_history()
            print("✅ 对话历史已清空\n")
            return True
        
        elif command == 'history':
            self.conversation.print_history()
            return True
        
        elif command == 'about':
            self.print_about()
            return True
        
        return False
    
    def run(self):
        """运行主循环"""
        self.print_welcome()
        
        while self.running:
            try:
                # 获取用户输入
                question = input("\n💬 请输入您的问题 (输入 'help' 查看帮助): ").strip()
                
                # 处理空输入
                if not question:
                    continue
                
                # 处理特殊命令
                if self.handle_command(question):
                    continue
                
                # 记录用户问题
                self.conversation.add_message("user", question)
                
                # 处理问题并获取答案
                result = self.process_question(question)
                
                if result:
                    # 显示答案
                    self.display_answer(result)
                    
                    # 记录助手回答
                    answer = result.get("answer", "")
                    if answer:
                        self.conversation.add_message("assistant", answer)
                
            except KeyboardInterrupt:
                print("\n\n⚠️  程序被中断")
                confirm = input("是否退出? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.running = False
                else:
                    print("继续运行...")
            
            except EOFError:
                print("\n\n👋 感谢使用，再见！\n")
                self.running = False
            
            except Exception as e:
                logger.error(f"运行错误: {e}", exc_info=True)
                print(f"\n❌ 发生错误: {str(e)}")
                print("程序将继续运行，您可以继续提问。\n")


def main():
    """主函数"""
    try:
        qa = InteractiveQA()
        qa.run()
    except Exception as e:
        logger.error(f"程序启动失败: {e}", exc_info=True)
        print(f"\n❌ 程序启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()

