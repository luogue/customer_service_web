"""
智能客服对话路由
实现五层调用顺序：
接入层 → 对话引擎层 → 大模型交互层 → 知识底座层 → 运维保障层
"""
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session
import json
import asyncio

# 直接导入 logger.py 文件中的 logger 实例
from ops_monitor.logger import logger

from knowledge_base.models import get_db
from dialogue_engine.order_dialogue import get_order_dialogue_flow
from llm_adapter.stream_generator import stream_generator
from context_management.context_manager import get_context_manager
from ops_monitor.monitor_decorator import monitor_api
from tracing.trace_manager import get_trace_manager

router = APIRouter(tags=["智能客服对话"])

class ChatMessageRequest(BaseModel):
    """聊天消息请求"""
    message: str
    session_id: str = "default"
    user_id: Optional[str] = None
    phone: Optional[str] = None

class ChatEndRequest(BaseModel):
    """结束会话请求"""
    session_id: str
    user_id: Optional[str] = None

class ChatMessageResponse(BaseModel):
    """聊天消息响应"""
    success: bool
    message: str
    intent: Optional[dict] = None
    data: Optional[dict] = None

# 存储会话状态
session_states = {}

# 导入指标统计模块
from knowledge_base.metrics import generate_request_id, record_metrics
from datetime import datetime

async def dialogue_sse_generator(user_id: str, phone: str, message: str, 
                                 session_id: str, db: Session, request: Request = None):
    """
    SSE生成器 - 集成五层调用流程
    首问语由前端处理，后端只处理业务逻辑
    """
    # 记录开始时间和生成请求ID
    start_time = datetime.now()
    request_id = generate_request_id()
    
    # 初始化指标变量
    ai_intent = None
    is_correct = False
    is_completed = False
    is_context_used = False
    is_transferred = False
    
    try:
        # 获取trace对象
        trace = None
        if request and hasattr(request, "state"):
            trace = getattr(request.state, "trace", None)
        
        # 添加对话处理span
        dialogue_span = None
        if trace:
            dialogue_span = trace.add_span("dialogue_engine", "process_input")
            dialogue_span.attributes["user_id"] = user_id or "u001"
            dialogue_span.attributes["session_id"] = session_id
            dialogue_span.attributes["message"] = message
        
        # 获取或创建对话流程实例
        flow_span = None
        if trace:
            flow_span = trace.add_span("dialogue_engine", "get_flow")
        
        logger.info(f"获取对话流程实例")
        dialogue_flow = get_order_dialogue_flow(db)
        
        if flow_span:
            flow_span.finish("success")
        
        # 初始化会话状态（不发送首问语）
        if session_id not in session_states:
            session_states[session_id] = {
                "started": True,
                "step": "welcome",
                "intents": [],
                "current_task": 0
            }
        
        # 处理用户输入
        state = session_states[session_id]
        state["step"] = "processing"
        
        # 调用对话引擎层处理
        process_span = None
        if trace:
            process_span = trace.add_span("dialogue_engine", "process_user_input")
        
        logger.info(f"调用对话引擎处理用户输入: {message}")
        result = dialogue_flow.process_user_input(
            user_id=user_id or "u001",
            phone=phone or "13800000000",
            content=message,
            session_id=session_id,
            trace_id=trace.trace_id if trace else None
        )
        
        if process_span:
            process_span.finish("success")
            process_span.attributes["result"] = str(result)
        
        logger.info(f"对话引擎处理结果: {result}")
        
        # 第四步：流式返回结果
        responses = result.get("responses", [])
        
        # 检测是否转人工
        for response in responses:
            if "转接人工客服" in response:
                is_transferred = True
                break
        
        # 提取意图信息
        intent_result = result.get("intent", {})
        if hasattr(intent_result, "intents") and intent_result.intents:
            ai_intent = intent_result.intents[0].intent_type
        
        for i, response in enumerate(responses):
            # 逐字符流式输出
            for char in response:
                data = json.dumps({
                    "type": "message",
                    "content": char,
                    "part": i,
                    "is_end": False
                }, ensure_ascii=False)
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.02)  # 20ms延迟，模拟打字效果
            
            # 每条消息结束标记
            end_data = json.dumps({
                "type": "message",
                "content": "",
                "part": i,
                "is_end": True
            }, ensure_ascii=False)
            yield f"data: {end_data}\n\n"
            
            # 消息间隔
            if i < len(responses) - 1:
                await asyncio.sleep(0.3)
        
        # 更新会话状态
        state["step"] = "waiting_confirm"
        state["intents"] = [intent.intent_type for intent in result.get("intent", {}).intents]
        
        # 第五步：发送结束语（如果是结束对话）
        if message.lower() in ['再见', '拜拜', '结束', '谢谢']:
            goodbye_msg = dialogue_flow.get_goodbye_message()
            for char in goodbye_msg:
                data = json.dumps({
                    "type": "goodbye",
                    "content": char,
                    "is_end": False
                }, ensure_ascii=False)
                yield f"data: {data}\n\n"
                await asyncio.sleep(0.02)
            
            end_data = json.dumps({
                "type": "goodbye",
                "content": "",
                "is_end": True
            }, ensure_ascii=False)
            yield f"data: {end_data}\n\n"
            
            # 清除会话状态
            if session_id in session_states:
                del session_states[session_id]
                # 对话结束，标记为完成
                is_completed = True
    
    except Exception as e:
        logger.error(f"对话处理错误: {e}")
        error_data = json.dumps({
            "type": "error",
            "content": f"处理消息时出现错误: {str(e)}"
        }, ensure_ascii=False)
        yield f"data: {error_data}\n\n"
    
    finally:
        # 记录结束时间
        end_time = datetime.now()
        
        # 记录指标
        record_metrics(
            request_id=request_id,
            user_question=message,
            ai_intent=ai_intent,
            is_correct=is_correct,
            is_completed=is_completed,
            is_context_used=is_context_used,
            is_transferred=is_transferred,
            start_time=start_time,
            end_time=end_time
        )
        
        # 发送完成标记
        yield "data: [DONE]\n\n"

@router.get("/metrics")
async def get_chat_metrics():
    """
    获取AI客服指标统计
    
    接口地址: GET /api/chat/metrics
    返回AI客服的各项指标统计数据
    """
    from knowledge_base.metrics import calculate_metrics
    metrics = calculate_metrics()
    return {
        "success": True,
        "data": metrics,
        "message": "指标统计完成"
    }

@router.post("/metrics/reset")
async def reset_chat_metrics(db: Session = Depends(get_db)):
    """
    重置AI客服指标数据
    
    接口地址: POST /api/chat/metrics/reset
    清空所有指标统计数据
    """
    from knowledge_base.metrics import Metrics
    try:
        db.query(Metrics).delete()
        db.commit()
        return {
            "success": True,
            "message": "指标数据已重置"
        }
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"重置失败: {str(e)}"
        }

@router.post("/message")
@monitor_api(endpoint="/api/chat/message")
async def chat_message(request: ChatMessageRequest, db: Session = Depends(get_db), http_request: Request = None):
    """
    智能客服消息接口 - 集成五层调用流程
    
    接口地址: POST /api/chat/message
    
    请求体:
    {
        "message": "帮我查下订单",
        "session_id": "session_001",
        "user_id": "u001",
        "phone": "13800000000"
    }
    
    返回: SSE流式数据
    
    测试命令:
    curl -N -X POST http://localhost:8000/api/chat/message \
      -H "Content-Type: application/json" \
      -d '{"message": "帮我查下订单", "phone": "13800000000"}'
    """
    logger.info(f"智能客服请求: session_id={request.session_id}, message={request.message}")
    
    return StreamingResponse(
        dialogue_sse_generator(
            user_id=request.user_id,
            phone=request.phone,
            message=request.message,
            session_id=request.session_id,
            db=db,
            request=http_request
        ),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )

@router.post("/welcome")
@monitor_api(endpoint="/api/chat/welcome")
async def chat_welcome(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    获取首问语
    
    接口地址: POST /api/chat/welcome
    
    请求体:
    {
        "session_id": "session_001"
    }
    """
    dialogue_flow = get_order_dialogue_flow(db)
    welcome_msg = dialogue_flow.get_welcome_message()
    
    # 初始化会话状态
    session_states[request.session_id] = {
        "started": True,
        "step": "welcome",
        "intents": [],
        "current_task": 0
    }
    
    return ChatMessageResponse(
        success=True,
        message=welcome_msg,
        data={"type": "welcome"}
    )

@router.post("/end")
async def chat_end(request: ChatEndRequest, db: Session = Depends(get_db)):
    """
    结束对话
    
    接口地址: POST /api/chat/end
    
    请求体:
    {
        "session_id": "session_001"
    }
    """
    dialogue_flow = get_order_dialogue_flow(db)
    goodbye_msg = dialogue_flow.get_goodbye_message()
    
    # 清除对话流程实例中的会话状态
    if request.session_id in dialogue_flow.session_states:
        del dialogue_flow.session_states[request.session_id]
    
    # 清除上下文管理器中的业务上下文
    context_manager = get_context_manager(db)
    context_manager.clear_business_context(request.session_id)
    
    # 结束会话（更新会话状态）
    context_manager.end_session(request.session_id)
    
    return ChatMessageResponse(
        success=True,
        message=goodbye_msg,
        data={"type": "goodbye"}
    )

@router.get("/intent-examples")
async def get_intent_examples():
    """
    获取意图识别示例
    
    接口地址: GET /api/chat/intent-examples
    """
    examples = {
        "single_intent": {
            "user_id": "u001",
            "phone": "13800000000",
            "content": "帮我查下最近买的卫衣订单",
            "intents": [
                {
                    "intent_type": "query_order",
                    "priority": 1,
                    "description": "查询订单信息"
                }
            ]
        },
        "multi_intent": {
            "user_id": "u001",
            "phone": "13800000000",
            "content": "帮我查下最近买的卫衣订单，顺便看看有没有优惠券",
            "intents": [
                {
                    "intent_type": "query_order",
                    "priority": 1,
                    "description": "查询订单信息"
                },
                {
                    "intent_type": "query_promotion",
                    "priority": 2,
                    "description": "查询优惠活动"
                }
            ]
        }
    }
    
    return {
        "success": True,
        "data": examples
    }

@router.post("/validate-session")
async def validate_session(request: ChatMessageRequest, db: Session = Depends(get_db)):
    """
    验证会话是否有效
    
    接口地址: POST /api/chat/validate-session
    
    请求体:
    {
        "user_id": "u001",
        "session_id": "session_001"
    }
    """
    from dialogue_engine.session_manager import SessionManager
    
    try:
        user_id = request.user_id or "default_user"
        session_id = request.session_id
        
        # 检查会话是否过期
        is_valid = SessionManager.check_session_expiry(user_id, session_id)
        
        return {
            "success": is_valid,
            "message": "会话有效" if is_valid else "会话已过期"
        }
    except Exception as e:
        logger.error(f"验证会话失败: {e}")
        return {
            "success": False,
            "message": "验证会话时出现错误"
        }
