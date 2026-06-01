"""
更新第一个订单的状态为已付款（未发货）
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from knowledge_base.models import User, Order, OrderStatus
from knowledge_base.database import engine, Base, SessionLocal

def main():
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 查找用户13800000001
        user = db.query(User).filter(User.phone == "13800000001").first()
        if not user:
            print("用户13800000001不存在")
            return
        
        # 查找用户的第一个订单（按创建时间最早的）
        first_order = db.query(Order).filter(
            Order.user_id == user.id
        ).order_by(Order.created_at.asc()).first()
        
        if not first_order:
            print("用户没有订单")
            return
        
        print(f"找到第一个订单: {first_order.order_number}")
        print(f"当前状态: {first_order.status.name}")
        print(f"商品: {first_order.product_name}")
        
        # 更新状态为已付款
        first_order.status = OrderStatus.PAID
        db.commit()
        
        print(f"\n订单状态已更新为: {first_order.status.name} (已付款，未发货)")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
