from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import random
import string

from knowledge_base.database import get_db
from knowledge_base.models import Order, OrderStatus
from api_gateway.schemas import OrderCreate, OrderResponse

router = APIRouter(prefix="/orders", tags=["订单管理"])

@router.get("/", response_model=List[OrderResponse])
async def get_orders(db: Session = Depends(get_db)):
    """获取所有订单列表"""
    return db.query(Order).all()

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int, db: Session = Depends(get_db)):
    """获取单个订单详情"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    return order

@router.post("/", response_model=OrderResponse)
async def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    """创建新订单"""
    order_number = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    db_order = Order(
        **order.model_dump(),
        order_number=order_number
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@router.put("/{order_id}/status")
async def update_order_status(order_id: int, status: OrderStatus, db: Session = Depends(get_db)):
    """更新订单状态"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    order.status = status
    db.commit()
    return {"message": "订单状态更新成功", "order": OrderResponse.model_validate(order)}

@router.delete("/{order_id}")
async def delete_order(order_id: int, db: Session = Depends(get_db)):
    """删除订单"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    db.delete(order)
    db.commit()
    return {"message": "订单删除成功"}

@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_orders(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户的所有订单"""
    return db.query(Order).filter(Order.user_id == user_id).all()
