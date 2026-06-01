"""
创建测试用户和订单数据
- 新增用户：13800000001，密码123456
- 为用户创建7个不同状态的订单
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from knowledge_base.models import User, Order, OrderStatus
from knowledge_base.database import engine, Base
def create_user(db: Session, phone: str, password: str) -> User:
    """创建用户"""
    # 简单密码哈希（仅用于测试）
    hashed_password = password  # 明文存储，仅用于测试
    user = User(
        phone=phone,
        password=hashed_password,
        is_active=True,
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

import random

def create_order(db: Session, user_id: int, status: OrderStatus, product_name: str, amount: float, status_index: int) -> Order:
    """创建订单"""
    order = Order(
        user_id=user_id,
        order_number=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}{random.randint(100, 999)}",
        product_name=product_name,
        total_amount=amount,
        status=status,
        created_at=datetime.now() - timedelta(days=7 - status_index),
        updated_at=datetime.now()
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order

def main():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    from knowledge_base.database import SessionLocal
    db = SessionLocal()
    
    try:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.phone == "13800000001").first()
        if existing_user:
            print("用户13800000001已存在")
            user = existing_user
        else:
            # 创建新用户
            user = create_user(db, "13800000001", "123456")
            print(f"创建用户成功: {user.phone}, ID: {user.id}")
        
        # 检查用户订单数量
        existing_orders = db.query(Order).filter(Order.user_id == user.id).count()
        if existing_orders >= 7:
            print(f"用户已有{existing_orders}个订单，无需创建")
            return
        
        # 创建7个不同状态的订单 - 使用真实商品名称
        order_statuses = [
            (OrderStatus.PAID, "iPhone 15 Pro Max 256GB", 9999.00),  # 第一个订单改为已付款（未发货）
            (OrderStatus.PAID, "MacBook Pro 14英寸 M3芯片", 14999.00),
            (OrderStatus.SHIPPED, "NVIDIA RTX 4090显卡", 12999.00),
            (OrderStatus.DELIVERED, "Sony WH-1000XM5降噪耳机", 2499.00),
            (OrderStatus.CANCELLED, "Nike Air Jordan 1篮球鞋", 1299.00),
            (OrderStatus.REFUNDING, "Dyson V15吸尘器", 4999.00),
            (OrderStatus.REFUNDED, "小米14 Pro 12GB+256GB", 4999.00)
        ]
        
        for i, (status, product_name, amount) in enumerate(order_statuses):
            order = create_order(db, user.id, status, product_name, amount, i+1)
            print(f"创建订单成功: {order.order_number}, 状态: {status.name}, 金额: {amount}")
        
        print("\n创建测试数据完成！")
        print(f"用户: 13800000001")
        print(f"密码: 123456")
        print(f"订单数量: {db.query(Order).filter(Order.user_id == user.id).count()}")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
