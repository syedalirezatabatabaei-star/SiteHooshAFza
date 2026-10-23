from django.db import models
from django.conf import settings


class Enrollment(models.Model):
    """Student enrollment in a course."""

    STATUS_CHOICES = [
        ('ACTIVE', 'فعال'),
        ('INACTIVE', 'غیرفعال'),
        ('SUSPENDED', 'معلق'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='دانشجو',
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='دوره',
    )
    status = models.CharField(
        'وضعیت',
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        db_index=True,
    )
    enrolled_at = models.DateTimeField('تاریخ ثبت‌نام', auto_now_add=True)
    access_start = models.DateTimeField('شروع دسترسی', null=True)
    access_end = models.DateTimeField('پایان دسترسی', null=True, blank=True)
    progress = models.DecimalField('پیشرفت', max_digits=5, decimal_places=2, default=0)
    last_lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+',
        verbose_name='آخرین جلسه مشاهده شده',
    )

    class Meta:
        verbose_name = 'ثبت‌نام'
        verbose_name_plural = 'ثبت‌نام‌ها'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.student} - {self.course}'

    @property
    def is_access_valid(self):
        from django.utils import timezone
        now = timezone.now()
        if self.status != 'ACTIVE':
            return False
        if self.access_start and now < self.access_start:
            return False
        if self.access_end and now > self.access_end:
            return False
        return True

    def calculate_progress(self):
        """Calculate progress based on completed lessons."""
        total = self.course.total_lessons
        if total == 0:
            return 0
        from apps.courses.models import Lesson
        from apps.exams.models import ExamAttempt
        completed = ExamAttempt.objects.filter(
            student=self.student,
            exam__course=self.course,
            passed=True,
        ).count()
        return round((completed / total) * 100, 2) if total > 0 else 0
