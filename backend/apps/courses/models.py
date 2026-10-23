from django.db import models


class Category(models.Model):
    """Course category with hierarchical structure."""
    name = models.CharField('نام دسته‌بندی', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=200, unique=True, allow_unicode=True)
    description = models.TextField('توضیحات', blank=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='دسته والد',
    )
    order = models.PositiveIntegerField('ترتیب', default=0)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'دسته‌بندی'
        verbose_name_plural = 'دسته‌بندی‌ها'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Instructor(models.Model):
    """Instructor profile."""
    name = models.CharField('نام', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=200, unique=True, allow_unicode=True)
    profile_image = models.ImageField('عکس پروفایل', upload_to='instructors/')
    bio = models.TextField('بیوگرافی')
    specialization = models.CharField('تخصص', max_length=300)
    education = models.TextField('تحصیلات', blank=True)
    experience = models.TextField('تجربه کاری', blank=True)
    social_links = models.JSONField('لینک‌های اجتماعی', default=dict, blank=True)
    is_active = models.BooleanField('فعال', default=True)

    class Meta:
        verbose_name = 'مدرس'
        verbose_name_plural = 'مدرسین'
        ordering = ['name']

    def __str__(self):
        return self.name


class Course(models.Model):
    """Main course model for both in-person and recorded courses."""

    TYPE_CHOICES = [
        ('IN_PERSON', 'حضوری'),
        ('RECORDED', 'ضبط‌شده'),
    ]
    STATUS_CHOICES = [
        ('DRAFT', 'پیش‌نویس'),
        ('PUBLISHED', 'منتشر شده'),
        ('ARCHIVED', 'بایگانی شده'),
    ]

    title = models.CharField('عنوان', max_length=300)
    slug = models.SlugField('اسلاگ', max_length=300, unique=True, allow_unicode=True)
    short_description = models.CharField('توضیح کوتاه', max_length=500)
    description = models.TextField('توضیحات کامل')
    thumbnail = models.ImageField('تصویر بندانگشتی', upload_to='courses/thumbnails/')
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name='مدرس',
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='دسته‌بندی',
    )
    course_type = models.CharField('نوع دوره', max_length=12, choices=TYPE_CHOICES, db_index=True)
    price = models.DecimalField('قیمت (تومان)', max_digits=12, decimal_places=0)
    status = models.CharField(
        'وضعیت',
        max_length=10,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True,
    )
    is_published = models.BooleanField('منتشر شده', default=False, db_index=True)
    # External SpotPlayer course/package ID configured by an administrator.
    spotplayer_course_id = models.CharField(
        'شناسه دوره در SpotPlayer', max_length=100, blank=True, db_index=True,
    )

    # SEO
    meta_title = models.CharField('عنوان متا', max_length=200, blank=True)
    meta_description = models.CharField('توضیحات متا', max_length=300, blank=True)

    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ به‌روزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'دوره'
        verbose_name_plural = 'دوره‌ها'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_in_person(self):
        return self.course_type == 'IN_PERSON'

    @property
    def is_recorded(self):
        return self.course_type == 'RECORDED'

    @property
    def total_lessons(self):
        if self.is_recorded:
            return Lesson.objects.filter(chapter__course=self).count()
        return 0

    @property
    def average_rating(self):
        from apps.reviews.models import Review
        reviews = Review.objects.filter(course=self, status='APPROVED')
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0

    @property
    def review_count(self):
        from apps.reviews.models import Review
        return Review.objects.filter(course=self, status='APPROVED').count()

    @property
    def enrolled_count(self):
        from apps.enrollments.models import Enrollment
        return Enrollment.objects.filter(course=self, status='ACTIVE').count()


class CourseSchedule(models.Model):
    """Weekly schedule for in-person courses."""

    DAY_CHOICES = [
        ('SATURDAY', 'شنبه'),
        ('SUNDAY', 'یکشنبه'),
        ('MONDAY', 'دوشنبه'),
        ('TUESDAY', 'سه‌شنبه'),
        ('WEDNESDAY', 'چهارشنبه'),
        ('THURSDAY', 'پنجشنبه'),
        ('FRIDAY', 'جمعه'),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='schedules',
        verbose_name='دوره',
    )
    day_of_week = models.CharField('روز هفته', max_length=10, choices=DAY_CHOICES)
    start_time = models.TimeField('ساعت شروع')
    end_time = models.TimeField('ساعت پایان')

    class Meta:
        verbose_name = 'برنامه هفتگی'
        verbose_name_plural = 'برنامه‌های هفتگی'
        unique_together = ['course', 'day_of_week']
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f'{self.course.title} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}'


class InPersonDetail(models.Model):
    """Additional details for in-person courses."""

    course = models.OneToOneField(
        Course,
        on_delete=models.CASCADE,
        related_name='inperson_detail',
        verbose_name='دوره',
    )
    prepayment_amount = models.DecimalField('مبلغ پیش‌پرداخت (تومان)', max_digits=12, decimal_places=0)
    remaining_amount = models.DecimalField('مبلغ باقی‌مانده (تومان)', max_digits=12, decimal_places=0)
    capacity = models.PositiveIntegerField('ظرفیت')
    start_date = models.DateField('تاریخ شروع')
    end_date = models.DateField('تاریخ پایان')
    location = models.CharField('محل برگزاری', max_length=500)

    class Meta:
        verbose_name = 'جزئیات دوره حضوری'
        verbose_name_plural = 'جزئیات دوره‌های حضوری'

    def __str__(self):
        return f'جزئیات حضوری: {self.course.title}'

    @property
    def is_full(self):
        return self.course.enrolled_count >= self.capacity

    @property
    def available_capacity(self):
        return max(0, self.capacity - self.course.enrolled_count)


class Chapter(models.Model):
    """Chapter for recorded courses."""

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='chapters',
        verbose_name='دوره',
    )
    title = models.CharField('عنوان فصل', max_length=300)
    order = models.PositiveIntegerField('ترتیب', default=0)
    is_published = models.BooleanField('منتشر شده', default=True)

    class Meta:
        verbose_name = 'فصل'
        verbose_name_plural = 'فصل‌ها'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.course.title} - {self.title}'

    @property
    def total_lessons(self):
        return self.lessons.count()


class Lesson(models.Model):
    """Individual lesson in a chapter (recorded courses)."""

    chapter = models.ForeignKey(
        Chapter,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='فصل',
    )
    title = models.CharField('عنوان جلسه', max_length=300)
    description = models.TextField('توضیحات', blank=True)
    duration = models.PositiveIntegerField('مدت زمان (دقیقه)')
    order = models.PositiveIntegerField('ترتیب', default=0)
    spotplayer_id = models.CharField('شناسه SpotPlayer', max_length=100, blank=True)
    is_preview = models.BooleanField('پیش‌نمایش رایگان', default=False)
    is_published = models.BooleanField('منتشر شده', default=True)

    class Meta:
        verbose_name = 'جلسه'
        verbose_name_plural = 'جلسات'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.chapter.course.title} - {self.title}'

    @property
    def total_lessons_in_course(self):
        return Lesson.objects.filter(chapter__course=self.chapter.course).count()



class SpotPlayerLicense(models.Model):
    """SpotPlayer license issued for a paid order item."""

    STATUS_CHOICES = [
        ('PENDING', 'در انتظار صدور'),
        ('CREATED', 'صادر شده'),
        ('FAILED', 'ناموفق'),
    ]

    order_item = models.OneToOneField(
        'orders.OrderItem', on_delete=models.CASCADE,
        related_name='spotplayer_license', verbose_name='آیتم سفارش',
    )
    external_license_id = models.CharField('شناسه لایسنس خارجی', max_length=120, blank=True)
    license_key = models.CharField('کد لایسنس', max_length=500, blank=True)
    license_url = models.URLField('آدرس دریافت لایسنس', max_length=1000, blank=True)
    status = models.CharField('وضعیت', max_length=10, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    error_message = models.TextField('خطا', blank=True)
    provider_response = models.JSONField('پاسخ سرویس', default=dict, blank=True)
    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ به‌روزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'لایسنس SpotPlayer'
        verbose_name_plural = 'لایسنس‌های SpotPlayer'
        ordering = ['-created_at']

    def __str__(self):
        return f'SpotPlayer license for order item #{self.order_item_id}'
