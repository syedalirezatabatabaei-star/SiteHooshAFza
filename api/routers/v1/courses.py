from fastapi import APIRouter, Depends, HTTPException, Query, status
from django.db.models import Q, Count
from django.utils.text import slugify
from typing import Optional
import math

from deps import get_current_user, get_optional_user
from schemas.v1.courses import (
    CourseListResponse,
    CourseDetailResponse,
    CategoryResponse,
    CourseScheduleResponse,
    InPersonDetailResponse,
    ChapterResponse,
    LessonBrief,
    InstructorBrief,
    InstructorDetail,
    PaginatedResponse,
)

from apps.courses.models import Course, Category, Instructor, InPersonDetail, Chapter, Lesson, CourseSchedule

router = APIRouter()


def serialize_course(course) -> CourseListResponse:
    return CourseListResponse(
        id=course.id,
        title=course.title,
        slug=course.slug,
        short_description=course.short_description,
        thumbnail=course.thumbnail.url if course.thumbnail else None,
        course_type=course.course_type,
        price=course.price,
        instructor=InstructorBrief(
            id=course.instructor.id,
            name=course.instructor.name,
            slug=course.instructor.slug,
            profile_image=course.instructor.profile_image.url if course.instructor.profile_image else None,
        ),
        category=CategoryResponse(
            id=course.category.id,
            name=course.category.name,
            slug=course.category.slug,
        ) if course.category else None,
        average_rating=course.average_rating,
        review_count=course.review_count,
    )


@router.get('', response_model=PaginatedResponse)
def list_courses(
    type: Optional[str] = Query(None, description='IN_PERSON or RECORDED'),
    category: Optional[str] = Query(None, description='Category slug'),
    search: Optional[str] = Query(None, description='Search text'),
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    """لیست دوره‌ها"""
    qs = Course.objects.filter(status='PUBLISHED', is_published=True).select_related('instructor', 'category')

    if type:
        qs = qs.filter(course_type=type)
    if category:
        qs = qs.filter(category__slug=category)
    if search:
        qs = qs.filter(
            Q(title__icontains=search) |
            Q(short_description__icontains=search) |
            Q(instructor__name__icontains=search)
        )

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    courses = qs[offset:offset + page_size]

    items = [serialize_course(c) for c in courses]
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        pages=pages,
        page_size=page_size,
    )


@router.get('/categories', response_model=list[CategoryResponse])
def list_categories():
    """لیست دسته‌بندی‌ها"""
    cats = Category.objects.filter(is_active=True)
    return [CategoryResponse(
        id=c.id, name=c.name, slug=c.slug, description=c.description,
        parent_id=c.parent_id,
    ) for c in cats]


@router.get('/in-person')
def list_in_person_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    """دوره‌های حضوری"""
    qs = Course.objects.filter(status='PUBLISHED', is_published=True, course_type='IN_PERSON').select_related('instructor', 'category')
    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    courses = qs[offset:offset + page_size]
    items = [serialize_course(c) for c in courses]
    return PaginatedResponse(items=items, total=total, page=page, pages=pages, page_size=page_size)


@router.get('/recorded')
def list_recorded_courses(
    page: int = Query(1, ge=1),
    page_size: int = Query(12, ge=1, le=50),
):
    """دوره‌های ضبط‌شده"""
    qs = Course.objects.filter(status='PUBLISHED', is_published=True, course_type='RECORDED').select_related('instructor', 'category')
    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    courses = qs[offset:offset + page_size]
    items = [serialize_course(c) for c in courses]
    return PaginatedResponse(items=items, total=total, page=page, pages=pages, page_size=page_size)


@router.get('/featured')
def featured_courses():
    """دوره‌های ویژه"""
    courses = Course.objects.filter(status='PUBLISHED', is_published=True).select_related('instructor', 'category')[:6]
    return [serialize_course(c) for c in courses]


@router.get('/{slug}', response_model=CourseDetailResponse)
def get_course(slug: str):
    """جزئیات دوره"""
    try:
        course = Course.objects.select_related('instructor', 'category').get(slug=slug)
    except Course.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='دوره یافت نشد')

    chapters = []
    if course.is_recorded:
        for ch in course.chapters.filter(is_published=True).prefetch_related('lessons'):
            lessons = [
                LessonBrief(
                    id=l.id, title=l.title, duration=l.duration,
                    is_preview=l.is_preview, spotplayer_id=l.spotplayer_id,
                ) for l in ch.lessons.filter(is_published=True)
            ]
            chapters.append(ChapterResponse(
                id=ch.id, title=ch.title, order=ch.order, lessons=lessons,
            ))

    schedules = [
        CourseScheduleResponse(day_of_week=s.day_of_week, start_time=s.start_time, end_time=s.end_time)
        for s in course.schedules.all()
    ]

    inperson = None
    if hasattr(course, 'inperson_detail'):
        ipd = course.inperson_detail
        inperson = InPersonDetailResponse(
            prepayment_amount=ipd.prepayment_amount,
            remaining_amount=ipd.remaining_amount,
            capacity=ipd.capacity,
            start_date=ipd.start_date,
            end_date=ipd.end_date,
            location=ipd.location,
        )

    return CourseDetailResponse(
        id=course.id,
        title=course.title,
        slug=course.slug,
        short_description=course.short_description,
        description=course.description,
        thumbnail=course.thumbnail.url if course.thumbnail else None,
        course_type=course.course_type,
        price=course.price,
        status=course.status,
        instructor=InstructorBrief(
            id=course.instructor.id,
            name=course.instructor.name,
            slug=course.instructor.slug,
            profile_image=course.instructor.profile_image.url if course.instructor.profile_image else None,
        ),
        category=CategoryResponse(
            id=course.category.id, name=course.category.name, slug=course.category.slug,
        ) if course.category else None,
        chapters=chapters,
        schedules=schedules,
        inperson_detail=inperson,
        average_rating=course.average_rating,
        review_count=course.review_count,
        enrolled_count=course.enrolled_count,
        total_lessons=course.total_lessons,
        meta_title=course.meta_title,
        meta_description=course.meta_description,
    )
