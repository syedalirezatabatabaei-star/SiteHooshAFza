from fastapi import APIRouter, Depends, HTTPException, status

from deps import get_current_user
from schemas.v1.cart import CartResponse, CartAddRequest, CartItemResponse, CartCouponRequest
from apps.orders.models import Cart, CartItem
from apps.courses.models import Course
from apps.discounts.models import Coupon

router = APIRouter()


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user, status='ACTIVE')
    return cart


def serialize_cart(cart) -> CartResponse:
    items = []
    for item in cart.items.select_related('course').all():
        items.append(CartItemResponse(
            id=item.id,
            course_id=item.course.id,
            course_title=item.course.title,
            course_slug=item.course.slug,
            course_thumbnail=item.course.thumbnail.url if item.course.thumbnail else None,
            course_price=(item.course.inperson_detail.prepayment_amount
                          if item.course.is_in_person and hasattr(item.course, 'inperson_detail')
                          else item.course.price),
            course_type=item.course.course_type,
            added_at=item.added_at,
        ))

    return CartResponse(
        id=cart.id,
        items=items,
        subtotal=cart.subtotal,
        discount=cart.discount_amount,
        total=cart.total,
        coupon_code=cart.coupon.code if cart.coupon else None,
    )


@router.get('', response_model=CartResponse)
def get_cart(user=Depends(get_current_user)):
    """دریافت سبد خرید"""
    cart = get_or_create_cart(user)
    return serialize_cart(cart)


@router.post('/items', status_code=status.HTTP_201_CREATED)
def add_to_cart(
    data: CartAddRequest,
    user=Depends(get_current_user),
):
    """افزودن دوره به سبد خرید"""
    try:
        course = Course.objects.get(pk=data.course_id, status='PUBLISHED', is_published=True)
    except Course.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='دوره یافت نشد')

    cart = get_or_create_cart(user)

    if cart.items.filter(course=course).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='این دوره قبلاً به سبد خرید اضافه شده است',
        )

    # Check capacity for in-person courses
    if course.is_in_person and hasattr(course, 'inperson_detail'):
        if course.inperson_detail.is_full:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='ظرفیت دوره تکمیل شده است',
            )

    # Check if already enrolled
    from apps.enrollments.models import Enrollment
    if Enrollment.objects.filter(student=user, course=course, status='ACTIVE').exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='شما قبلاً در این دوره ثبت‌نام کرده‌اید',
        )

    CartItem.objects.create(cart=cart, course=course)
    return {'message': 'دوره به سبد خرید اضافه شد'}


@router.delete('/items/{item_id}')
def remove_from_cart(
    item_id: int,
    user=Depends(get_current_user),
):
    """حذف دوره از سبد خرید"""
    cart = get_or_create_cart(user)
    try:
        item = CartItem.objects.get(pk=item_id, cart=cart)
    except CartItem.DoesNotExist:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='آیتم یافت نشد')

    item.delete()
    return {'message': 'دوره از سبد خرید حذف شد'}


@router.post('/coupon')
def apply_coupon(
    data: CartCouponRequest,
    user=Depends(get_current_user),
):
    """اعمال کد تخفیف"""
    cart = get_or_create_cart(user)

    try:
        coupon = Coupon.objects.get(code__iexact=data.code)
    except Coupon.DoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='کد تخفیف معتبر نیست',
        )

    if not coupon.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='تاریخ اعتبار یا تعداد استفاده کد تخفیف تمام شده است',
        )

    # Check course applicability
    cart_courses = [item.course for item in cart.items.all()]
    for course in cart_courses:
        if not coupon.is_valid_for_course(course):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'کد تخفیف برای دوره {course.title} معتبر نیست',
            )

    cart.coupon = coupon
    cart.save(update_fields=['coupon'])

    return {
        'message': 'کد تخفیف اعمال شد',
        'discount': str(cart.discount_amount),
        'total': str(cart.total),
    }


@router.delete('/coupon')
def remove_coupon(user=Depends(get_current_user)):
    """حذف کد تخفیف"""
    cart = get_or_create_cart(user)
    cart.coupon = None
    cart.save(update_fields=['coupon'])
    return {'message': 'کد تخفیف حذف شد'}
