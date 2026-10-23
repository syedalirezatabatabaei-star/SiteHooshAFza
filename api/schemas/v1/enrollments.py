from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from datetime import datetime


class EnrollmentResponse(BaseModel):
    id: int
    course_id: int
    course_title: str
    course_slug: str
    course_thumbnail: Optional[str] = None
    course_type: str
    status: str
    enrolled_at: datetime
    access_start: Optional[datetime] = None
    access_end: Optional[datetime] = None
    progress: Decimal
    last_lesson_id: Optional[int] = None
    last_lesson_title: Optional[str] = None

    class Config:
        from_attributes = True


class ProgressUpdateRequest(BaseModel):
    lesson_id: int


class AdminEnrollRequest(BaseModel):
    student_id: int
    course_id: int
    access_start: Optional[str] = None
    access_end: Optional[str] = None
