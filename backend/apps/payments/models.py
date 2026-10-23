from django.db import models
from django.conf import settings


class Payment(models.Model):
    """Payment record for orders."""

    STATUS_CHOICES = [
        ('PENDING', 'در انتظار'),
        ('SUCCESS', 'موفق'),
        ('FAILED', 'ناموفق'),
        ('CANCELED', 'لغو شده'),
    ]
    GATEWAY_CHOICES = [
        ('ZARINPAL', 'زرین‌پال'),
        ('NEXTPAY', 'نکست‌پی'),
        ('SADAD', 'سداد'),
        ('MANUAL', 'دستی'),
    ]
    TYPE_CHOICES = [
        ('FULL_PAYMENT', 'پرداخت کامل'),
        ('PREPAYMENT', 'پیش‌پرداخت'),
        ('REMAINING', 'باقی‌مانده'),
    ]

    order = models.ForeignKey(
        'orders.Order',
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='سفارش',
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name='کاربر',
    )
    amount = models.DecimalField('مبلغ (تومان)', max_digits=12, decimal_places=0)
    payment_type = models.CharField('نوع پرداخت', max_length=15, choices=TYPE_CHOICES)
    gateway = models.CharField('درگاه پرداخت', max_length=15, choices=GATEWAY_CHOICES, default='MANUAL')
    authority = models.CharField('مرجع درگاه', max_length=100, blank=True)
    transaction_id = models.CharField('شماره تراکنش', max_length=100, blank=True)
    status = models.CharField(
        'وضعیت',
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    paid_at = models.DateTimeField('تاریخ پرداخت', null=True, blank=True)
    extra_data = models.JSONField('اطلاعات اضافی درگاه', default=dict, blank=True)

    class Meta:
        verbose_name = 'پرداخت'
        verbose_name_plural = 'پرداخت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'پرداخت {self.amount} تومان - {self.get_status_display()}'
