from fastapi import APIRouter, Depends, HTTPException, status
from django.db.models import Prefetch, Q

from deps import get_current_user
from schemas.v1.enrollments import EnrollmentResponse, ProgressUpdateRequest
from apps.enrollments.models import Enrollment
from apps.courses.models import Lesson

router = APIRouter()


@router.get('')
def list_enrollments(user=Depends(get_current_user)):
    """لیست ثبت‌نام‌های کاربر"""
    enrollments = Enrollment.objects.filter(
        student=user
    ).select_related('course', 'course__instructor', 'last_lesson')

    result = []
    for e in enrollments:
        last_lesson_title = None
        if e.last_lesson:
            last_lesson_title = e.last_lesson.title
        result.append(EnrollmentResponse(
            id=e.id,
            course_id=e.course.id,
            course_title=e.course.title,
            course_slug=e.course.slug,
            course_thumbnail=e.course.thumbnail.url if e.course.thumbnail else None,
            course_type=e.course.course_type,
            status=e.status,
            enrolled_at=e.enrolled_at,
            access_start=e.access_start,
            access_end=e.access_end,
            progress=e.progress,
            last_lesson_id=e.last_lesson_id,
            last_lesson_title=last_lesson_title,
        ))
    return result


@router.get('/{enrollment_id}')
def get_enrollment(enrollment_id: int, user=Depends(get_current_user)):
    """جزئیات ثبت‌نام"""
    try:
        e = Enrollment.objects.select_related('course', 'course__instructor', 'last_lesson').get(
            pk=enrollment_id, student=user
        )
    except Enrollment.DoesNotExist:
        raise HTTPException(status_code=404, detail='ثبت‌نام یافت نشد')

    return EnrollmentResponse(
        id=e.id,
        course_id=e.course.id,
        course_title=e.course.title,
        course_slug=e.course.slug,
        course_thumbnail=e.course.thumbnail.url if e.course.thumbnail else None,
        course_type=e.course.course_type,
        status=e.status,
        enrolled_at=e.enrolled_at,
        access_start=e.access_start,
        access_end=e.access_end,
        progress=e.progress,
        last_lesson_id=e.last_lesson_id,
        last_lesson_title=e.last_lesson.title if e.last_lesson else None,
    )


@router.put('/{enrollment_id}/progress')
def update_progress(
    enrollment_id: int,
    data: ProgressUpdateRequest,
    user=Depends(get_current_user),
):
    """به‌روزرسانی پیشرفت دوره"""
    try:
        enrollment = Enrollment.objects.get(pk=enrollment_id, student=user)
    except Enrollment.DoesNotExist:
        raise HTTPException(status_code=404, detail='ثبت‌نام یافت نشد')

    if not enrollment.is_access_valid:
        raise HTTPException(status_code=400, detail='ثبت‌نام فعال نیست')

    # Verify lesson belongs to the course
    try:
        lesson = Lesson.objects.get(pk=data.lesson_id, chapter__course=enrollment.course)
    except Lesson.DoesNotExist:
        raise HTTPException(status_code=404, detail='جلسه متعلق به این دوره نیست')

    # Update last lesson
    enrollment.last_lesson = lesson

    # Calculate progress
    total_lessons = enrollment.course.total_lessons
    if total_lessons > 0:
        current_lesson_order = lesson.order
        completed_count = Lesson.objects.filter(
            chapter__course=enrollment.course,
        ).filter(Q(chapter__order__lt=lesson.chapter.order) |
                 Q(chapter=lesson.chapter, order__lte=current_lesson_order)).count()
        enrollment.progress = max(enrollment.progress, round((completed_count / total_lessons) * 100, 2))

    enrollment.save(update_fields=['last_lesson', 'progress'])

    return {
        'progress': str(enrollment.progress),
        'last_lesson': {'id': lesson.id, 'title': lesson.title},
    }


@router.get('/check-access/{course_id}')
def check_access(course_id: int, user=Depends(get_current_user)):
    """بررسی دسترسی به دوره"""
    try:
        enrollment = Enrollment.objects.get(student=user, course_id=course_id, status='ACTIVE')
    except Enrollment.DoesNotExist:
        return {'has_access': False}

    return {
        'has_access': enrollment.is_access_valid,
        'enrollment_id': enrollment.id,
        'progress': str(enrollment.progress),
    }



@router.get('/spotplayer-licenses')
def list_spotplayer_licenses(user=Depends(get_current_user)):
    """لیسانس‌های SpotPlayer صادرشده برای سفارش‌های همین کاربر."""
    from apps.courses.models import SpotPlayerLicense
    records = SpotPlayerLicense.objects.filter(
        order_item__order__user=user,
        order_item__order__status='PAID',
        status='CREATED',
    ).select_related('order_item__course').order_by('-created_at')
    return [{
        'course_id': row.order_item.course_id,
        'course_title': row.order_item.course.title,
        'license_id': row.external_license_id,
        'license_key': row.license_key,
        'license_url': row.license_url,
        'created_at': row.created_at,
    } for row in records]
