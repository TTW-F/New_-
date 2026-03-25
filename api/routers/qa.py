"""
问答路由

处理医疗问答相关的 API 端点
使用 MedicalAgent 提供智能问答服务
"""

import logging
import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.schemas.qa import QARequest, QAResponse, QAErrorResponse
from api.services.qa_service import QAService
from api.security.jwt import get_current_user_optional
from api.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/qa", tags=["问答"])


@router.post(
    "",
    response_model=QAResponse,
    responses={
        500: {"model": QAErrorResponse, "description": "服务器错误"}
    }
)
async def ask_question(
    request: QARequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    提交问答请求
    
    向医疗问答系统提交问题，获取基于知识图谱的智能回答。
    
    - 支持匿名访问（不保存对话历史）
    - 登录用户的对话会自动保存到历史记录
    - 可通过 session_id 关联多轮对话
    - 使用 MedicalAgent 进行智能工具选择和推理
    
    **请求参数：**
    - **question**: 用户问题（1-1000字符）
    - **session_id**: 会话 ID（可选，用于关联多轮对话）
    
    **响应包含：**
    - 智能生成的回答
    - 识别的医疗实体（疾病、症状、药品等）
    - 工具调用记录
    - 响应时间
    """
    qa_service = QAService(db)
    user_id = current_user.id if current_user else None
    
    try:
        result = qa_service.process_question(
            question=request.question,
            user_id=user_id,
            session_id=request.session_id
        )
        
        if "error" in result:
            logger.warning(f"问答处理出现错误: {result.get('error')}")
        
        return QAResponse(
            question_id=result["question_id"],
            session_id=result["session_id"],
            question=result["question"],
            answer=result["answer"],
            entities=result.get("entities", []),
            citations=result.get("citations", []),
            response_time_ms=result["response_time_ms"]
        )
        
    except RuntimeError as e:
        logger.error(f"MedicalAgent 服务错误: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="问答服务暂时不可用，请稍后重试"
        )
        
    except Exception as e:
        logger.error(f"问答处理失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="处理问题时发生错误"
        )


@router.post("/stream")
async def ask_question_stream(
    request: QARequest,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    流式问答接口
    
    使用 Server-Sent Events (SSE) 流式返回回答内容。
    基于 MedicalAgent 的原生流式输出，提供真正的实时响应。
    
    **SSE 事件格式：**
    - `{"type": "tool_start", "tool_id": "...", "tool_name": "...", "arguments": {...}}` - 工具调用开始
    - `{"type": "tool_end", "tool_id": "...", "tool_name": "...", "status": "success|error", ...}` - 工具调用结束
    - `{"type": "chunk", "content": "..."}` - 回答内容块
    - `{"type": "meta", "question_id": "...", "entities": [...], ...}` - 元数据
    - `{"type": "error", "message": "..."}` - 错误信息
    - `[DONE]` - 流结束标记
    """
    qa_service = QAService(db)
    user_id = current_user.id if current_user else None
    
    async def generate():
        try:
            stream = qa_service.process_question_stream(
                question=request.question,
                user_id=user_id,
                session_id=request.session_id
            )
            
            for event in stream:
                data = json.dumps(event, ensure_ascii=False)
                yield f"data: {data}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except GeneratorExit:
            # 客户端断开连接
            logger.info("客户端断开连接，停止流式输出")
        except Exception as e:
            logger.error(f"流式问答错误: {e}", exc_info=True)
            error_data = json.dumps({"type": "error", "message": str(e)}, ensure_ascii=False)
            yield f"data: {error_data}\n\n"
            yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.get("/health")
async def qa_health():
    """
    问答服务健康检查
    
    检查 MedicalAgent 服务是否可用。
    """
    try:
        from medical_agent import MedicalAgent
        from api.core.config import settings
        
        # 尝试创建 Agent 实例（验证配置）
        agent = MedicalAgent(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
            model=settings.DEEPSEEK_MODEL
        )
        tool_count = len(agent.tool_registry)
        
        return {
            "status": "healthy",
            "service": "MedicalAgent",
            "model": agent.model,
            "tools_registered": tool_count,
            "message": "问答服务运行正常"
        }
        
    except Exception as e:
        logger.error(f"健康检查失败: {e}")
        return {
            "status": "unhealthy",
            "service": "MedicalAgent",
            "message": str(e)
        }


@router.post("/restore")
async def restore_session_context(
    session_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    恢复会话上下文
    
    从数据库加载历史对话并恢复到 Agent 的记忆中。
    用于切换历史对话时自动加载上下文。
    
    **使用场景：**
    - 用户切换到历史会话时调用
    - 确保 LLM 能看到之前的对话历史
    - 支持多轮对话的连续性
    
    **请求参数：**
    - **session_id**: 要恢复的会话 ID
    
    **响应：**
    - 恢复的对话轮数
    - 是否成功
    """
    qa_service = QAService(db)
    user_id = current_user.id if current_user else None
    
    result = qa_service.restore_session_context(
        session_id=session_id,
        user_id=user_id
    )
    
    return result


@router.post("/clear")
async def clear_session(
    session_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    清空会话对话历史
    
    清空指定会话的对话记忆，但保留 Agent 实例。
    """
    qa_service = QAService(db)
    success = qa_service.clear_session(session_id)
    
    return {
        "success": success,
        "session_id": session_id,
        "message": "对话历史已清空" if success else "会话不存在"
    }


@router.delete("/session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: User = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    删除会话
    
    删除指定会话及其 Agent 实例，释放资源。
    """
    qa_service = QAService(db)
    success = qa_service.delete_session(session_id)
    
    return {
        "success": success,
        "session_id": session_id,
        "message": "会话已删除" if success else "会话不存在"
    }
