from pydantic import BaseModel, Field
from typing import Optional


class CareerApplicationCreate(BaseModel):
    application_type: str = Field(min_length=1, max_length=12)
    full_name: str = Field(min_length=2, max_length=180)
    phone: str = Field(min_length=7, max_length=30)
    email: Optional[str] = Field(default=None, max_length=254)
    organization: str = Field(default='', max_length=200)
    position: str = Field(default='', max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    resume_url: Optional[str] = Field(default='', max_length=1000)


class CareerApplicationUpdate(BaseModel):
    status: str = Field(min_length=1, max_length=12)
    admin_notes: str = Field(default='', max_length=5000)
