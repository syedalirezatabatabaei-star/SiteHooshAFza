from fastapi import APIRouter, Depends, HTTPException, Query, status
from django.utils import timezone

from deps import get_current_user, get_current_admin
from django.db import transaction
from schemas.v1.payments import PaymentResponse, PaymentInitiateRequest
from apps.payments.models import Payment
from apps.orders.models import Order

router = APIRouter()


def get_gateway(gateway_name=None):
    """Get payment gateway instance based on settings."""
    from django.conf import settings
    gateway_name = gateway_name or getattr(settings, 'PAYMENT_GATEWAY', 'MANUAL')

    if gateway_name == 'ZARINPAL':
        return ZarinpalGateway()
    if gateway_name == 'MANUAL':
        return ManualGateway()
    raise HTTPException(status_code=503, detail='درگاه انتخاب‌شده پشتیبانی نمی‌شود')


class PaymentGatewayInterface:
    def create_payment(self, amount, order_id, callback_url):
        raise NotImplementedError

    def verify_payment(self, authority, amount):
        raise NotImplementedError


class ManualGateway(PaymentGatewayInterface):
    """Manual/placeholder gateway for testing."""
    def create_payment(self, amount, order_id, callback_url):
        return {'authority': f'MANUAL_{order_id}', 'payment_url': None,
                'message': 'پرداخت دستی نیازمند تأیید مدیر است'}

    def verify_payment(self, authority, amount):
        return {'success': False}


class ZarinpalGateway(PaymentGatewayInterface):
    """Zarinpal payment gateway placeholder."""
    def create_payment(self, amount, order_id, callback_url):
        raise HTTPException(status_code=503, detail='اتصال واقعی درگاه زرین‌پال هنوز پیکربندی نشده است')

    def verify_payment(self, authority, amount):
        raise HTTPException(status_code=503, detail='تأیید واقعی درگاه زرین‌پال هنوز پیکربندی نشده است')


@router.post('/initiate')
def initiate_payment(
    data: PaymentInitiateRequest,
    user=Depends(get_current_user),
):
    """آغاز پرداخت"""
    try:
        order = Order.objects.get(pk=data.order_id, user=user, status='PENDING')
    except Order.DoesNotExist:
        raise HTTPException(status_code=404, detail='سفارش یافت نشد')

    gateway = get_gateway()
    from django.conf import settings
    callback_url = getattr(settings, 'PAYMENT_CALLBACK_URL', 'http://localhost/api/v1/payments/callback')

    result = gateway.create_payment(
        amount=int(order.final_amount),
        order_id=order.id,
        callback_url=callback_url,
    )

    # Update payment with authority
    payment = Payment.objects.filter(order=order, status='PENDING').first()
    if payment:
        payment.authority = result.get('authority', '')
        payment.gateway = getattr(settings, 'PAYMENT_GATEWAY', 'MANUAL')
        payment.save(update_fields=['authority', 'gateway'])

    return {
        'payment_url': result.get('payment_url'),
        'authority': result.get('authority'),
        'message': result.get('message'),
    }


@router.get('/callback')
def payment_callback(
    Authority: str = Query(''),
    Status: str = Query(''),
):
    """callback from payment gateway"""
    if Status != 'OK':
        return {'message': 'پرداخت لغو شد', 'success': False}

    try:
        payment = Payment.objects.get(authority=Authority, status='PENDING')
    except Payment.DoesNotExist:
        raise HTTPException(status_code=404, detail='پرداخت یافت نشد')

    if payment.gateway == 'MANUAL':
        raise HTTPException(status_code=403, detail='پرداخت دستی فقط توسط مدیر تأیید می‌شود')
    gateway = get_gateway(payment.gateway)
    result = gateway.verify_payment(
        authority=Authority,
        amount=int(payment.amount),
    )

    if result.get('success'):
        payment.status = 'SUCCESS'
        payment.transaction_id = result.get('transaction_id', '')
        payment.paid_at = timezone.now()
        payment.save()

        # Update order status
        order = payment.order
        order.status = 'PAID'
        order.save(update_fields=['status'])

        # Create enrollment for each course
        from apps.enrollments.models import Enrollment
        from apps.courses.models import InPersonDetail
        for item in order.items.all():
            enrollment, _ = Enrollment.objects.get_or_create(
                student=order.user,
                course=item.course,
                defaults={'status': 'ACTIVE', 'access_start': timezone.now()},
            )

        return {'message': 'پرداخت موفق', 'success': True}
    else:
        payment.status = 'FAILED'
        payment.save(update_fields=['status'])
        return {'message': 'پرداخت ناموفق', 'success': False}


@router.post('/manual-success/{order_id}')
@transaction.atomic
def manual_payment_success(
    order_id: int,
    user=Depends(get_current_admin),
):
    """Manual payment success (for admin testing)"""
    try:
        order = Order.objects.select_for_update().get(pk=order_id, status='PENDING')
    except Order.DoesNotExist:
        raise HTTPException(status_code=404, detail='سفارش یافت نشد')

    payment = Payment.objects.filter(order=order, status='PENDING').first()
    if not payment:
        raise HTTPException(status_code=404, detail='پرداخت در انتظار یافت نشد')

    for item in order.items.select_related('course'):
        if item.course.is_in_person and hasattr(item.course, 'inperson_detail'):
            from apps.courses.models import InPersonDetail
            detail = InPersonDetail.objects.select_for_update().get(course=item.course)
            if detail.is_full:
                raise HTTPException(status_code=400, detail='ظرفیت دوره تکمیل است')

    if order.coupon_code and order.discount_amount > 0:
        from apps.discounts.models import Coupon
        coupon = Coupon.objects.select_for_update().filter(code=order.coupon_code).first()
        if not coupon or not coupon.is_valid:
            raise HTTPException(status_code=400, detail='کد تخفیف سفارش دیگر معتبر نیست')
        coupon.use()

    payment.status = 'SUCCESS'
    payment.transaction_id = f'MANUAL_{timezone.now().timestamp()}'
    payment.paid_at = timezone.now()
    payment.save()

    order.status = 'PAID'
    order.paid_at = payment.paid_at
    order.save(update_fields=['status', 'paid_at'])

    # Create enrollments
    from apps.enrollments.models import Enrollment
    for item in order.items.all():
        Enrollment.objects.get_or_create(
            student=order.user,
            course=item.course,
            defaults={'status': 'ACTIVE', 'access_start': timezone.now()},
        )

    return {'message': 'پرداخت با موفقیت ثبت شد'}


@router.get('')
def payment_history(user=Depends(get_current_user)):
    """تاریخچه پرداخت‌ها"""
    payments = Payment.objects.filter(user=user).order_by('-created_at')
    return [PaymentResponse(
        id=p.id, amount=p.amount, payment_type=p.payment_type,
        gateway=p.gateway, status=p.status, transaction_id=p.transaction_id,
        created_at=p.created_at, paid_at=p.paid_at,
    ) for p in payments]
