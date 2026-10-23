from fastapi import APIRouter, Depends, HTTPException

from deps import get_current_user
from schemas.v1.certificates import CertificateResponse, CertificateVerifyResponse
from apps.certificates.models import Certificate
from apps.courses.models import Course
from apps.enrollments.models import Enrollment
from apps.exams.models import ExamAttempt

router = APIRouter()


@router.get('')
def list_certificates(user=Depends(get_current_user)):
    """لیست گواهینامه‌های کاربر"""
    certs = Certificate.objects.filter(student=user, status='ISSUED').select_related('course')
    return [CertificateResponse(
        id=c.id, certificate_number=c.certificate_number,
        course_id=c.course.id, course_title=c.course.title,
        issue_date=c.issue_date, status=c.status,
        verification_code=c.verification_code,
        file=c.file.url if c.file else None,
    ) for c in certs]


@router.get('/verify/{code}')
def verify_certificate(code: str):
    """تأیید گواهینامه"""
    try:
        cert = Certificate.objects.select_related('student', 'course').get(
            verification_code=code, status='ISSUED'
        )
    except Certificate.DoesNotExist:
        return CertificateVerifyResponse(valid=False)

    return CertificateVerifyResponse(
        valid=True,
        certificate_number=cert.certificate_number,
        student_name=cert.student.full_name,
        course_title=cert.course.title,
        issue_date=cert.issue_date,
    )


@router.post('/issue/{course_id}')
def request_certificate(course_id: int, user=Depends(get_current_user)):
    """درخواست صدور گواهینامه"""
    try:
        enrollment = Enrollment.objects.get(student=user, course_id=course_id, status='ACTIVE')
    except Enrollment.DoesNotExist:
        raise HTTPException(status_code=404, detail='ثبت‌نام یافت نشد')

    # Check progress
    if enrollment.progress < 70:
        raise HTTPException(
            status_code=400,
            detail=f'پیشرفت شما {enrollment.progress}% است. حداقل ۷۰٪ برای صدور گواهینامه لازم است',
        )

    # Check exam passed
    passed = ExamAttempt.objects.filter(
        student=user, exam__course_id=course_id, passed=True,
    ).exists()

    if not passed:
        raise HTTPException(
            status_code=400,
            detail='برای صدور گواهینامه باید آزمون را با موفقیت گذرانده باشید',
        )

    # Create or get certificate
    cert, created = Certificate.objects.get_or_create(
        student=user,
        course_id=course_id,
        defaults={'status': 'ISSUED'},
    )

    return CertificateResponse(
        id=cert.id, certificate_number=cert.certificate_number,
        course_id=cert.course.id, course_title=cert.course.title,
        issue_date=cert.issue_date, status=cert.status,
        verification_code=cert.verification_code,
        file=cert.file.url if cert.file else None,
    )
