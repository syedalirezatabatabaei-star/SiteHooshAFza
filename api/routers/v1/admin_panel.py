from fastapi import APIRouter, Depends, HTTPException, Query, status
from django.contrib.auth import get_user_model
from django.db import transaction
import math

from deps import get_current_admin
from schemas.v1.admin_panel import (
    AdminDashboardStats, AdminUserCreateRequest, AdminUserUpdateRequest,
    AdminUserResponse, AdminCouponCreateRequest, AdminEnrollRequest,
    AdminNotificationSendRequest, AdminOrderResponse, AdminPaymentResponse,
    PaginatedAdminResponse,
)
from apps.courses.models import Course, Chapter, Lesson
from apps.enrollments.models import Enrollment
from apps.orders.models import Order
from apps.payments.models import Payment
from apps.discounts.models import Coupon
from apps.blog.models import Article
from apps.tickets.models import Ticket
from apps.certificates.models import Certificate
from apps.notifications.models import Notification

User = get_user_model()
router = APIRouter()


# ──────────── Dashboard Stats ────────────

@router.get('/dashboard/stats', response_model=AdminDashboardStats)
def dashboard_stats(admin=Depends(get_current_admin)):
    """آمار داشبورد مدیریت"""
    return AdminDashboardStats(
        students_count=User.objects.filter(role='STUDENT', is_active=True).count(),
        courses_count=Course.objects.count(),
        in_person_count=Course.objects.filter(course_type='IN_PERSON').count(),
        recorded_count=Course.objects.filter(course_type='RECORDED').count(),
        orders_count=Order.objects.count(),
        total_revenue=Payment.objects.filter(status='SUCCESS').aggregate(
            total=models_sum('amount')
        )['total'] or 0,
        successful_payments=Payment.objects.filter(status='SUCCESS').count(),
        open_tickets=Ticket.objects.filter(status__in=['OPEN', 'IN_PROGRESS']).count(),
        articles_count=Article.objects.count(),
        total_enrollments=Enrollment.objects.filter(status='ACTIVE').count(),
        certificates_issued=Certificate.objects.filter(status='ISSUED').count(),
    )


from django.db.models import Sum as models_sum


# ──────────── Users ────────────

@router.get('/users', response_model=PaginatedAdminResponse)
def list_users(
    role: str = None,
    search: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
):
    """لیست کاربران"""
    qs = User.objects.all()
    if role:
        qs = qs.filter(role=role)
    if search:
        qs = qs.filter(phone_number__icontains=search) | qs.filter(first_name__icontains=search)

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    users = qs[offset:offset + page_size]

    items = [AdminUserResponse(
        id=u.id, phone_number=u.phone_number, first_name=u.first_name,
        last_name=u.last_name, email=u.email, role=u.role,
        is_active=u.is_active, date_joined=u.date_joined,
        enrollment_count=u.enrollments.filter(status='ACTIVE').count(),
    ) for u in users]

    return PaginatedAdminResponse(items=items, total=total, page=page, pages=pages)


@router.post('/users', response_model=AdminUserResponse, status_code=201)
def create_user(data: AdminUserCreateRequest, admin=Depends(get_current_admin)):
    """ایجاد کاربر"""
    if User.objects.filter(phone_number=data.phone_number).exists():
        raise HTTPException(status_code=400, detail='شماره تلفن قبلاً ثبت شده')

    user = User.objects.create_user(
        phone_number=data.phone_number,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        email=data.email,
        role=data.role,
    )
    return AdminUserResponse(
        id=user.id, phone_number=user.phone_number, first_name=user.first_name,
        last_name=user.last_name, email=user.email, role=user.role,
        is_active=user.is_active, date_joined=user.date_joined,
    )


@router.put('/users/{user_id}', response_model=AdminUserResponse)
def update_user(
    user_id: int,
    data: AdminUserUpdateRequest,
    admin=Depends(get_current_admin),
):
    """ویرایش کاربر"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail='کاربر یافت نشد')

    if data.first_name is not None:
        user.first_name = data.first_name
    if data.last_name is not None:
        user.last_name = data.last_name
    if data.email is not None:
        user.email = data.email
    if data.role is not None:
        user.role = data.role
    if data.is_active is not None:
        user.is_active = data.is_active
    user.save()

    return AdminUserResponse(
        id=user.id, phone_number=user.phone_number, first_name=user.first_name,
        last_name=user.last_name, email=user.email, role=user.role,
        is_active=user.is_active, date_joined=user.date_joined,
    )


@router.put('/users/{user_id}/deactivate')
def deactivate_user(user_id: int, admin=Depends(get_current_admin)):
    """غیرفعال‌سازی کاربر"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail='کاربر یافت نشد')

    user.is_active = False
    user.save(update_fields=['is_active'])
    return {'message': 'کاربر غیرفعال شد'}


@router.put('/users/{user_id}/reset-password')
def reset_password(
    user_id: int,
    password: str = Query(..., min_length=6),
    admin=Depends(get_current_admin),
):
    """بازنشانی رمز عبور"""
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail='کاربر یافت نشد')

    user.set_password(password)
    user.save()
    return {'message': 'رمز عبور با موفقیت تغییر کرد'}


# ──────────── Enrollments ────────────

@router.post('/enrollments', status_code=201)
def admin_enroll(data: AdminEnrollRequest, admin=Depends(get_current_admin)):
    """ثبت‌نام دستی توسط مدیر"""
    try:
        student = User.objects.get(pk=data.student_id, role='STUDENT')
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail='دانشجو یافت نشد')

    try:
        course = Course.objects.get(pk=data.course_id)
    except Course.DoesNotExist:
        raise HTTPException(status_code=404, detail='دوره یافت نشد')

    if Enrollment.objects.filter(student=student, course=course, status='ACTIVE').exists():
        raise HTTPException(status_code=400, detail='دانشجو قبلاً در این دوره ثبت‌نام شده')

    from django.utils import timezone
    from datetime import datetime

    access_start = timezone.now()
    access_end = None
    if data.access_start:
        access_start = datetime.fromisoformat(data.access_start)
    if data.access_end:
        access_end = datetime.fromisoformat(data.access_end)

    enrollment = Enrollment.objects.create(
        student=student,
        course=course,
        status='ACTIVE',
        access_start=access_start,
        access_end=access_end,
    )

    Notification.objects.create(
        user=student,
        title=f'ثبت‌نام در دوره {course.title}',
        message=f'ثبت‌نام شما در دوره {course.title} با موفقیت فعال شد.',
        type='SUCCESS',
    )

    return {'message': 'ثبت‌نام با موفقیت انجام شد', 'enrollment_id': enrollment.id}


@router.get('/enrollments')
def list_all_enrollments(
    student_id: int = None,
    course_id: int = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
):
    """لیست همه ثبت‌نام‌ها"""
    qs = Enrollment.objects.select_related('student', 'course')
    if student_id:
        qs = qs.filter(student_id=student_id)
    if course_id:
        qs = qs.filter(course_id=course_id)

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    enrollments = qs[offset:offset + page_size]

    return {
        'items': [{
            'id': e.id,
            'student': {'id': e.student.id, 'name': e.student.full_name, 'phone': e.student.phone_number},
            'course': {'id': e.course.id, 'title': e.course.title},
            'status': e.status,
            'progress': str(e.progress),
            'enrolled_at': e.enrolled_at.isoformat(),
        } for e in enrollments],
        'total': total, 'page': page, 'pages': pages,
    }


@router.put('/enrollments/{enrollment_id}')
def update_enrollment(
    enrollment_id: int,
    status_val: str = Query(None),
    admin=Depends(get_current_admin),
):
    """به‌روزرسانی ثبت‌نام"""
    try:
        enrollment = Enrollment.objects.get(pk=enrollment_id)
    except Enrollment.DoesNotExist:
        raise HTTPException(status_code=404, detail='ثبت‌نام یافت نشد')

    if status_val:
        enrollment.status = status_val
        enrollment.save(update_fields=['status'])

    return {'message': 'ثبت‌نام به‌روزرسانی شد'}


# ──────────── Orders ────────────

@router.get('/orders', response_model=PaginatedAdminResponse)
def list_orders(
    status_val: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
):
    """لیست سفارشات"""
    qs = Order.objects.select_related('user')
    if status_val:
        qs = qs.filter(status=status_val)

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    orders = qs[offset:offset + page_size]

    items = [AdminOrderResponse(
        id=o.id, user_phone=o.user.phone_number,
        user_name=o.user.full_name,
        total_amount=o.total_amount, discount_amount=o.discount_amount,
        final_amount=o.final_amount, status=o.status,
        created_at=o.created_at, coupon_code=o.coupon_code,
    ) for o in orders]

    return PaginatedAdminResponse(items=items, total=total, page=page, pages=pages)


# ──────────── Payments ────────────

@router.get('/payments', response_model=PaginatedAdminResponse)
def list_payments(
    status_val: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
):
    """لیست پرداخت‌ها"""
    qs = Payment.objects.select_related('user', 'order')
    if status_val:
        qs = qs.filter(status=status_val)

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    payments = qs[offset:offset + page_size]

    items = [AdminPaymentResponse(
        id=p.id, user_phone=p.user.phone_number, order_id=p.order_id,
        amount=p.amount, payment_type=p.payment_type,
        gateway=p.gateway, status=p.status,
        transaction_id=p.transaction_id,
        created_at=p.created_at, paid_at=p.paid_at,
    ) for p in payments]

    return PaginatedAdminResponse(items=items, total=total, page=page, pages=pages)


# ──────────── Discounts ────────────

@router.post('/discounts', status_code=201)
def create_coupon(data: AdminCouponCreateRequest, admin=Depends(get_current_admin)):
    """ایجاد کد تخفیف"""
    from django.utils import timezone
    from datetime import datetime

    coupon = Coupon.objects.create(
        code=data.code,
        discount_type=data.discount_type,
        discount_value=data.discount_value,
        start_date=datetime.fromisoformat(data.start_date),
        end_date=datetime.fromisoformat(data.end_date),
        max_uses=data.max_uses,
        is_active=data.is_active,
    )
    if data.applicable_course_ids:
        coupon.applicable_courses.set(data.applicable_course_ids)

    return {'message': 'کد تخفیف ایجاد شد', 'id': coupon.id}


@router.get('/discounts')
def list_coupons(admin=Depends(get_current_admin)):
    """لیست کدهای تخفیف"""
    coupons = Coupon.objects.all()
    return [{
        'id': c.id, 'code': c.code, 'discount_type': c.discount_type,
        'discount_value': str(c.discount_value), 'start_date': c.start_date.isoformat(),
        'end_date': c.end_date.isoformat(), 'max_uses': c.max_uses,
        'used_count': c.used_count, 'is_active': c.is_active,
    } for c in coupons]


@router.put('/discounts/{coupon_id}')
def update_coupon(
    coupon_id: int,
    is_active: bool = None,
    max_uses: int = None,
    admin=Depends(get_current_admin),
):
    """به‌روزرسانی کد تخفیف"""
    try:
        coupon = Coupon.objects.get(pk=coupon_id)
    except Coupon.DoesNotExist:
        raise HTTPException(status_code=404, detail='کد تخفیف یافت نشد')

    if is_active is not None:
        coupon.is_active = is_active
    if max_uses is not None:
        coupon.max_uses = max_uses
    coupon.save()
    return {'message': 'کد تخفیف به‌روزرسانی شد'}


# ──────────── Notifications ────────────

@router.post('/notifications', status_code=201)
def send_notification(data: AdminNotificationSendRequest, admin=Depends(get_current_admin)):
    """ارسال اعلان"""
    try:
        user = User.objects.get(pk=data.user_id)
    except User.DoesNotExist:
        raise HTTPException(status_code=404, detail='کاربر یافت نشد')

    Notification.objects.create(
        user=user, title=data.title, message=data.message, type=data.type,
    )
    return {'message': 'اعلان ارسال شد'}


# ──────────── Tickets ────────────

@router.get('/tickets')
def admin_list_tickets(
    status_val: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
):
    """لیست تیکت‌ها"""
    qs = Ticket.objects.select_related('user')
    if status_val:
        qs = qs.filter(status=status_val)

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    tickets = qs[offset:offset + page_size]

    return {
        'items': [{
            'id': t.id, 'subject': t.subject, 'status': t.status,
            'priority': t.priority, 'user': t.user.full_name,
            'created_at': t.created_at.isoformat(), 'updated_at': t.updated_at.isoformat(),
        } for t in tickets],
        'total': total, 'page': page, 'pages': pages,
    }


@router.post('/tickets/{ticket_id}/reply')
def admin_reply_ticket(
    ticket_id: int,
    message: str = Query(..., min_length=1),
    admin=Depends(get_current_admin),
):
    """پاسخ مدیر به تیکت"""
    from apps.tickets.models import TicketMessage

    try:
        ticket = Ticket.objects.get(pk=ticket_id)
    except Ticket.DoesNotExist:
        raise HTTPException(status_code=404, detail='تیکت یافت نشد')

    TicketMessage.objects.create(ticket=ticket, sender=admin, message=message)
    ticket.status = 'ANSWERED'
    ticket.save(update_fields=['status', 'updated_at'])

    Notification.objects.create(
        user=ticket.user,
        title=f'پاسخ به تیکت: {ticket.subject}',
        message=message[:200],
        type='INFO',
    )

    return {'message': 'پاسخ ارسال شد'}


# ──────────── Reviews ────────────

@router.get('/reviews')
def list_all_reviews(
    status_val: str = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    admin=Depends(get_current_admin),
):
    """لیست نظرات"""
    from apps.reviews.models import Review
    qs = Review.objects.select_related('student', 'course')
    if status_val:
        qs = qs.filter(status=status_val)

    total = qs.count()
    pages = math.ceil(total / page_size) if total > 0 else 1
    offset = (page - 1) * page_size
    reviews = qs[offset:offset + page_size]

    return {
        'items': [{
            'id': r.id, 'student': r.student.full_name, 'course': r.course.title,
            'rating': r.rating, 'comment': r.comment, 'status': r.status,
            'created_at': r.created_at.isoformat(),
        } for r in reviews],
        'total': total, 'page': page, 'pages': pages,
    }


@router.put('/reviews/{review_id}/approve')
def approve_review(review_id: int, admin=Depends(get_current_admin)):
    """تأیید نظر"""
    from apps.reviews.models import Review
    try:
        review = Review.objects.get(pk=review_id)
    except Review.DoesNotExist:
        raise HTTPException(status_code=404, detail='نظر یافت نشد')

    review.status = 'APPROVED'
    review.save(update_fields=['status'])
    return {'message': 'نظر تأیید شد'}


@router.put('/reviews/{review_id}/reject')
def reject_review(review_id: int, admin=Depends(get_current_admin)):
    """رد نظر"""
    from apps.reviews.models import Review
    try:
        review = Review.objects.get(pk=review_id)
    except Review.DoesNotExist:
        raise HTTPException(status_code=404, detail='نظر یافت نشد')

    review.status = 'REJECTED'
    review.save(update_fields=['status'])
    return {'message': 'نظر رد شد'}


# ──────────── Courses Admin ────────────

@router.get('/courses')
def admin_list_courses(admin=Depends(get_current_admin)):
    from routers.v1.courses import serialize_course
    return [dict(serialize_course(course).model_dump(), status=course.status,
                 is_published=course.is_published)
            for course in Course.objects.select_related('instructor', 'category').all()]

@router.post('/courses', status_code=201)
def admin_create_course(
    title: str = Query(...),
    slug: str = Query(...),
    short_description: str = Query(...),
    course_type: str = Query(...),
    price: int = Query(...),
    instructor_id: int = Query(...),
    admin=Depends(get_current_admin),
):
    """ایجاد دوره"""
    try:
        from apps.courses.models import Instructor
        instructor = Instructor.objects.get(pk=instructor_id)
    except:
        raise HTTPException(status_code=404, detail='مدرس یافت نشد')

    course = Course.objects.create(
        title=title, slug=slug, short_description=short_description,
        course_type=course_type, price=price, instructor=instructor,
    )
    return {'message': 'دوره ایجاد شد', 'id': course.id}
