from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from knowledge_base.database import get_db
from knowledge_base.models import Complaint, ComplaintStatus
from api_gateway.schemas import ComplaintCreate, ComplaintResponse

router = APIRouter(prefix="/complaints", tags=["投诉管理"])

@router.get("/", response_model=List[ComplaintResponse])
async def get_complaints(db: Session = Depends(get_db)):
    """获取所有投诉列表"""
    return db.query(Complaint).all()

@router.get("/{complaint_id}", response_model=ComplaintResponse)
async def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    """获取单个投诉详情"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="投诉不存在")
    return complaint

@router.post("/", response_model=ComplaintResponse)
async def create_complaint(complaint: ComplaintCreate, db: Session = Depends(get_db)):
    """创建投诉"""
    db_complaint = Complaint(**complaint.model_dump())
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

@router.put("/{complaint_id}/status")
async def update_complaint_status(complaint_id: int, status: ComplaintStatus, db: Session = Depends(get_db)):
    """更新投诉状态"""
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="投诉不存在")
    complaint.status = status
    db.commit()
    return {"message": "投诉状态更新成功", "complaint": ComplaintResponse.model_validate(complaint)}

@router.get("/user/{user_id}", response_model=List[ComplaintResponse])
async def get_user_complaints(user_id: int, db: Session = Depends(get_db)):
    """获取指定用户的所有投诉"""
    return db.query(Complaint).filter(Complaint.user_id == user_id).all()

@router.get("/order/{order_id}", response_model=List[ComplaintResponse])
async def get_order_complaints(order_id: int, db: Session = Depends(get_db)):
    """获取指定订单的所有投诉"""
    return db.query(Complaint).filter(Complaint.order_id == order_id).all()
