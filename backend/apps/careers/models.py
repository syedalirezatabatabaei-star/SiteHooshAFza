from django.db import models


class CareerApplication(models.Model):
    TYPE_CHOICES = [
        ('INSTITUTE', 'همکاری با مؤسسه'),
        ('SUBSIDIARY', 'همکاری با شرکت‌های زیرمجموعه'),
        ('JOB', 'فرصت شغلی'),
    ]
    STATUS_CHOICES = [
        ('NEW', 'جدید'),
        ('REVIEWING', 'در حال بررسی'),
        ('CONTACTED', 'تماس گرفته شد'),
        ('REJECTED', 'بسته شده'),
    ]
    application_type = models.CharField('نوع درخواست', max_length=12, choices=TYPE_CHOICES, db_index=True)
    full_name = models.CharField('نام و نام خانوادگی', max_length=180)
    phone = models.CharField('شماره تماس', max_length=30)
    email = models.EmailField('ایمیل', blank=True)
    organization = models.CharField('نام شرکت/مؤسسه', max_length=200, blank=True)
    position = models.CharField('عنوان موقعیت یا زمینه همکاری', max_length=200, blank=True)
    message = models.TextField('توضیحات', max_length=5000)
    resume_url = models.URLField('لینک رزومه', max_length=1000, blank=True)
    status = models.CharField('وضعیت بررسی', max_length=12, choices=STATUS_CHOICES, default='NEW', db_index=True)
    admin_notes = models.TextField('یادداشت مدیر', blank=True)
    created_at = models.DateTimeField('زمان ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'درخواست همکاری/استخدام'
        verbose_name_plural = 'درخواست‌های همکاری/استخدام'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_application_type_display()} - {self.full_name}'
