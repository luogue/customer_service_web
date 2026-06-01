"""
订单查询服务
提供订单相关的数据库操作
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta

from knowledge_base.models import Order, OrderStatus, User, OrderItem

class OrderService:
    """订单服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_orders_by_phone(self, phone: str, limit: int = 5, offset: int = 0) -> List[Dict]:
        """
        根据手机号查询订单
        
        Args:
            phone: 用户手机号
            limit: 返回订单数量限制
            offset: 跳过前offset个订单
            
        Returns:
            订单列表
        """
        # 先查询用户
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            return []
        
        # 查询用户的订单
        orders = self.db.query(Order).filter(
            Order.user_id == user.id
        ).order_by(desc(Order.created_at)).offset(offset).limit(limit).all()
        
        return [self._format_order(order) for order in orders]
    
    def get_total_orders_count(self, phone: str) -> int:
        """
        获取用户订单总数
        
        Args:
            phone: 用户手机号
            
        Returns:
            订单总数
        """
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            return 0
        
        return self.db.query(Order).filter(Order.user_id == user.id).count()
    
    def get_order_by_number(self, order_number: str) -> Optional[Dict]:
        """
        根据订单号查询订单
        
        Args:
            order_number: 订单号
            
        Returns:
            订单信息
        """
        order = self.db.query(Order).filter(
            Order.order_number == order_number
        ).first()
        
        if not order:
            return None
        
        return self._format_order(order)
    
    def get_recent_orders(self, phone: str, days: int = 30) -> List[Dict]:
        """
        查询最近一段时间的订单
        
        Args:
            phone: 用户手机号
            days: 最近多少天
            
        Returns:
            订单列表
        """
        user = self.db.query(User).filter(User.phone == phone).first()
        if not user:
            return []
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        orders = self.db.query(Order).filter(
            Order.user_id == user.id,
            Order.created_at >= start_date
        ).order_by(desc(Order.created_at)).all()
        
        return [self._format_order(order) for order in orders]
    
    def _format_order(self, order: Order) -> Dict:
        """格式化订单信息"""
        status_map = {
            OrderStatus.PENDING: "待付款",
            OrderStatus.PAID: "已付款",
            OrderStatus.SHIPPED: "已发货",
            OrderStatus.DELIVERED: "已签收",
            OrderStatus.CANCELLED: "已取消"
        }
        
        # 从订单商品表中获取商品名称
        order_item = self.db.query(OrderItem).filter(OrderItem.order_id == order.id).first()
        product_name = order_item.product_name if order_item else "未知商品"
        
        return {
            "id": order.id,
            "order_number": order.order_no,
            "product_name": product_name,
            "total_amount": order.total_amount,
            "status": order.status.value,
            "status_text": status_map.get(order.status, "未知状态"),
            "created_at": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": order.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_order_response(self, orders: List[Dict], page: int = 1, total_count: int = 0) -> str:
        """
        生成订单查询回复（Mock 数据）
        
        Args:
            orders: 订单列表
            page: 当前页码
            total_count: 订单总数
            
        Returns:
            自然语言回复
        """
        if not orders:
            if page > 1:
                return "没有更多订单了。"
            return "抱歉，没有找到您手机号下的订单。请问是这个手机号下的订单吗？"
        
        if len(orders) == 1:
            order = orders[0]
            return f"您的订单（{order['product_name']} - {order['order_number']}）目前{order['status_text']}，请您耐心等待。"
        
        # 多个订单
        start_num = (page - 1) * 5 + 1
        order_info = "\n".join([
            f"{i+1}. {order['product_name']} - {order['order_number']} - {order['status_text']}"
            for i, order in enumerate(orders)
        ])
        
        has_more = total_count > page * 5
        
        response = f"找到您的订单（第{page}页，共{total_count}个）：\n{order_info}\n\n您要找的订单在上面列表中吗？请回复：\n• 是 - 确认在列表中，然后回复订单编号（1、2、3...）选择具体订单\n• 不是 - 查看下一页订单"
        
        return response

# 快捷函数
def get_order_service(db: Session) -> OrderService:
    """获取订单服务实例"""
    return OrderService(db)
