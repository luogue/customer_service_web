"""
投诉处理器
独立模块 - 负责投诉相关逻辑
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from .order_query_handler import OrderQueryHandler
from .transfer_human_handler import TransferHumanHandler

logger = logging.getLogger(__name__)


class ComplaintHandler:
    """投诉处理器"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.order_query_handler = OrderQueryHandler(db)
        self.transfer_handler = TransferHumanHandler(db)
    
    def get_orders_for_complaint(self, phone: str, page: int = 1, page_size: int = 5) -> Dict[str, Any]:
        """
        获取可用于投诉的订单列表
        
        Args:
            phone: 用户手机号
            page: 页码
            page_size: 每页数量
            
        Returns:
            查询结果
        """
        return self.order_query_handler.query_orders(phone, page, page_size)
    
    def submit_complaint(self, order: Optional[Dict], description: str) -> Dict[str, Any]:
        """
        提交投诉
        
        Args:
            order: 相关订单（可选）
            description: 投诉描述
            
        Returns:
            提交结果
        """
        logger.info(f"提交投诉: 订单={order}, 描述={description}")
        
        # 这里应该调用实际的投诉服务
        # 目前记录并转人工
        return {
            "success": True,
            "message": "很抱歉给您带来不好的体验，已为您记录问题并反馈。",
            "action": "transfer_human",
            "order_info": order
        }
    
    def handle_complaint_flow(self, phone: str, selected_order: Optional[Dict] = None) -> Dict[str, Any]:
        """
        处理投诉流程
        
        Args:
            phone: 用户手机号
            selected_order: 用户选择的订单（可选）
            
        Returns:
            处理结果
        """
        if selected_order:
            # 用户选择了订单
            return {
                "success": True,
                "action": "record_and_transfer",
                "message": f"您选择的订单：{selected_order['product_name']} - {selected_order['order_number']}\n\n很抱歉给您带来不好的体验，已为您记录问题并反馈。",
                "order_info": selected_order
            }
        else:
            # 用户不选择订单
            return {
                "success": True,
                "action": "record_and_transfer",
                "message": "很抱歉给您带来不好的体验，已为您记录问题并反馈。"
            }
    
    def get_complaint_prompt(self, orders: List[Dict]) -> str:
        """
        获取投诉订单选择提示
        
        Args:
            orders: 订单列表
            
        Returns:
            提示消息
        """
        order_info = self.order_query_handler.format_order_list(orders)
        return f"请选择您要投诉的订单（可选）：\n{order_info}\n\n0. 不选择订单\n\n请直接回复订单编号（1、2、3...）选择订单，回复\"0\"不选择订单，或回复\"不是\"查看下一页。"


# 全局实例
_complaint_handler_instance: Optional[ComplaintHandler] = None


def get_complaint_handler(db: Session = None) -> ComplaintHandler:
    """获取投诉处理器实例"""
    global _complaint_handler_instance
    if _complaint_handler_instance is None:
        _complaint_handler_instance = ComplaintHandler(db)
    elif db:
        _complaint_handler_instance.db = db
        _complaint_handler_instance.order_query_handler = OrderQueryHandler(db)
        _complaint_handler_instance.transfer_handler = TransferHumanHandler(db)
    return _complaint_handler_instance
