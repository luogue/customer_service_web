"""
订单查询处理器
独立模块 - 负责订单查询相关逻辑
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from knowledge_base.order_service import OrderService
from knowledge_base.models import OrderStatus
from datetime import datetime

logger = logging.getLogger(__name__)


class OrderQueryHandler:
    """订单查询处理器"""
    
    def __init__(self, db: Session = None):
        self.db = db
        self.order_service = OrderService(db) if db else None
    
    def query_orders(self, phone: str, page: int = 1, page_size: int = 5) -> Dict[str, Any]:
        """
        查询订单列表
        
        Args:
            phone: 用户手机号
            page: 页码
            page_size: 每页数量
            
        Returns:
            {
                "success": bool,
                "orders": List[Dict],
                "total": int,
                "page": int,
                "has_more": bool,
                "message": str
            }
        """
        try:
            if self.order_service:
                orders = self.order_service.get_orders_by_phone(
                    phone, 
                    limit=page_size, 
                    offset=(page-1)*page_size
                )
                total_count = self.order_service.get_total_orders_count(phone)
            else:
                orders = []
                total_count = 0
            
            has_more = total_count > page * page_size
            
            return {
                "success": True,
                "orders": orders,
                "total": total_count,
                "page": page,
                "has_more": has_more,
                "message": f"找到您的订单（第{page}页，共{total_count}个）" if orders else "未查询到订单"
            }
        except Exception as e:
            logger.error(f"查询订单失败: {e}")
            return {
                "success": False,
                "orders": [],
                "total": 0,
                "page": page,
                "has_more": False,
                "message": "查询订单时出现错误，请稍后再试。"
            }
    
    def get_order_detail(self, order: Dict) -> str:
        """
        获取订单详细信息
        
        Args:
            order: 订单数据字典
            
        Returns:
            格式化的订单详情字符串
        """
        return f"订单详情：\n商品：{order['product_name']}\n订单号：{order['order_number']}\n金额：¥{order['total_amount']}\n状态：{order['status_text']}\n下单时间：{order['created_at']}\n{order.get('logistics_info', '')}"
    
    def format_order_list(self, orders: List[Dict]) -> str:
        """
        格式化订单列表
        
        Args:
            orders: 订单列表
            
        Returns:
            格式化的订单列表字符串
        """
        return "\n".join([
            f"{i+1}. {order['product_name']} - {order['order_number']} - {order['status_text']}"
            for i, order in enumerate(orders)
        ])
    
    def select_order_by_index(self, orders: List[Dict], index: int) -> Optional[Dict]:
        """
        根据索引选择订单
        
        Args:
            orders: 订单列表
            index: 用户输入的索引（1-based）
            
        Returns:
            选中的订单或None
        """
        if 0 < index <= len(orders):
            return orders[index - 1]
        return None
    
    def get_orders_by_status(self, phone: str, statuses: List[str], page: int = 1, page_size: int = 5) -> Dict[str, Any]:
        """
        根据状态查询订单
        
        Args:
            phone: 用户手机号
            statuses: 订单状态列表
            page: 页码
            page_size: 每页数量
            
        Returns:
            查询结果
        """
        try:
            if self.order_service:
                all_orders = self.order_service.get_orders_by_phone(phone, limit=100)
                filtered_orders = [
                    order for order in all_orders 
                    if order.get('status') in statuses
                ]
                total_count = len(filtered_orders)
                
                start_idx = (page - 1) * page_size
                end_idx = start_idx + page_size
                orders = filtered_orders[start_idx:end_idx]
                
                has_more = total_count > page * page_size
                
                return {
                    "success": True,
                    "orders": orders,
                    "total": total_count,
                    "page": page,
                    "has_more": has_more,
                    "message": f"找到符合条件的订单（第{page}页，共{total_count}个）" if orders else "未查询到符合条件的订单"
                }
            else:
                return {
                    "success": False,
                    "orders": [],
                    "total": 0,
                    "page": page,
                    "has_more": False,
                    "message": "订单服务不可用"
                }
        except Exception as e:
            logger.error(f"根据状态查询订单失败: {e}")
            return {
                "success": False,
                "orders": [],
                "total": 0,
                "page": page,
                "has_more": False,
                "message": "查询订单时出现错误"
            }
    
    def check_order_time_limit(self, order: Dict, days: int = 7) -> bool:
        """
        检查订单是否在时间限制内
        
        Args:
            order: 订单数据
            days: 天数限制
            
        Returns:
            是否在时间限制内
        """
        delivered_time_str = order.get('updated_at', '')
        if not delivered_time_str:
            return True
        
        try:
            if isinstance(delivered_time_str, str):
                delivered_time = datetime.fromisoformat(delivered_time_str.replace('Z', '+00:00'))
            else:
                delivered_time = delivered_time_str
            
            days_since_delivered = (datetime.now() - delivered_time.replace(tzinfo=None)).days
            return days_since_delivered <= days
        except Exception as e:
            logger.error(f"解析时间失败: {e}")
            return True


# 全局实例
_order_query_handler_instance: Optional[OrderQueryHandler] = None


def get_order_query_handler(db: Session = None) -> OrderQueryHandler:
    """获取订单查询处理器实例"""
    global _order_query_handler_instance
    if _order_query_handler_instance is None:
        _order_query_handler_instance = OrderQueryHandler(db)
    elif db:
        _order_query_handler_instance.db = db
        _order_query_handler_instance.order_service = OrderService(db) if db else None
    return _order_query_handler_instance
