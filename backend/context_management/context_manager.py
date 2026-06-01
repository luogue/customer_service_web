"""
上下文管理模块
- 业务上下文管理（用户意图、任务步骤、订单信息等）
- 全量对话记录管理（留痕合规）
- 会话管理
"""
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from sqlalchemy.orm import Session

from knowledge_base.models import (
    BusinessContext, ConversationSession, Message
)

logger = logging.getLogger(__name__)


class ContextManager:
    """上下文管理器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # ============================================
    # 会话管理
    # ============================================
    
    def create_session(self, session_id: str, user_id: Optional[int] = None) -> ConversationSession:
        """创建新会话"""
        session = ConversationSession(
            session_id=session_id,
            user_id=user_id,
            started_at=datetime.utcnow(),
            is_active=True
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        logger.info(f"创建会话: {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[ConversationSession]:
        """获取会话"""
        return self.db.query(ConversationSession).filter(
            ConversationSession.session_id == session_id
        ).first()
    
    def end_session(self, session_id: str) -> Optional[ConversationSession]:
        """结束会话（不自动清理，按法规留存）"""
        session = self.get_session(session_id)
        if session:
            session.is_active = False
            session.ended_at = datetime.utcnow()
            self.db.commit()
            logger.info(f"结束会话: {session_id}")
        return session
    
    # ============================================
    # 业务上下文管理
    # ============================================
    
    def get_business_context(self, session_id: str) -> Optional[BusinessContext]:
        """获取业务上下文"""
        return self.db.query(BusinessContext).filter(
            BusinessContext.session_id == session_id
        ).first()
    
    def create_or_update_business_context(
        self,
        session_id: str,
        current_intent: Optional[str] = None,
        current_step: Optional[str] = None,
        current_node: Optional[str] = None,
        user_phone: Optional[str] = None,
        user_id: Optional[int] = None,
        selected_order: Optional[str] = None,
        order_list: Optional[List[Dict]] = None,
        intent_params: Optional[Dict] = None,
        custom_params: Optional[Dict] = None
    ) -> BusinessContext:
        """创建或更新业务上下文"""
        context = self.get_business_context(session_id)
        
        if not context:
            context = BusinessContext(session_id=session_id)
            self.db.add(context)
        
        if current_intent is not None:
            context.current_intent = current_intent
        if current_step is not None:
            context.current_step = current_step
        if current_node is not None:
            context.current_node = current_node
        if user_phone is not None:
            context.user_phone = user_phone
        if user_id is not None:
            context.user_id = user_id
        if selected_order is not None:
            context.selected_order = selected_order
        if order_list is not None:
            context.order_list = json.dumps(order_list, ensure_ascii=False)
        if intent_params is not None:
            context.intent_params = json.dumps(intent_params, ensure_ascii=False)
        if custom_params is not None:
            context.custom_params = json.dumps(custom_params, ensure_ascii=False)
        
        self.db.commit()
        self.db.refresh(context)
        logger.debug(f"更新业务上下文: {session_id}")
        return context
    
    def get_context_dict(self, session_id: str) -> Dict[str, Any]:
        """获取业务上下文（字典格式）"""
        context = self.get_business_context(session_id)
        if not context:
            return {}
        
        result = {
            "session_id": context.session_id,
            "current_intent": context.current_intent,
            "current_step": context.current_step,
            "current_node": context.current_node,
            "user_phone": context.user_phone,
            "user_id": context.user_id,
            "selected_order": context.selected_order
        }
        
        if context.order_list:
            result["order_list"] = json.loads(context.order_list)
        if context.intent_params:
            result["intent_params"] = json.loads(context.intent_params)
        if context.custom_params:
            result["custom_params"] = json.loads(context.custom_params)
        
        return result
    
    # ============================================
    # 对话记录管理（留痕合规）
    # ============================================
    
    def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        msg_type: str = "text"
    ) -> Message:
        """保存单条消息（留痕）"""
        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            type=msg_type,
            created_at=datetime.utcnow()
        )
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        logger.debug(f"保存消息: {session_id}, {role}")
        return message
    
    def get_messages(
        self,
        session_id: str,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Message]:
        """获取会话消息列表"""
        query = self.db.query(Message).filter(
            Message.session_id == session_id
        ).order_by(Message.created_at)
        
        if offset:
            query = query.offset(offset)
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_recent_messages(self, session_id: str, count: int = 10) -> List[Dict[str, Any]]:
        """获取最近N轮对话（用于大模型Prompt）"""
        messages = self.get_messages(session_id, limit=count * 2)  # 获取2倍数量确保有N轮
        result = []
        
        for msg in messages:
            result.append({
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None
            })
        
        return result[-count * 2:]  # 只保留最近count*2条
    
    # ============================================
    # 大模型Prompt构建
    # ============================================
    
    def build_prompt_context(self, session_id: str, max_recent_turns: int = 10) -> str:
        """
        构建大模型Prompt上下文
        - 业务上下文 + 最近N轮对话
        - 控制Token成本
        """
        business_context = self.get_context_dict(session_id)
        recent_messages = self.get_recent_messages(session_id, max_recent_turns)
        
        # 构建业务上下文部分
        context_parts = []
        context_parts.append("【业务上下文】")
        
        if business_context.get("current_intent"):
            context_parts.append(f"- 当前意图: {business_context['current_intent']}")
        if business_context.get("current_step"):
            context_parts.append(f"- 当前步骤: {business_context['current_step']}")
        if business_context.get("user_phone"):
            context_parts.append(f"- 用户手机号: {business_context['user_phone']}")
        if business_context.get("selected_order"):
            context_parts.append(f"- 选中订单: {business_context['selected_order']}")
        
        # 构建对话历史部分
        context_parts.append("\n【对话历史（最近10轮）】")
        for msg in recent_messages:
            role_name = "用户" if msg["role"] == "user" else "AI客服"
            context_parts.append(f"{role_name}: {msg['content']}")
        
        return "\n".join(context_parts)
    
    # ============================================
    # 清理功能（按法规，不自动清理）
    # ============================================
    
    def clear_business_context(self, session_id: str) -> None:
        """清空业务上下文（保留对话记录）"""
        context = self.get_business_context(session_id)
        if context:
            context.current_intent = None
            context.current_step = None
            context.current_node = None
            context.selected_order = None
            context.order_list = None
            context.intent_params = None
            context.custom_params = None
            self.db.commit()
            logger.info(f"清空业务上下文: {session_id}")


# 全局上下文管理器实例（单例模式）
_context_manager_instance: Optional[ContextManager] = None


def get_context_manager(db: Session) -> ContextManager:
    """获取上下文管理器实例"""
    global _context_manager_instance
    if not _context_manager_instance:
        _context_manager_instance = ContextManager(db)
    return _context_manager_instance
