from pydantic import BaseModel
from typing import List, Optional
from decimal import Decimal
from datetime import datetime


class CartItemResponse(BaseModel):
    id: int
    course_id: int
    course_title: str
    course_slug: str
    course_thumbnail: Optional[str] = None
    course_price: Decimal
    course_type: str
    added_at: datetime

    class Config:
        from_attributes = True


class CartAddRequest(BaseModel):
    course_id: int


class CartCouponRequest(BaseModel):
    code: str


class CartResponse(BaseModel):
    id: int
    items: List[CartItemResponse] = []
    subtotal: Decimal
    discount: Decimal
    total: Decimal
    coupon_code: Optional[str] = None

    class Config:
        from_attributes = True
