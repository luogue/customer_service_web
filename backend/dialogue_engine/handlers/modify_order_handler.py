"""
修改订单处理器
独立模块 - 负责修改订单相关逻辑（地址、备注、电话等）
"""
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from knowledge_base.models import OrderStatus
from .order_query_handler import OrderQueryHandler

logger = logging.getLogger(__name__)


class ModifyOrderHandler:
    """修改订单处理器"""
    
    # 可修改订单状态（未发货）
    MODIFIABLE_STATUSES = [
        OrderStatus.PENDING.value,
        OrderStatus.PAID.value
    ]
    
    def __init__(self, db: Session = None):
        self.db = db
        self.order_query_handler = OrderQueryHandler(db)
    
    def get_modifiable_orders(self, phone: str, page: int = 1, page_size: int = 5) -> Dict[str, Any]:
        """
        获取可修改的订单列表
        
        规则：
        - 仅支持「待付款/已付款」状态的订单（未发货）
        
        Args:
            phone: 用户手机号
            page: 页码
            page_size: 每页数量
            
        Returns:
            查询结果
        """
        return self.order_query_handler.get_orders_by_status(
            phone, 
            self.MODIFIABLE_STATUSES, 
            page, 
            page_size
        )
    
    def check_modifiable(self, order: Dict) -> Dict[str, Any]:
        """
        检查订单是否可修改
        
        Args:
            order: 订单数据
            
        Returns:
            {
                "modifiable": bool,
                "reason": str
            }
        """
        status = order.get('status', '')
        
        if status not in self.MODIFIABLE_STATUSES:
            return {
                "modifiable": False,
                "reason": f"订单状态为{status}，已发货无法修改"
            }
        
        return {
            "modifiable": True,
            "reason": "可以修改"
        }
    
    def modify_order(self, order: Dict, modify_type: str, new_value: str) -> Dict[str, Any]:
        """
        修改订单信息
        
        Args:
            order: 订单数据
            modify_type: 修改类型（address/remark/phone）
            new_value: 新值
            
        Returns:
            修改结果
        """
        modifiable = self.check_modifiable(order)
        
        if not modifiable["modifiable"]:
            return {
                "success": False,
                "message": modifiable["reason"]
            }
        
        # 这里应该调用实际的订单修改服务
        # 目前模拟成功
        logger.info(f"修改订单: 订单号={order.get('order_number')}, 类型={modify_type}, 新值={new_value}")
        
        modify_type_text = {
            "address": "地址",
            "remark": "备注",
            "phone": "电话"
        }.get(modify_type, modify_type)
        
        return {
            "success": True,
            "message": f"订单修改成功！\n订单：{order.get('product_name')}\n修改内容：{modify_type_text} - {new_value}\n\n后台已更新您的订单信息。",
            "order_number": order.get('order_number'),
            "modify_type": modify_type,
            "new_value": new_value
        }
    
    def parse_modify_type(self, user_input: str) -> str:
        """
        解析用户输入的修改类型
        
        Args:
            user_input: 用户输入
            
        Returns:
            修改类型（address/remark/phone/unknown）
        """
        input_lower = user_input.lower()
        
        if any(keyword in input_lower for keyword in ["地址", "收货地址", "送货地址"]):
            return "address"
        elif any(keyword in input_lower for keyword in ["备注", "留言", "说明"]):
            return "remark"
        elif any(keyword in input_lower for keyword in ["电话", "手机号", "联系方式"]):
            return "phone"
        else:
            # 默认当作新地址处理
            return "address"
    
    def get_modify_prompt(self, order: Dict) -> str:
        """
        获取修改提示消息
        
        Args:
            order: 订单数据
            
        Returns:
            提示消息
        """
        return f"您选择的订单：{order['product_name']} - {order['order_number']}\n\n请回复您要修改的内容（地址/备注/电话），或直接发送新的信息。"


# 全局实例
_modify_order_handler_instance: Optional[ModifyOrderHandler] = None


def get_modify_order_handler(db: Session = None) -> ModifyOrderHandler:
    """获取修改订单处理器实例"""
    global _modify_order_handler_instance
    if _modify_order_handler_instance is None:
        _modify_order_handler_instance = ModifyOrderHandler(db)
    elif db:
        _modify_order_handler_instance.db = db
        _modify_order_handler_instance.order_query_handler = OrderQueryHandler(db)
    return _modify_order_handler_instance
