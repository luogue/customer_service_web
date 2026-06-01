from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from knowledge_base.database import get_db
from knowledge_base.models import Refund, Order, RefundStatus
from api_gateway.schemas import RefundRequest, RefundUpdate, RefundResponse

router = APIRouter(prefix="/refunds", tags=["退款管理"])

@router.get("/", response_model=List[RefundResponse])
async def get_refunds(db: Session = Depends(get_db)):
    """获取所有退款申请列表"""
    return db.query(Refund).all()

@router.get("/{refund_id}", response_model=RefundResponse)
async def get_refund(refund_id: int, db: Session = Depends(get_db)):
    """获取单个退款详情"""
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="退款申请不存在")
    return refund

@router.post("/", response_model=RefundResponse)
async def create_refund(refund: RefundRequest, db: Session = Depends(get_db)):
    """创建退款申请"""
    db_refund = Refund(**refund.model_dump())
    db.add(db_refund)
    db.commit()
    db.refresh(db_refund)
    return db_refund

@router.put("/{refund_id}")
async def update_refund(refund_id: int, refund_update: RefundUpdate, db: Session = Depends(get_db)):
    """更新退款状态"""
    refund = db.query(Refund).filter(Refund.id == refund_id).first()
    if not refund:
        raise HTTPException(status_code=404, detail="退款申请不存在")
    refund.status = refund_update.status
    db.commit()
    return {"message": "退款状态更新成功", "refund": RefundResponse.model_validate(refund)}

@router.get("/order/{order_id}", response_model=List[RefundResponse])
async def get_order_refunds(order_id: int, db: Session = Depends(get_db)):
    """获取指定订单的退款记录"""
    return db.query(Refund).filter(Refund.order_id == order_id).all()
