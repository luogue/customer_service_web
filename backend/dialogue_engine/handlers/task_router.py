"""
任务路由器
独立模块 - 负责根据意图路由到不同的处理器
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from llm_adapter.intent_mock import IntentRecognitionResult
from .order_query_handler import OrderQueryHandler, get_order_query_handler
from .refund_handler import RefundHandler, get_refund_handler
from .exchange_handler import ExchangeHandler, get_exchange_handler
from .transfer_human_handler import TransferHumanHandler, get_transfer_human_handler
from .complaint_handler import ComplaintHandler, get_complaint_handler
from .modify_order_handler import ModifyOrderHandler, get_modify_order_handler

logger = logging.getLogger(__name__)


class TaskRouter:
    """任务路由器 - 根据意图路由到对应的处理器"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.order_query_handler = get_order_query_handler(db)
        self.refund_handler = get_refund_handler(db)
        self.exchange_handler = get_exchange_handler(db)
        self.transfer_handler = get_transfer_human_handler(db)
        self.complaint_handler = get_complaint_handler(db)
        self.modify_order_handler = get_modify_order_handler(db)
    
    def route_by_intent(self, intent_type: str, phone: str, session_id: str, context: Dict = None) -> Dict[str, Any]:
        """
        根据意图类型路由到对应处理器
        
        Args:
            intent_type: 意图类型
            phone: 用户手机号
            session_id: 会话ID
            context: 上下文信息
            
        Returns:
            路由结果
        """
        logger.info(f"路由意图: {intent_type}")
        
        # 意图类型到处理器的映射
        intent_handlers = {
            "query_order": self._handle_query_order,
            "refund_return": self._handle_refund,
            "exchange": self._handle_exchange,
            "modify_address": self._handle_modify,
            "complaint": self._handle_complaint,
            "query_promotion": self._handle_promotion,
            "cancel_order": self._handle_cancel_order,
            "urgent_delivery": self._handle_urgent_delivery,
            "human": self._handle_transfer_human
        }
        
        handler = intent_handlers.get(intent_type, self._handle_unknown_intent)
        return handler(phone, session_id, context or {})
    
    def _handle_query_order(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理订单查询意图"""
        result = self.order_query_handler.query_orders(phone, page=1)
        
        if result["success"] and result["orders"]:
            order_list = self.order_query_handler.format_order_list(result["orders"])
            return {
                "success": True,
                "action": "show_orders",
                "step": "waiting_order_in_list",
                "message": f"找到您的订单（第1页，共{result['total']}个）：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择订单，或回复\"不是\"查看下一页。",
                "data": result
            }
        else:
            return {
                "success": True,
                "action": "self_check",
                "step": "waiting_self_check",
                "message": "未查询到当前登录账号绑定手机号下的任何订单。\n\n请您先自查：\n1. 确认当前登录的手机号是否正确\n2. 如需查询其他手机号的订单，请切换对应账号登录后重试\n\n请问您是否已核对？回复\"是\"确认已核对，回复\"不是\"我再帮您查询。"
            }
    
    def _handle_refund(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理退款意图"""
        return {
            "success": True,
            "action": "ask_return_willingness",
            "step": "waiting_return_confirm",
            "message": self.refund_handler.check_willing_to_return()
        }
    
    def _handle_exchange(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理换货意图"""
        result = self.exchange_handler.get_exchangeable_orders(phone)
        
        if result["success"] and result["orders"]:
            order_list = self.order_query_handler.format_order_list(result["orders"])
            return {
                "success": True,
                "action": "show_orders",
                "step": "waiting_exchange_order_selection",
                "message": f"请选择您要换货的订单：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择要换货的订单，或回复\"不是\"查看下一页。",
                "data": result
            }
        else:
            return {
                "success": True,
                "action": "info",
                "step": "initial",
                "message": f"{result['message']}。\n{self.exchange_handler.get_exchange_policy()}"
            }
    
    def _handle_modify(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理修改订单意图"""
        result = self.modify_order_handler.get_modifiable_orders(phone)
        
        if result["success"] and result["orders"]:
            order_list = self.order_query_handler.format_order_list(result["orders"])
            return {
                "success": True,
                "action": "show_orders",
                "step": "waiting_modify_order_selection",
                "message": f"请选择您要修改的订单：\n{order_list}\n\n请直接回复订单编号（1、2、3...）选择要修改的订单，或回复\"不是\"查看下一页。",
                "data": result
            }
        else:
            return {
                "success": True,
                "action": "info",
                "step": "initial",
                "message": "未查询到您的订单，无法修改地址。"
            }
    
    def _handle_complaint(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理投诉意图"""
        result = self.complaint_handler.get_orders_for_complaint(phone)
        
        if result["success"] and result["orders"]:
            prompt = self.complaint_handler.get_complaint_prompt(result["orders"])
            return {
                "success": True,
                "action": "show_orders",
                "step": "waiting_complaint_order_selection",
                "message": prompt,
                "data": result
            }
        else:
            return {
                "success": True,
                "action": "transfer_human",
                "step": "completed",
                "message": "未查询到您的订单。\n\n很抱歉给您带来不好的体验，已为您记录问题并反馈。\n转接人工客服为您处理，请稍候。"
            }
    
    def _handle_promotion(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理优惠查询意图"""
        return {
            "success": True,
            "action": "info",
            "step": "initial",
            "message": "目前我们有满199减20的活动，还有新人专享优惠券可以领取哦！"
        }
    
    def _handle_cancel_order(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理取消订单意图"""
        return {
            "success": True,
            "action": "info",
            "step": "initial",
            "message": "取消订单功能正在开发中，请通过APP或网站操作，或联系人工客服。"
        }
    
    def _handle_urgent_delivery(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理催发货意图"""
        return {
            "success": True,
            "action": "info",
            "step": "initial",
            "message": "已为您催促发货，仓库会尽快处理，请耐心等待。"
        }
    
    def _handle_transfer_human(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理转人工意图"""
        result = self.transfer_handler.transfer_to_human()
        return {
            "success": True,
            "action": "transfer_human",
            "step": "completed",
            "message": result["message"]
        }
    
    def _handle_unknown_intent(self, phone: str, session_id: str, context: Dict) -> Dict[str, Any]:
        """处理未知意图"""
        return {
            "success": True,
            "action": "info",
            "step": "initial",
            "message": "抱歉，我没有理解您的意思。请问您需要什么帮助？"
        }
    
    def get_handler_for_step(self, step: str) -> Optional[Any]:
        """
        根据步骤获取对应的处理器
        
        Args:
            step: 当前步骤
            
        Returns:
            对应的处理器
        """
        step_handler_map = {
            "waiting_order_in_list": self.order_query_handler,
            "waiting_order_selection": self.order_query_handler,
            "waiting_refund_order_selection": self.refund_handler,
            "waiting_refund_confirm": self.refund_handler,
            "waiting_return_confirm": self.refund_handler,
            "waiting_exchange_order_selection": self.exchange_handler,
            "waiting_exchange_confirm": self.exchange_handler,
            "waiting_complaint_order_selection": self.complaint_handler,
            "waiting_modify_order_selection": self.modify_order_handler,
            "waiting_modify_content": self.modify_order_handler
        }
        
        return step_handler_map.get(step)


# 全局实例
_task_router_instance: Optional[TaskRouter] = None


def get_task_router(db: Session = None) -> TaskRouter:
    """获取任务路由器实例"""
    global _task_router_instance
    if _task_router_instance is None:
        _task_router_instance = TaskRouter(db)
    elif db:
        _task_router_instance.db = db
        _task_router_instance.order_query_handler = get_order_query_handler(db)
        _task_router_instance.refund_handler = get_refund_handler(db)
        _task_router_instance.exchange_handler = get_exchange_handler(db)
        _task_router_instance.transfer_handler = get_transfer_human_handler(db)
        _task_router_instance.complaint_handler = get_complaint_handler(db)
        _task_router_instance.modify_order_handler = get_modify_order_handler(db)
    return _task_router_instance
