from django.db import models
from django.conf import settings


class Notification(models.Model):
    """User notification."""

    TYPE_CHOICES = [
        ('INFO', 'اطلاعات'),
        ('WARNING', 'هشدار'),
        ('SUCCESS', 'موفقیت'),
        ('ERROR', 'خطا'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='کاربر',
    )
    title = models.CharField('عنوان', max_length=200)
    message = models.TextField('پیام')
    type = models.CharField('نوع', max_length=10, choices=TYPE_CHOICES, default='INFO')
    is_read = models.BooleanField('خوانده شده', default=False, db_index=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'اعلان'
        verbose_name_plural = 'اعلان‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.user})'
