from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class CareerApplicationCreate(BaseModel):
    application_type: str = Field(pattern='^(INSTITUTE|SUBSIDIARY|JOB)$')
    full_name: str = Field(min_length=2, max_length=180)
    phone: str = Field(min_length=7, max_length=30)
    email: Optional[EmailStr] = None
    organization: str = Field(default='', max_length=200)
    position: str = Field(default='', max_length=200)
    message: str = Field(min_length=10, max_length=5000)
    resume_url: Optional[str] = Field(default='', max_length=1000)


class CareerApplicationUpdate(BaseModel):
    status: str = Field(pattern='^(NEW|REVIEWING|CONTACTED|REJECTED)$')
    admin_notes: str = Field(default='', max_length=5000)
