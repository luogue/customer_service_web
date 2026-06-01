"""
上下文管理路由
- 业务上下文管理
- 会话管理
- 对话历史查询
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from knowledge_base.database import get_db
from context_management.context_manager import ContextManager
from ops_monitor import logger

router = APIRouter(prefix="/context", tags=["上下文管理"])

# 请求模型
class CreateSessionRequest(BaseModel):
    session_id: str
    user_id: Optional[int] = None

class UpdateBusinessContextRequest(BaseModel):
    session_id: str
    current_intent: Optional[str] = None
    current_step: Optional[str] = None
    current_node: Optional[str] = None
    user_phone: Optional[str] = None
    user_id: Optional[int] = None
    selected_order: Optional[str] = None
    order_list: Optional[List[Dict]] = None
    intent_params: Optional[Dict] = None
    custom_params: Optional[Dict] = None

class SaveMessageRequest(BaseModel):
    session_id: str
    role: str
    content: str
    msg_type: str = "text"

# 响应模型
class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# ============================================
# 会话管理接口
# ============================================

@router.post("/session/create", response_model=ApiResponse)
async def create_session(
    request: CreateSessionRequest,
    db: Session = Depends(get_db)
):
    """创建新会话"""
    try:
        context_manager = ContextManager(db)
        session = context_manager.create_session(request.session_id, request.user_id)
        
        return ApiResponse(
            success=True,
            message="会话创建成功",
            data={
                "session_id": session.session_id,
                "started_at": session.started_at.isoformat() if session.started_at else None
            }
        )
    except Exception as e:
        logger.error(f"创建会话失败: {e}")
        return ApiResponse(
            success=False,
            message=f"创建会话失败: {str(e)}"
        )

@router.get("/session/{session_id}", response_model=ApiResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取会话信息"""
    try:
        context_manager = ContextManager(db)
        session = context_manager.get_session(session_id)
        
        if not session:
            return ApiResponse(
                success=False,
                message="会话不存在"
            )
        
        return ApiResponse(
            success=True,
            message="获取会话成功",
            data={
                "session_id": session.session_id,
                "user_id": session.user_id,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "is_active": session.is_active
            }
        )
    except Exception as e:
        logger.error(f"获取会话失败: {e}")
        return ApiResponse(
            success=False,
            message=f"获取会话失败: {str(e)}"
        )

@router.post("/session/{session_id}/end", response_model=ApiResponse)
async def end_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """结束会话（不清理数据，按法规留存）"""
    try:
        context_manager = ContextManager(db)
        session = context_manager.end_session(session_id)
        
        if not session:
            return ApiResponse(
                success=False,
                message="会话不存在"
            )
        
        return ApiResponse(
            success=True,
            message="会话结束成功"
        )
    except Exception as e:
        logger.error(f"结束会话失败: {e}")
        return ApiResponse(
            success=False,
            message=f"结束会话失败: {str(e)}"
        )

# ============================================
# 业务上下文管理接口
# ============================================

@router.get("/business/{session_id}", response_model=ApiResponse)
async def get_business_context(
    session_id: str,
    db: Session = Depends(get_db)
):
    """获取业务上下文"""
    try:
        context_manager = ContextManager(db)
        context = context_manager.get_context_dict(session_id)
        
        return ApiResponse(
            success=True,
            message="获取业务上下文成功",
            data=context
        )
    except Exception as e:
        logger.error(f"获取业务上下文失败: {e}")
        return ApiResponse(
            success=False,
            message=f"获取业务上下文失败: {str(e)}"
        )

@router.post("/business/update", response_model=ApiResponse)
async def update_business_context(
    request: UpdateBusinessContextRequest,
    db: Session = Depends(get_db)
):
    """更新业务上下文"""
    try:
        context_manager = ContextManager(db)
        context = context_manager.create_or_update_business_context(
            session_id=request.session_id,
            current_intent=request.current_intent,
            current_step=request.current_step,
            current_node=request.current_node,
            user_phone=request.user_phone,
            user_id=request.user_id,
            selected_order=request.selected_order,
            order_list=request.order_list,
            intent_params=request.intent_params,
            custom_params=request.custom_params
        )
        
        return ApiResponse(
            success=True,
            message="更新业务上下文成功",
            data=context_manager.get_context_dict(request.session_id)
        )
    except Exception as e:
        logger.error(f"更新业务上下文失败: {e}")
        return ApiResponse(
            success=False,
            message=f"更新业务上下文失败: {str(e)}"
        )

@router.post("/business/{session_id}/clear", response_model=ApiResponse)
async def clear_business_context(
    session_id: str,
    db: Session = Depends(get_db)
):
    """清空业务上下文（保留对话记录）"""
    try:
        context_manager = ContextManager(db)
        context_manager.clear_business_context(session_id)
        
        return ApiResponse(
            success=True,
            message="清空业务上下文成功"
        )
    except Exception as e:
        logger.error(f"清空业务上下文失败: {e}")
        return ApiResponse(
            success=False,
            message=f"清空业务上下文失败: {str(e)}"
        )

# ============================================
# 对话历史管理接口
# ============================================

@router.post("/message/save", response_model=ApiResponse)
async def save_message(
    request: SaveMessageRequest,
    db: Session = Depends(get_db)
):
    """保存消息（留痕合规）"""
    try:
        context_manager = ContextManager(db)
        message = context_manager.save_message(
            session_id=request.session_id,
            role=request.role,
            content=request.content,
            msg_type=request.msg_type
        )
        
        return ApiResponse(
            success=True,
            message="保存消息成功",
            data={
                "id": message.id,
                "session_id": message.session_id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at.isoformat() if message.created_at else None
            }
        )
    except Exception as e:
        logger.error(f"保存消息失败: {e}")
        return ApiResponse(
            success=False,
            message=f"保存消息失败: {str(e)}"
        )

@router.get("/messages/{session_id}", response_model=ApiResponse)
async def get_messages(
    session_id: str,
    limit: Optional[int] = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """获取会话消息列表"""
    try:
        context_manager = ContextManager(db)
        messages = context_manager.get_messages(session_id, limit=limit, offset=offset)
        
        result = []
        for msg in messages:
            result.append({
                "id": msg.id,
                "role": msg.role,
                "content": msg.content,
                "type": msg.type,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        return ApiResponse(
            success=True,
            message="获取消息列表成功",
            data={
                "session_id": session_id,
                "messages": result,
                "total": len(result)
            }
        )
    except Exception as e:
        logger.error(f"获取消息列表失败: {e}")
        return ApiResponse(
            success=False,
            message=f"获取消息列表失败: {str(e)}"
        )

@router.get("/messages/{session_id}/recent", response_model=ApiResponse)
async def get_recent_messages(
    session_id: str,
    count: int = 10,
    db: Session = Depends(get_db)
):
    """获取最近N轮对话（用于大模型Prompt）"""
    try:
        context_manager = ContextManager(db)
        messages = context_manager.get_recent_messages(session_id, count=count)
        
        return ApiResponse(
            success=True,
            message="获取最近对话成功",
            data={
                "session_id": session_id,
                "messages": messages,
                "turn_count": count
            }
        )
    except Exception as e:
        logger.error(f"获取最近对话失败: {e}")
        return ApiResponse(
            success=False,
            message=f"获取最近对话失败: {str(e)}"
        )

@router.get("/prompt/{session_id}", response_model=ApiResponse)
async def build_prompt_context(
    session_id: str,
    max_recent_turns: int = 10,
    db: Session = Depends(get_db)
):
    """构建大模型Prompt上下文（业务上下文 + 最近对话）"""
    try:
        context_manager = ContextManager(db)
        prompt_context = context_manager.build_prompt_context(
            session_id, 
            max_recent_turns=max_recent_turns
        )
        
        return ApiResponse(
            success=True,
            message="构建Prompt成功",
            data={
                "session_id": session_id,
                "prompt_context": prompt_context
            }
        )
    except Exception as e:
        logger.error(f"构建Prompt失败: {e}")
        return ApiResponse(
            success=False,
            message=f"构建Prompt失败: {str(e)}"
        )
