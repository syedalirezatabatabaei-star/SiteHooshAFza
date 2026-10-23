import uuid
from django.db import models
from django.conf import settings


class Certificate(models.Model):
    """Course completion certificate."""

    STATUS_CHOICES = [
        ('PENDING', 'در انتظار صدور'),
        ('ISSUED', 'صادر شده'),
        ('REVOKED', 'لغو شده'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name='دانشجو',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='certificates',
        verbose_name='دوره',
    )
    certificate_number = models.CharField(
        'شماره گواهینامه',
        max_length=50,
        unique=True,
        editable=False,
    )
    issue_date = models.DateField('تاریخ صدور', auto_now_add=True)
    status = models.CharField(
        'وضعیت',
        max_length=10,
        choices=STATUS_CHOICES,
        default='PENDING',
    )
    verification_code = models.CharField(
        'کد تأیید',
        max_length=36,
        unique=True,
        editable=False,
    )
    file = models.FileField(
        'فایل گواهینامه',
        upload_to='certificates/',
        blank=True,
        null=True,
    )

    class Meta:
        verbose_name = 'گواهینامه'
        verbose_name_plural = 'گواهینامه‌ها'
        unique_together = ['student', 'course']
        ordering = ['-issue_date']

    def __str__(self):
        return f'{self.certificate_number} - {self.student} - {self.course}'

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            self.certificate_number = f'HZ-{uuid.uuid4().hex[:8].upper()}'
        if not self.verification_code:
            self.verification_code = str(uuid.uuid4())
        super().save(*args, **kwargs)
