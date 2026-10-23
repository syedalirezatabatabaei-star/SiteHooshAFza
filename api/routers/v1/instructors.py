from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import math

from schemas.v1.courses import InstructorDetail, CourseListResponse, InstructorBrief, PaginatedResponse
from apps.courses.models import Instructor, Course

router = APIRouter()


def serialize_course(course) -> CourseListResponse:
    return CourseListResponse(
        id=course.id, title=course.title, slug=course.slug,
        short_description=course.short_description,
        thumbnail=course.thumbnail.url if course.thumbnail else None,
        course_type=course.course_type, price=course.price,
        instructor=InstructorBrief(
            id=course.instructor.id, name=course.instructor.name,
            slug=course.instructor.slug,
            profile_image=course.instructor.profile_image.url if course.instructor.profile_image else None,
        ),
        average_rating=course.average_rating,
        review_count=course.review_count,
    )


@router.get('')
def list_instructors(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    """لیست مدرسین"""
    qs = Instructor.objects.filter(is_active=True)
    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    instructors = qs[offset:offset + page_size]

    items = []
    for inst in instructors:
        items.append(InstructorDetail(
            id=inst.id, name=inst.name, slug=inst.slug,
            profile_image=inst.profile_image.url if inst.profile_image else None,
            bio=inst.bio, specialization=inst.specialization,
            education=inst.education, experience=inst.experience,
            social_links=inst.social_links,
        ))
    return PaginatedResponse(items=items, total=total, page=page, pages=pages, page_size=page_size)


@router.get('/{slug}')
def get_instructor(slug: str):
    """جزئیات مدرس و دوره‌هایش"""
    try:
        inst = Instructor.objects.get(slug=slug, is_active=True)
    except Instructor.DoesNotExist:
        raise HTTPException(status_code=404, detail='مدرس یافت نشد')

    courses = Course.objects.filter(
        instructor=inst, status='PUBLISHED', is_published=True
    ).select_related('instructor', 'category')

    return {
        'instructor': InstructorDetail(
            id=inst.id, name=inst.name, slug=inst.slug,
            profile_image=inst.profile_image.url if inst.profile_image else None,
            bio=inst.bio, specialization=inst.specialization,
            education=inst.education, experience=inst.experience,
            social_links=inst.social_links,
        ),
        'courses': [serialize_course(c) for c in courses],
    }
