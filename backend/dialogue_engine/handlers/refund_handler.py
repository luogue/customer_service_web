"""
退款处理器
独立模块 - 负责退款相关逻辑
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from knowledge_base.models import OrderStatus
from .order_query_handler import OrderQueryHandler

logger = logging.getLogger(__name__)


class RefundHandler:
    """退款处理器"""
    
    # 可退款订单状态
    REFUNDABLE_STATUSES = [
        OrderStatus.PAID.value,
        OrderStatus.SHIPPED.value,
        OrderStatus.DELIVERED.value
    ]
    
    def __init__(self, db: Session = None):
        self.db = db
        self.order_query_handler = OrderQueryHandler(db)
    
    def get_refundable_orders(self, phone: str, page: int = 1, page_size: int = 5) -> Dict[str, Any]:
        """
        获取可退款的订单列表
        
        规则：
        - 仅支持「已付款/已发货/已签收」状态的订单
        - 已签收订单需在签收后7天内
        
        Args:
            phone: 用户手机号
            page: 页码
            page_size: 每页数量
            
        Returns:
            查询结果
        """
        try:
            result = self.order_query_handler.get_orders_by_status(
                phone, 
                self.REFUNDABLE_STATUSES, 
                page=1, 
                page_size=100
            )
            
            if not result["success"]:
                return result
            
            all_orders = result["orders"]
            refundable_orders = []
            
            for order in all_orders:
                status = order.get('status', '')
                
                # 已付款/已发货状态的订单可以直接退货退款
                if status in [OrderStatus.PAID.value, OrderStatus.SHIPPED.value]:
                    refundable_orders.append(order)
                # 已签收状态的订单需要检查是否在7天内
                elif status == OrderStatus.DELIVERED.value:
                    if self.order_query_handler.check_order_time_limit(order, days=7):
                        refundable_orders.append(order)
            
            # 分页
            total_count = len(refundable_orders)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            orders = refundable_orders[start_idx:end_idx] if start_idx < total_count else []
            has_more = total_count > page * page_size
            
            return {
                "success": True,
                "orders": orders,
                "total": total_count,
                "page": page,
                "has_more": has_more,
                "message": f"找到可退货退款的订单（第{page}页，共{total_count}个）" if orders else "未查询到符合退货退款条件的订单"
            }
        except Exception as e:
            logger.error(f"获取可退款订单失败: {e}")
            return {
                "success": False,
                "orders": [],
                "total": 0,
                "page": page,
                "has_more": False,
                "message": "查询订单时出现错误"
            }
    
    def check_refund_eligibility(self, order: Dict) -> Dict[str, Any]:
        """
        检查订单是否符合退款条件
        
        Args:
            order: 订单数据
            
        Returns:
            {
                "eligible": bool,
                "reason": str
            }
        """
        status = order.get('status', '')
        
        if status not in self.REFUNDABLE_STATUSES:
            return {
                "eligible": False,
                "reason": f"订单状态为{status}，不支持退款"
            }
        
        if status == OrderStatus.DELIVERED.value:
            if not self.order_query_handler.check_order_time_limit(order, days=7):
                return {
                    "eligible": False,
                    "reason": "已签收订单超过7天，不支持退款"
                }
        
        return {
            "eligible": True,
            "reason": "符合退款条件"
        }
    
    def submit_refund_request(self, order: Dict, reason: str = "") -> Dict[str, Any]:
        """
        提交退款申请
        
        Args:
            order: 订单数据
            reason: 退款原因
            
        Returns:
            提交结果
        """
        eligibility = self.check_refund_eligibility(order)
        
        if not eligibility["eligible"]:
            return {
                "success": False,
                "message": eligibility["reason"]
            }
        
        # 这里应该调用实际的退款服务
        # 目前模拟成功
        logger.info(f"提交退款申请: 订单号={order.get('order_number')}, 原因={reason}")
        
        return {
            "success": True,
            "message": "已提交系统审核，1个工作日内处理。",
            "order_number": order.get('order_number')
        }
    
    def check_willing_to_return(self) -> str:
        """
        询问用户是否愿意退货
        
        Returns:
            提示消息
        """
        return "请问您是否愿意退货？请回复\"是\"愿意退货，回复\"不是\"不愿意退货。"
    
    def handle_return_willingness(self, is_willing: bool, phone: str) -> Dict[str, Any]:
        """
        处理用户是否愿意退货的回答
        
        Args:
            is_willing: 是否愿意退货
            phone: 用户手机号
            
        Returns:
            处理结果
        """
        if is_willing:
            # 用户愿意退货，返回可退款订单列表
            result = self.get_refundable_orders(phone)
            return {
                "success": True,
                "action": "show_orders",
                "data": result,
                "message": "请选择您要退货退款的订单："
            }
        else:
            # 用户不愿意退货（仅退款），需要转人工
            return {
                "success": True,
                "action": "transfer_human",
                "message": "仅退款申请需要人工审核，已为您转接人工客服，请稍候。"
            }


# 全局实例
_refund_handler_instance: Optional[RefundHandler] = None


def get_refund_handler(db: Session = None) -> RefundHandler:
    """获取退款处理器实例"""
    global _refund_handler_instance
    if _refund_handler_instance is None:
        _refund_handler_instance = RefundHandler(db)
    elif db:
        _refund_handler_instance.db = db
        _refund_handler_instance.order_query_handler = OrderQueryHandler(db)
    return _refund_handler_instance
