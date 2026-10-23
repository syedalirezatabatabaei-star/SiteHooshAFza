from django.db import models
from django.conf import settings


class Review(models.Model):
    """Course review."""

    STATUS_CHOICES = [
        ('PENDING', 'در انتظار تأیید'),
        ('APPROVED', 'تأیید شده'),
        ('REJECTED', 'رد شده'),
    ]

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='دوره',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='دانشجو',
    )
    rating = models.PositiveSmallIntegerField('امتیاز')
    comment = models.TextField('نظر')
    status = models.CharField(
        'وضعیت',
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
        db_index=True,
    )
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'نظر'
        verbose_name_plural = 'نظرات'
        unique_together = ['course', 'student']
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.student} - {self.course} ({self.rating})'

    def save(self, *args, **kwargs):
        if self.rating < 1 or self.rating > 5:
            raise ValueError('امتیاز باید بین ۱ تا ۵ باشد')
        super().save(*args, **kwargs)
