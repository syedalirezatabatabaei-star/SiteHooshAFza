from fastapi import APIRouter, Depends, HTTPException, status

from deps import get_current_user
from schemas.v1.orders import OrderResponse, OrderItemResponse, CheckoutResponse
from apps.orders.models import Cart, Order, OrderItem
from apps.payments.models import Payment
from apps.courses.models import InPersonDetail
from django.db import transaction

router = APIRouter()


@router.get('')
def list_orders(user=Depends(get_current_user)):
    """لیست سفارشات کاربر"""
    orders = Order.objects.filter(user=user).prefetch_related('items').order_by('-created_at')
    result = []
    for order in orders:
        items = [
            OrderItemResponse(
                course_id=oi.course_id,
                course_title=oi.course.title,
                course_thumbnail=oi.course.thumbnail.url if oi.course.thumbnail else None,
                price_at_purchase=oi.price_at_purchase,
                payment_type=oi.payment_type,
            ) for oi in order.items.all()
        ]
        result.append(OrderResponse(
            id=order.id,
            total_amount=order.total_amount,
            discount_amount=order.discount_amount,
            final_amount=order.final_amount,
            coupon_code=order.coupon_code,
            status=order.status,
            created_at=order.created_at,
            items=items,
        ))
    return result


@router.get('/{order_id}')
def get_order(order_id: int, user=Depends(get_current_user)):
    """جزئیات سفارش"""
    try:
        order = Order.objects.prefetch_related('items').get(pk=order_id, user=user)
    except Order.DoesNotExist:
        raise HTTPException(status_code=404, detail='سفارش یافت نشد')

    items = [
        OrderItemResponse(
            course_id=oi.course_id,
            course_title=oi.course.title,
            course_thumbnail=oi.course.thumbnail.url if oi.course.thumbnail else None,
            price_at_purchase=oi.price_at_purchase,
            payment_type=oi.payment_type,
        ) for oi in order.items.all()
    ]
    return OrderResponse(
        id=order.id,
        total_amount=order.total_amount,
        discount_amount=order.discount_amount,
        final_amount=order.final_amount,
        coupon_code=order.coupon_code,
        status=order.status,
        created_at=order.created_at,
        items=items,
    )


@router.post('/checkout', response_model=CheckoutResponse)
@transaction.atomic
def checkout(user=Depends(get_current_user)):
    """تسویه سبد خرید و ایجاد سفارش"""
    try:
        cart = Cart.objects.select_for_update().get(user=user, status='ACTIVE')
    except Cart.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='سبد خرید فعالی یافت نشد',
        )

    if not cart.items.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='سبد خرید خالی است',
        )

    with transaction.atomic():
        # Server-side price calculation
        total_amount = 0
        order = Order.objects.create(
            user=user,
            total_amount=0,
            discount_amount=0,
            final_amount=0,
            coupon_code=cart.coupon.code if cart.coupon else '',
            status='PENDING',
        )

        for cart_item in cart.items.select_related('course').all():
            course = cart_item.course
            if not course.is_published or course.status != 'PUBLISHED':
                raise HTTPException(status_code=400, detail='یکی از دوره‌ها دیگر قابل خرید نیست')
            from apps.enrollments.models import Enrollment
            if Enrollment.objects.filter(student=user, course=course, status='ACTIVE').exists():
                raise HTTPException(status_code=400, detail='شما قبلاً در این دوره ثبت‌نام کرده‌اید')
            if course.is_in_person and hasattr(course, 'inperson_detail') and course.inperson_detail.is_full:
                raise HTTPException(status_code=400, detail='ظرفیت دوره تکمیل است')
            # Determine payment type
            if course.is_in_person and hasattr(course, 'inperson_detail'):
                amount = course.inperson_detail.prepayment_amount
                payment_type = 'PREPAYMENT'
            else:
                amount = course.price
                payment_type = 'FULL_PAYMENT'

            OrderItem.objects.create(
                order=order,
                course=course,
                price_at_purchase=amount,
                payment_type=payment_type,
            )
            total_amount += amount

        # Apply coupon discount (server-side calculation)
        discount_amount = 0
        if cart.coupon and cart.coupon.is_valid:
            discount_amount = cart.coupon.calculate_discount(total_amount)
            # Validate all courses are eligible
            for item in order.items.all():
                if not cart.coupon.is_valid_for_course(item.course):
                    discount_amount = 0
                    break

        final_amount = max(0, total_amount - discount_amount)

        order.total_amount = total_amount
        order.discount_amount = discount_amount
        order.final_amount = final_amount
        order.save()

        # Create pending payment
        Payment.objects.create(
            order=order,
            user=user,
            amount=final_amount,
            payment_type='FULL_PAYMENT' if not order.items.filter(payment_type='PREPAYMENT').exists() else 'PREPAYMENT',
            gateway='MANUAL',
        )

        # Mark cart as checked out
        cart.status = 'CHECKED_OUT'
        cart.save(update_fields=['status'])

    return CheckoutResponse(
        order_id=order.id,
        total_amount=order.total_amount,
        discount_amount=order.discount_amount,
        final_amount=order.final_amount,
    )
