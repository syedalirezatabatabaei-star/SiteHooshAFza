from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime


class ReviewCreateRequest(BaseModel):
    course_id: int
    rating: int
    comment: str

    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v):
        if v < 1 or v > 5:
            raise ValueError('امتیاز باید بین ۱ تا ۵ باشد')
        return v


class ReviewResponse(BaseModel):
    id: int
    course_id: int
    student_name: str
    rating: int
    comment: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
