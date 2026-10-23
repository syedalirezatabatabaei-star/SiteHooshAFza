from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TicketCreateRequest(BaseModel):
    subject: str
    message: str
    priority: str = 'MEDIUM'


class TicketMessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_name: str
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    id: int
    subject: str
    status: str
    priority: str
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    last_message: Optional[str] = None

    class Config:
        from_attributes = True


class TicketDetailResponse(BaseModel):
    id: int
    subject: str
    status: str
    priority: str
    messages: List[TicketMessageResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TicketReplyRequest(BaseModel):
    message: str


class TicketUpdateStatusRequest(BaseModel):
    status: str
