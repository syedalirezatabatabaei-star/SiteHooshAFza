from django.db import models
from django.conf import settings


class BlogCategory(models.Model):
    """Blog article category."""

    name = models.CharField('نام دسته‌بندی', max_length=200)
    slug = models.SlugField('اسلاگ', max_length=200, unique=True, allow_unicode=True)
    description = models.TextField('توضیحات', blank=True)

    class Meta:
        verbose_name = 'دسته‌بندی مقاله'
        verbose_name_plural = 'دسته‌بندی مقالات'
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Blog tag."""

    name = models.CharField('نام برچسب', max_length=100)
    slug = models.SlugField('اسلاگ', max_length=100, unique=True, allow_unicode=True)

    class Meta:
        verbose_name = 'برچسب'
        verbose_name_plural = 'برچسب‌ها'
        ordering = ['name']

    def __str__(self):
        return self.name


class Article(models.Model):
    """Blog article with full SEO support."""

    STATUS_CHOICES = [
        ('DRAFT', 'پیش‌نویس'),
        ('PUBLISHED', 'منتشر شده'),
        ('ARCHIVED', 'بایگانی شده'),
    ]

    title = models.CharField('عنوان', max_length=300)
    slug = models.SlugField('اسلاگ', max_length=300, unique=True, allow_unicode=True)
    excerpt = models.TextField('خلاصه', max_length=500)
    content = models.TextField('محتوا')
    featured_image = models.ImageField('تصویر شاخص', upload_to='blog/images/')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name='نویسنده',
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name='دسته‌بندی',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='articles', verbose_name='برچسب‌ها')
    published_at = models.DateTimeField('تاریخ انتشار', null=True, blank=True)
    status = models.CharField(
        'وضعیت',
        max_length=10,
        choices=STATUS_CHOICES,
        default='DRAFT',
        db_index=True,
    )

    # SEO fields
    meta_title = models.CharField('عنوان متا', max_length=200, blank=True)
    meta_description = models.CharField('توضیحات متا', max_length=300, blank=True)
    canonical_url = models.URLField('لینک کاننیکال', blank=True)
    og_title = models.CharField('عنوان Open Graph', max_length=200, blank=True)
    og_description = models.CharField('توضیحات Open Graph', max_length=300, blank=True)
    view_count = models.PositiveIntegerField('تعداد بازدید', default=0)

    created_at = models.DateTimeField('تاریخ ایجاد', auto_now_add=True)
    updated_at = models.DateTimeField('تاریخ به‌روزرسانی', auto_now=True)

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title
