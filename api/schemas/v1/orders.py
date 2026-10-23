from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class OrderItemResponse(BaseModel):
    course_id: int
    course_title: str
    course_thumbnail: Optional[str] = None
    price_at_purchase: Decimal
    payment_type: str

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    coupon_code: Optional[str] = None
    status: str
    created_at: datetime
    items: List[OrderItemResponse] = []

    class Config:
        from_attributes = True


class CheckoutResponse(BaseModel):
    order_id: int
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
