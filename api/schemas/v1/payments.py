from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class PaymentInitiateRequest(BaseModel):
    order_id: int


class PaymentResponse(BaseModel):
    id: int
    amount: Decimal
    payment_type: str
    gateway: str
    status: str
    transaction_id: str
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaymentCallbackResponse(BaseModel):
    message: str
    success: bool
