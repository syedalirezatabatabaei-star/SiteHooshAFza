from fastapi import APIRouter, Depends, HTTPException, status

from deps import get_current_user
from schemas.v1.reviews import ReviewCreateRequest, ReviewResponse
from apps.reviews.models import Review
from apps.enrollments.models import Enrollment

router = APIRouter()


@router.post('', response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(data: ReviewCreateRequest, user=Depends(get_current_user)):
    """ایجاد نظر"""
    # Check enrollment
    if not Enrollment.objects.filter(student=user, course_id=data.course_id, status='ACTIVE').exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='شما در این دوره ثبت‌نام نکرده‌اید',
        )

    if Review.objects.filter(student=user, course_id=data.course_id).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='شما قبلاً برای این دوره نظر ثبت کرده‌اید',
        )

    review = Review.objects.create(
        student=user,
        course_id=data.course_id,
        rating=data.rating,
        comment=data.comment,
    )

    return ReviewResponse(
        id=review.id,
        course_id=review.course_id,
        student_name=user.full_name,
        rating=review.rating,
        comment=review.comment,
        status=review.status,
        created_at=review.created_at,
    )


@router.get('/course/{course_id}')
def list_course_reviews(course_id: int):
    """نظرات یک دوره"""
    reviews = Review.objects.filter(
        course_id=course_id, status='APPROVED'
    ).select_related('student')
    return [ReviewResponse(
        id=r.id, course_id=r.course_id,
        student_name=r.student.full_name,
        rating=r.rating, comment=r.comment,
        status=r.status, created_at=r.created_at,
    ) for r in reviews]
