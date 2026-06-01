from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: str
    phone: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class OrderCreate(BaseModel):
    user_id: int
    total_amount: float

class OrderResponse(BaseModel):
    id: int
    user_id: int
    order_number: str
    total_amount: float
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RefundRequest(BaseModel):
    order_id: int
    amount: float
    reason: str

class RefundUpdate(BaseModel):
    status: str

class RefundResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LogisticsUpdate(BaseModel):
    tracking_number: str
    carrier: str
    status: str
    estimated_delivery: Optional[datetime] = None

class LogisticsResponse(BaseModel):
    id: int
    order_id: int
    tracking_number: str
    carrier: str
    status: str
    estimated_delivery: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ComplaintCreate(BaseModel):
    user_id: int
    order_id: Optional[int] = None
    title: str
    description: str
    priority: int = 1

class ComplaintResponse(BaseModel):
    id: int
    user_id: int
    order_id: Optional[int] = None
    title: str
    description: str
    status: str
    priority: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TransferCreate(BaseModel):
    from_agent: str
    to_agent: str
    order_id: Optional[int] = None
    complaint_id: Optional[int] = None
    reason: str

class TransferUpdate(BaseModel):
    status: str

class TransferResponse(BaseModel):
    id: int
    from_agent: str
    to_agent: str
    order_id: Optional[int] = None
    complaint_id: Optional[int] = None
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class EscalationCreate(BaseModel):
    order_id: Optional[int] = None
    complaint_id: Optional[int] = None
    level: str
    reason: str

class EscalationResponse(BaseModel):
    id: int
    order_id: Optional[int] = None
    complaint_id: Optional[int] = None
    level: str
    reason: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
