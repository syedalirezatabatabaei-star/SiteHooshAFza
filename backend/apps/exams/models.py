from django.db import models
from django.conf import settings


class Exam(models.Model):
    """Exam for a course."""

    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='exams',
        verbose_name='دوره',
    )
    title = models.CharField('عنوان آزمون', max_length=300)
    description = models.TextField('توضیحات', blank=True)
    duration_minutes = models.PositiveIntegerField('مدت زمان (دقیقه)')
    passing_score = models.DecimalField('حد نصاب', max_digits=5, decimal_places=2)
    is_active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)

    class Meta:
        verbose_name = 'آزمون'
        verbose_name_plural = 'آزمون‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.course.title})'

    @property
    def total_score(self):
        return sum(q.score for q in self.questions.all())

    @property
    def question_count(self):
        return self.questions.count()


class Question(models.Model):
    """Question in an exam."""

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='آزمون',
    )
    text = models.TextField('متن سؤال')
    score = models.DecimalField('امتیاز', max_digits=5, decimal_places=2, default=1)
    order = models.PositiveIntegerField('ترتیب', default=0)

    class Meta:
        verbose_name = 'سؤال'
        verbose_name_plural = 'سؤالات'
        ordering = ['order', 'id']

    def __str__(self):
        return f'سؤال {self.order}: {self.text[:50]}'


class Choice(models.Model):
    """Choice for a question."""

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='choices',
        verbose_name='سؤال',
    )
    text = models.CharField('متن گزینه', max_length=500)
    is_correct = models.BooleanField('پاسخ صحیح', default=False)

    class Meta:
        verbose_name = 'گزینه'
        verbose_name_plural = 'گزینه‌ها'

    def __str__(self):
        return self.text


class ExamAttempt(models.Model):
    """A student's attempt at an exam."""

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name='آزمون',
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_attempts',
        verbose_name='دانشجو',
    )
    started_at = models.DateTimeField('تاریخ شروع', auto_now_add=True)
    completed_at = models.DateTimeField('تاریخ پایان', null=True, blank=True)
    score = models.DecimalField('نمره', max_digits=6, decimal_places=2, null=True)
    passed = models.BooleanField('قبول شده', null=True)

    class Meta:
        verbose_name = 'تلاش آزمون'
        verbose_name_plural = 'تلاش‌های آزمون'
        ordering = ['-started_at']

    def __str__(self):
        return f'{self.student} - {self.exam} ({self.score})'

    @property
    def is_expired(self):
        from django.utils import timezone
        if self.completed_at:
            return True
        elapsed = (timezone.now() - self.started_at).total_seconds() / 60
        return elapsed > self.exam.duration_minutes


class ExamAnswer(models.Model):
    """Student's answer to a question."""

    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='تلاش',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='سؤال',
    )
    choice = models.ForeignKey(
        Choice,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='گزینه انتخاب شده',
    )

    class Meta:
        verbose_name = 'پاسخ'
        verbose_name_plural = 'پاسخ‌ها'
        unique_together = ['attempt', 'question']

    def __str__(self):
        return f'{self.question} -> {self.choice}'
