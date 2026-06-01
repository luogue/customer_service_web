"""
换货处理器
独立模块 - 负责换货相关逻辑
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from knowledge_base.models import OrderStatus
from .order_query_handler import OrderQueryHandler

logger = logging.getLogger(__name__)


class ExchangeHandler:
    """换货处理器"""
    
    # 可换货订单状态
    EXCHANGEABLE_STATUSES = [
        OrderStatus.PAID.value,
        OrderStatus.SHIPPED.value,
        OrderStatus.DELIVERED.value
    ]
    
    def __init__(self, db: Session = None):
        self.db = db
        self.order_query_handler = OrderQueryHandler(db)
    
    def get_exchangeable_orders(self, phone: str, page: int = 1, page_size: int = 5) -> Dict[str, Any]:
        """
        获取可换货的订单列表
        
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
                self.EXCHANGEABLE_STATUSES, 
                page=1, 
                page_size=100
            )
            
            if not result["success"]:
                return result
            
            all_orders = result["orders"]
            exchangeable_orders = []
            
            for order in all_orders:
                status = order.get('status', '')
                
                # 已付款/已发货状态的订单可以直接换货
                if status in [OrderStatus.PAID.value, OrderStatus.SHIPPED.value]:
                    exchangeable_orders.append(order)
                # 已签收状态的订单需要检查是否在7天内
                elif status == OrderStatus.DELIVERED.value:
                    if self.order_query_handler.check_order_time_limit(order, days=7):
                        exchangeable_orders.append(order)
            
            # 分页
            total_count = len(exchangeable_orders)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            orders = exchangeable_orders[start_idx:end_idx] if start_idx < total_count else []
            has_more = total_count > page * page_size
            
            return {
                "success": True,
                "orders": orders,
                "total": total_count,
                "page": page,
                "has_more": has_more,
                "message": f"找到可换货的订单（第{page}页，共{total_count}个）" if orders else "未查询到符合换货条件的订单"
            }
        except Exception as e:
            logger.error(f"获取可换货订单失败: {e}")
            return {
                "success": False,
                "orders": [],
                "total": 0,
                "page": page,
                "has_more": False,
                "message": "查询订单时出现错误"
            }
    
    def check_exchange_eligibility(self, order: Dict) -> Dict[str, Any]:
        """
        检查订单是否符合换货条件
        
        Args:
            order: 订单数据
            
        Returns:
            {
                "eligible": bool,
                "reason": str
            }
        """
        status = order.get('status', '')
        
        if status not in self.EXCHANGEABLE_STATUSES:
            return {
                "eligible": False,
                "reason": f"订单状态为{status}，不支持换货"
            }
        
        if status == OrderStatus.DELIVERED.value:
            if not self.order_query_handler.check_order_time_limit(order, days=7):
                return {
                    "eligible": False,
                    "reason": "已签收订单超过7天，不支持换货"
                }
        
        return {
            "eligible": True,
            "reason": "符合换货条件"
        }
    
    def submit_exchange_request(self, order: Dict, reason: str = "") -> Dict[str, Any]:
        """
        提交换货申请
        
        Args:
            order: 订单数据
            reason: 换货原因
            
        Returns:
            提交结果
        """
        eligibility = self.check_exchange_eligibility(order)
        
        if not eligibility["eligible"]:
            return {
                "success": False,
                "message": eligibility["reason"]
            }
        
        # 这里应该调用实际的换货服务
        # 目前模拟成功
        logger.info(f"提交换货申请: 订单号={order.get('order_number')}, 原因={reason}")
        
        return {
            "success": True,
            "message": "已为您提交换货申请，系统审核后将在1个工作日内告知您换货地址及流程。",
            "order_number": order.get('order_number')
        }
    
    def get_exchange_policy(self) -> str:
        """
        获取换货政策说明
        
        Returns:
            换货政策文本
        """
        return "换货仅支持「已付款/已发货/已签收」状态的订单，且已签收订单需在签收后7天内申请。"


# 全局实例
_exchange_handler_instance: Optional[ExchangeHandler] = None


def get_exchange_handler(db: Session = None) -> ExchangeHandler:
    """获取换货处理器实例"""
    global _exchange_handler_instance
    if _exchange_handler_instance is None:
        _exchange_handler_instance = ExchangeHandler(db)
    elif db:
        _exchange_handler_instance.db = db
        _exchange_handler_instance.order_query_handler = OrderQueryHandler(db)
    return _exchange_handler_instance
