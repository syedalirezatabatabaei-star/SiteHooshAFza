from pydantic import BaseModel
from typing import Optional, List
from datetime import date, time, datetime
from decimal import Decimal


class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str = ''
    parent_id: Optional[int] = None

    class Config:
        from_attributes = True


class InstructorBrief(BaseModel):
    id: int
    name: str
    slug: str
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True


class InstructorDetail(BaseModel):
    id: int
    name: str
    slug: str
    profile_image: Optional[str] = None
    bio: str
    specialization: str
    education: str = ''
    experience: str = ''
    social_links: dict = {}

    class Config:
        from_attributes = True


class CourseScheduleResponse(BaseModel):
    day_of_week: str
    start_time: time
    end_time: time

    class Config:
        from_attributes = True


class InPersonDetailResponse(BaseModel):
    prepayment_amount: Decimal
    remaining_amount: Decimal
    capacity: int
    start_date: date
    end_date: date
    location: str

    class Config:
        from_attributes = True


class LessonBrief(BaseModel):
    id: int
    title: str
    duration: int
    is_preview: bool
    spotplayer_id: Optional[str] = None

    class Config:
        from_attributes = True


class ChapterResponse(BaseModel):
    id: int
    title: str
    order: int
    lessons: List[LessonBrief] = []

    class Config:
        from_attributes = True


class CourseListResponse(BaseModel):
    id: int
    title: str
    slug: str
    short_description: str
    thumbnail: Optional[str] = None
    course_type: str
    price: Decimal
    instructor: InstructorBrief
    category: Optional[CategoryResponse] = None
    average_rating: float = 0
    review_count: int = 0

    class Config:
        from_attributes = True


class CourseDetailResponse(BaseModel):
    id: int
    title: str
    slug: str
    short_description: str
    description: str
    thumbnail: Optional[str] = None
    course_type: str
    price: Decimal
    status: str
    instructor: InstructorBrief
    category: Optional[CategoryResponse] = None
    chapters: List[ChapterResponse] = []
    schedules: List[CourseScheduleResponse] = []
    inperson_detail: Optional[InPersonDetailResponse] = None
    average_rating: float = 0
    review_count: int = 0
    enrolled_count: int = 0
    total_lessons: int = 0
    meta_title: str = ''
    meta_description: str = ''

    class Config:
        from_attributes = True


class CourseBrief(BaseModel):
    id: int
    title: str
    slug: str
    thumbnail: Optional[str] = None
    price: Decimal

    class Config:
        from_attributes = True


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    pages: int
    page_size: int
