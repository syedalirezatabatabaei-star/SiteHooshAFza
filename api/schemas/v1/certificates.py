from pydantic import BaseModel
from typing import Optional
from datetime import date


class CertificateResponse(BaseModel):
    id: int
    certificate_number: str
    course_id: int
    course_title: str
    issue_date: date
    status: str
    verification_code: str
    file: Optional[str] = None

    class Config:
        from_attributes = True


class CertificateVerifyResponse(BaseModel):
    valid: bool
    certificate_number: Optional[str] = None
    student_name: Optional[str] = None
    course_title: Optional[str] = None
    issue_date: Optional[date] = None
