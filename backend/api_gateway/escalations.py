from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from knowledge_base.database import get_db
from knowledge_base.models import Escalation, EscalationLevel
from api_gateway.schemas import EscalationCreate, EscalationResponse

router = APIRouter(prefix="/escalations", tags=["升级管理"])

@router.get("/", response_model=List[EscalationResponse])
async def get_escalations(db: Session = Depends(get_db)):
    """获取所有升级记录列表"""
    return db.query(Escalation).all()

@router.get("/{escalation_id}", response_model=EscalationResponse)
async def get_escalation(escalation_id: int, db: Session = Depends(get_db)):
    """获取单个升级详情"""
    escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not escalation:
        raise HTTPException(status_code=404, detail="升级记录不存在")
    return escalation

@router.post("/", response_model=EscalationResponse)
async def create_escalation(escalation: EscalationCreate, db: Session = Depends(get_db)):
    """创建升级"""
    db_escalation = Escalation(**escalation.model_dump())
    db.add(db_escalation)
    db.commit()
    db.refresh(db_escalation)
    return db_escalation

@router.put("/{escalation_id}/status")
async def update_escalation_status(escalation_id: int, status: str, db: Session = Depends(get_db)):
    """更新升级状态"""
    escalation = db.query(Escalation).filter(Escalation.id == escalation_id).first()
    if not escalation:
        raise HTTPException(status_code=404, detail="升级记录不存在")
    escalation.status = status
    db.commit()
    return {"message": "升级状态更新成功", "escalation": EscalationResponse.model_validate(escalation)}

@router.get("/order/{order_id}", response_model=List[EscalationResponse])
async def get_order_escalations(order_id: int, db: Session = Depends(get_db)):
    """获取指定订单的升级记录"""
    return db.query(Escalation).filter(Escalation.order_id == order_id).all()

@router.get("/complaint/{complaint_id}", response_model=List[EscalationResponse])
async def get_complaint_escalations(complaint_id: int, db: Session = Depends(get_db)):
    """获取指定投诉的升级记录"""
    return db.query(Escalation).filter(Escalation.complaint_id == complaint_id).all()
