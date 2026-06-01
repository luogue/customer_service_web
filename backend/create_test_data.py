"""
创建测试用户和订单数据
- 用户1：13800000000，密码123456
- 用户2：13800000001，密码123456
- 为每个用户创建7个不同状态的订单
"""
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from knowledge_base.models import User, Order, OrderStatus, OrderItem
from knowledge_base.database import engine, Base
import random

def create_user(db: Session, phone: str, password: str) -> User:
    """创建用户"""
    user = User(
        phone=phone,
        created_at=datetime.now()
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def create_order(db: Session, user_id: int, status: OrderStatus, product_name: str, amount: float, days_ago: int) -> Order:
    """创建订单"""
    order = Order(
        user_id=user_id,
        order_no=f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{user_id}{random.randint(100, 999)}",
        total_amount=amount,
        status=status,
        shipping_address="测试地址",
        receiver_name="测试用户",
        receiver_phone="13800000001",
        created_at=datetime.now() - timedelta(days=days_ago),
        updated_at=datetime.now()
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # 创建订单商品记录
    order_item = OrderItem(
        order_id=order.id,
        product_id=random.randint(1, 100),
        product_name=product_name,
        quantity=1,
        price=amount
    )
    db.add(order_item)
    db.commit()
    
    return order

def create_orders_for_user(db: Session, phone: str, password: str):
    """为用户创建测试数据"""
    # 检查用户是否已存在
    existing_user = db.query(User).filter(User.phone == phone).first()
    if existing_user:
        print(f"用户{phone}已存在，ID: {existing_user.id}")
        user = existing_user
    else:
        # 创建新用户
        user = create_user(db, phone, password)
        print(f"创建用户成功: {user.phone}, ID: {user.id}")
    
    # 检查用户订单数量
    existing_orders = db.query(Order).filter(Order.user_id == user.id).count()
    if existing_orders >= 7:
        print(f"用户已有{existing_orders}个订单，无需创建")
        return
    
    # 创建7个不同状态的订单
    order_statuses = [
        (OrderStatus.PENDING, "iPhone 15 Pro Max 256GB", 9999.00),
        (OrderStatus.PAID, "MacBook Pro 14英寸 M3芯片", 14999.00),
        (OrderStatus.SHIPPED, "NVIDIA RTX 4090显卡", 12999.00),
        (OrderStatus.DELIVERED, "Sony WH-1000XM5降噪耳机", 2499.00),
        (OrderStatus.CANCELLED, "Nike Air Jordan 1篮球鞋", 1299.00),
        (OrderStatus.PAID, "Dyson V15吸尘器", 4999.00),
        (OrderStatus.SHIPPED, "小米14 Pro 12GB+256GB", 4999.00)
    ]
    
    for i, (status, product_name, amount) in enumerate(order_statuses):
        order = create_order(db, user.id, status, product_name, amount, 7-i)
        print(f"创建订单成功: {order.order_no}, 商品: {product_name}, 状态: {status.name}")
    
    print(f"\n用户{phone}订单数量: {db.query(Order).filter(Order.user_id == user.id).count()}")

def main():
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 创建数据库会话
    from knowledge_base.database import SessionLocal
    db = SessionLocal()
    
    try:
        # 为13800000000创建订单
        print("=" * 60)
        print("为用户13800000000创建测试数据")
        print("=" * 60)
        create_orders_for_user(db, "13800000000", "123456")
        
        print("\n" + "=" * 60)
        print("为用户13800000001创建测试数据")
        print("=" * 60)
        create_orders_for_user(db, "13800000001", "123456")
        
        print("\n" + "=" * 60)
        print("创建测试数据完成！")
        print("=" * 60)
        print("用户1: 13800000000, 密码: 123456")
        print("用户2: 13800000001, 密码: 123456")
        
    finally:
        db.close()

if __name__ == "__main__":
    main()
