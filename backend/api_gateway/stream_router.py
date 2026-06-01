from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json

from llm_adapter.stream_generator import stream_generator
from ops_monitor import logger

router = APIRouter(prefix="/stream", tags=["SSE流式输出"])

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

async def sse_generator(message: str = ""):
    """
    SSE生成器
    将生成器的输出包装为SSE格式
    """
    try:
        async for chunk in stream_generator.generate_stream(message):
            # SSE格式：data: {...}\n\n
            data = json.dumps({"content": chunk}, ensure_ascii=False)
            yield f"data: {data}\n\n"
            
    except Exception as e:
        logger.error(f"SSE生成错误: {e}")
        error_data = json.dumps({"error": str(e)}, ensure_ascii=False)
        yield f"data: {error_data}\n\n"
    
    finally:
        # 发送结束标记
        yield "data: [DONE]\n\n"

@router.post("/chat")
async def stream_chat(request: ChatRequest):
    """
    SSE流式聊天接口
    
    接口地址: POST /api/stream/chat
    
    请求体:
    {
        "message": "用户消息",
        "session_id": "会话ID"
    }
    
    返回: text/event-stream 格式的流式数据
    
    测试命令:
    curl -N -X POST http://localhost:8000/api/stream/chat \\
      -H "Content-Type: application/json" \\
      -d '{"message": "你好"}'
    """
    logger.info(f"SSE流式请求: session_id={request.session_id}, message={request.message}")
    
    return StreamingResponse(
        sse_generator(request.message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
        }
    )

@router.get("/chat")
async def stream_chat_get(request: Request, message: str = "", session_id: str = "default"):
    """
    SSE流式聊天接口 (GET方式，方便测试)
    
    接口地址: GET /api/stream/chat?message=你好&session_id=test
    
    测试命令:
    curl -N "http://localhost:8000/api/stream/chat?message=你好"
    """
    logger.info(f"SSE流式请求(GET): session_id={session_id}, message={message}")
    
    return StreamingResponse(
        sse_generator(message),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.get("/test")
async def stream_test():
    """
    SSE测试接口 - 简单的流式输出测试
    
    接口地址: GET /api/stream/test
    
    测试命令:
    curl -N http://localhost:8000/api/stream/test
    """
    logger.info("SSE测试请求")
    
    return StreamingResponse(
        sse_generator("测试消息"),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )
