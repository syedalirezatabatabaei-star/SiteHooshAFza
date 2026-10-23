from django.db import models
from django.conf import settings


class Cart(models.Model):
    """Shopping cart for a user."""

    STATUS_CHOICES = [
        ('ACTIVE', 'فعال'),
        ('CHECKED_OUT', 'تسویه شده'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='carts',
        verbose_name='کاربر',
    )
    status = models.CharField(
        'وضعیت',
        max_length=12,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        db_index=True,
    )
    coupon = models.ForeignKey(
        'discounts.Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name='کد تخفیف',
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ به‌روزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'سبد خرید'
        verbose_name_plural = 'سبدهای خرید'
        ordering = ['-created_at']

    def __str__(self):
        return f'سبد خرید {self.user}'

    @property
    def subtotal(self):
        total = 0
        for item in self.items.all():
            if item.course.is_in_person and hasattr(item.course, 'inperson_detail'):
                total += item.course.inperson_detail.prepayment_amount
            else:
                total += item.course.price
        return total

    @property
    def discount_amount(self):
        if not self.coupon:
            return 0
        return self.coupon.calculate_discount(self.subtotal)

    @property
    def total(self):
        return max(0, self.subtotal - self.discount_amount)


class CartItem(models.Model):
    """Individual item in a cart."""

    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سبد خرید',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        verbose_name='دوره',
    )
    added_at = models.DateTimeField('تاریخ افزودن', auto_now_add=True)

    class Meta:
        verbose_name = 'آیتم سبد'
        verbose_name_plural = 'آیتم‌های سبد'
        unique_together = ['cart', 'course']

    def __str__(self):
        return f'{self.course.title}'


class Order(models.Model):
    """Order placed by a user after checkout."""

    STATUS_CHOICES = [
        ('PENDING', 'در انتظار پرداخت'),
        ('PAID', 'پرداخت شده'),
        ('FAILED', 'ناموفق'),
        ('CANCELLED', 'لغو شده'),
        ('COMPLETED', 'اتمام یافته'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name='کاربر',
    )
    status = models.CharField(
        'وضعیت',
        max_length=12,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
    )
    subtotal = models.DecimalField('جمع کل دوره‌ها', max_digits=12, decimal_places=0)
    discount_amount = models.DecimalField(
        'تخفیف', max_digits=12, decimal_places=0, default=0
    )
    total = models.DecimalField('مبلغ نهایی', max_digits=12, decimal_places=0)
    note = models.TextField('یادداشت', blank=True)
    coupon_code = models.CharField('کد تخفیف استفاده‌شده', max_length=50, blank=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ به‌روزرسانی', auto_now=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)

    class Meta:
        verbose_name = 'سفارش'
        verbose_name_plural = 'سفارشات'
        ordering = ['-created_at']

    def __str__(self):
        return f'سفارش #{self.pk} - {self.user}'

    @property
    def is_paid(self):
        return self.status == 'PAID' or self.status == 'COMPLETED'

    # Keep the API's published names compatible with the original DB columns.
    @property
    def total_amount(self):
        return self.subtotal

    @total_amount.setter
    def total_amount(self, value):
        self.subtotal = value

    @property
    def final_amount(self):
        return self.total

    @final_amount.setter
    def final_amount(self, value):
        self.total = value


class OrderItem(models.Model):
    """Individual course in an order."""

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='سفارش',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        verbose_name='دوره',
    )
    price = models.DecimalField('قیمت ', max_digits=12, decimal_places=0)
    payment_type = models.CharField(
        'نوع پرداخت', max_length=15, default='FULL_PAYMENT',
        choices=[('FULL_PAYMENT', 'پرداخت کامل'), ('PREPAYMENT', 'پیش‌پرداخت')],
    )

    @property
    def price_at_purchase(self):
        return self.price

    @price_at_purchase.setter
    def price_at_purchase(self, value):
        self.price = value

    class Meta:
        verbose_name = 'آیتم سفارش'
        verbose_name_plural = 'آیتم‌های سفارش'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.course.title} - {self.price} تومان'
