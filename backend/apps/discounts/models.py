from django.db import models
from django.utils import timezone


class Coupon(models.Model):
    """Discount coupon code."""

    TYPE_CHOICES = [
        ('PERCENTAGE', 'درصدی'),
        ('FIXED', 'مبلغ ثابت'),
    ]

    code = models.CharField('کد تخفیف', max_length=50, unique=True, db_index=True)
    discount_type = models.CharField('نوع تخفیف', max_length=12, choices=TYPE_CHOICES)
    discount_value = models.DecimalField('مقدار تخفیف', max_digits=12, decimal_places=0)
    start_date = models.DateTimeField('تاریخ شروع')
    end_date = models.DateTimeField('تاریخ پایان')
    max_uses = models.PositiveIntegerField('حداکثر تعداد استفاده', default=0, help_text='0 = بدون محدودیت')
    used_count = models.PositiveIntegerField('تعداد استفاده شده', default=0)
    applicable_courses = models.ManyToManyField(
        'courses.Course',
        blank=True,
        related_name='coupons',
        verbose_name='دوره‌های مجاز',
    )
    is_active = models.BooleanField('فعال', default=True, db_index=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'کد تخفیف'
        verbose_name_plural = 'کدهای تخفیف'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.code} - {self.get_discount_display()}'

    def get_discount_display(self):
        if self.discount_type == 'PERCENTAGE':
            return f'{self.discount_value}%'
        return f'{self.discount_value} تومان'

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.start_date:
            return False
        if now > self.end_date:
            return False
        if self.max_uses > 0 and self.used_count >= self.max_uses:
            return False
        return True

    def is_valid_for_course(self, course):
        if not self.applicable_courses.exists():
            return True
        return self.applicable_courses.filter(pk=course.pk).exists()

    def calculate_discount(self, subtotal):
        """Calculate discount amount for the given subtotal."""
        if not self.is_valid:
            return 0
        if self.discount_type == 'PERCENTAGE':
            discount = subtotal * (self.discount_value / 100)
            return min(discount, subtotal)
        else:
            return min(self.discount_value, subtotal)

    def use(self):
        """Increment the used count."""
        self.used_count += 1
        self.save(update_fields=['used_count'])
