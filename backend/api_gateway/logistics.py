from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from knowledge_base.database import get_db
from knowledge_base.models import Logistics, Order, OrderStatus
from api_gateway.schemas import LogisticsUpdate, LogisticsResponse

router = APIRouter(prefix="/logistics", tags=["物流管理"])

@router.get("/", response_model=List[LogisticsResponse])
async def get_logistics(db: Session = Depends(get_db)):
    """获取所有物流信息列表"""
    return db.query(Logistics).all()

@router.get("/{logistics_id}", response_model=LogisticsResponse)
async def get_logistics_by_id(logistics_id: int, db: Session = Depends(get_db)):
    """获取单个物流详情"""
    logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    return logistics

@router.post("/order/{order_id}", response_model=LogisticsResponse)
async def create_logistics(order_id: int, logistics: LogisticsUpdate, db: Session = Depends(get_db)):
    """为订单创建物流信息"""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    db_logistics = Logistics(order_id=order_id, **logistics.model_dump())
    db.add(db_logistics)
    order.status = OrderStatus.SHIPPED
    db.commit()
    db.refresh(db_logistics)
    return db_logistics

@router.put("/{logistics_id}")
async def update_logistics(logistics_id: int, logistics: LogisticsUpdate, db: Session = Depends(get_db)):
    """更新物流信息"""
    db_logistics = db.query(Logistics).filter(Logistics.id == logistics_id).first()
    if not db_logistics:
        raise HTTPException(status_code=404, detail="物流信息不存在")
    for key, value in logistics.model_dump().items():
        setattr(db_logistics, key, value)
    db.commit()
    return {"message": "物流信息更新成功", "logistics": LogisticsResponse.model_validate(db_logistics)}

@router.get("/order/{order_id}/info", response_model=LogisticsResponse)
async def get_order_logistics(order_id: int, db: Session = Depends(get_db)):
    """获取指定订单的物流信息"""
    logistics = db.query(Logistics).filter(Logistics.order_id == order_id).first()
    if not logistics:
        raise HTTPException(status_code=404, detail="该订单暂无物流信息")
    return logistics
