from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from knowledge_base.database import get_db
from knowledge_base.models import Transfer, TransferStatus
from api_gateway.schemas import TransferCreate, TransferUpdate, TransferResponse

router = APIRouter(prefix="/transfers", tags=["转接管理"])

@router.get("/", response_model=List[TransferResponse])
async def get_transfers(db: Session = Depends(get_db)):
    """获取所有转接记录列表"""
    return db.query(Transfer).all()

@router.get("/{transfer_id}", response_model=TransferResponse)
async def get_transfer(transfer_id: int, db: Session = Depends(get_db)):
    """获取单个转接详情"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="转接记录不存在")
    return transfer

@router.post("/", response_model=TransferResponse)
async def create_transfer(transfer: TransferCreate, db: Session = Depends(get_db)):
    """创建转接"""
    db_transfer = Transfer(**transfer.model_dump())
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    return db_transfer

@router.put("/{transfer_id}")
async def update_transfer(transfer_id: int, transfer_update: TransferUpdate, db: Session = Depends(get_db)):
    """更新转接状态"""
    transfer = db.query(Transfer).filter(Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=404, detail="转接记录不存在")
    transfer.status = transfer_update.status
    db.commit()
    return {"message": "转接状态更新成功", "transfer": TransferResponse.model_validate(transfer)}

@router.get("/agent/{agent_name}", response_model=List[TransferResponse])
async def get_agent_transfers(agent_name: str, db: Session = Depends(get_db)):
    """获取指定客服的转接记录"""
    return db.query(Transfer).filter(
        (Transfer.from_agent == agent_name) | (Transfer.to_agent == agent_name)
    ).all()
