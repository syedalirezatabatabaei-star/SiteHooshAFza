from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class AdminDashboardStats(BaseModel):
    students_count: int
    courses_count: int
    in_person_count: int
    recorded_count: int
    orders_count: int
    total_revenue: Decimal
    successful_payments: int
    open_tickets: int
    articles_count: int
    total_enrollments: int
    certificates_issued: int


class AdminUserCreateRequest(BaseModel):
    phone_number: str
    password: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    role: str = 'STUDENT'


class AdminUserUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class AdminUserResponse(BaseModel):
    id: int
    phone_number: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    role: str
    is_active: bool
    date_joined: datetime
    enrollment_count: int = 0

    class Config:
        from_attributes = True


class AdminCouponCreateRequest(BaseModel):
    code: str
    discount_type: str
    discount_value: Decimal
    start_date: str
    end_date: str
    max_uses: int = 0
    is_active: bool = True
    applicable_course_ids: List[int] = []


class AdminEnrollRequest(BaseModel):
    student_id: int
    course_id: int
    access_start: Optional[str] = None
    access_end: Optional[str] = None


class AdminNotificationSendRequest(BaseModel):
    user_id: int
    title: str
    message: str
    type: str = 'INFO'


class AdminOrderResponse(BaseModel):
    id: int
    user_phone: str
    user_name: str
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    status: str
    created_at: datetime
    coupon_code: str = ''

    class Config:
        from_attributes = True


class AdminPaymentResponse(BaseModel):
    id: int
    user_phone: str
    order_id: int
    amount: Decimal
    payment_type: str
    gateway: str
    status: str
    transaction_id: str
    created_at: datetime
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PaginatedAdminResponse(BaseModel):
    items: list
    total: int
    page: int
    pages: int
