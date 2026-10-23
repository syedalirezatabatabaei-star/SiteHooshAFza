from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserProfileResponse(BaseModel):
    id: int
    phone_number: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    role: str
    profile_image: Optional[str] = None
    date_joined: datetime

    class Config:
        from_attributes = True


class UserProfileUpdateRequest(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
