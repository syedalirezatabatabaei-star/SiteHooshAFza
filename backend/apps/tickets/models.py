from django.db import models
from django.conf import settings


class Ticket(models.Model):
    """Support ticket."""

    STATUS_CHOICES = [
        ('OPEN', 'باز'),
        ('IN_PROGRESS', 'در حال بررسی'),
        ('ANSWERED', 'پاسخ داده شده'),
        ('CLOSED', 'بسته شده'),
    ]
    PRIORITY_CHOICES = [
        ('LOW', 'کم'),
        ('MEDIUM', 'متوسط'),
        ('HIGH', 'زیاد'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='کاربر',
    )
    subject = models.CharField('موضوع', max_length=300)
    status = models.CharField(
        'وضعیت',
        max_length=12,
        choices=STATUS_CHOICES,
        default='OPEN',
        db_index=True,
    )
    priority = models.CharField(
        'اولویت',
        max_length=6,
        choices=PRIORITY_CHOICES,
        default='MEDIUM',
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ به‌روزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} ({self.user})'


class TicketMessage(models.Model):
    """Message in a ticket."""

    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='تیکت',
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_messages',
        verbose_name='فرستنده',
    )
    message = models.TextField('پیام')
    is_read = models.BooleanField('خوانده شده', default=False)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'پیام تیکت'
        verbose_name_plural = 'پیام‌های تیکت'
        ordering = ['created_at']

    def __str__(self):
        return f'پیام {self.sender} در تیکت {self.ticket}'
