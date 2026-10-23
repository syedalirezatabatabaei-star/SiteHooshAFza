from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='CareerApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('application_type', models.CharField(choices=[('INSTITUTE', 'همکاری با مؤسسه'), ('SUBSIDIARY', 'همکاری با شرکت‌های زیرمجموعه'), ('JOB', 'فرصت شغلی')], db_index=True, max_length=12, verbose_name='نوع درخواست')),
                ('full_name', models.CharField(max_length=180, verbose_name='نام و نام خانوادگی')),
                ('phone', models.CharField(max_length=30, verbose_name='شماره تماس')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='ایمیل')),
                ('organization', models.CharField(blank=True, max_length=200, verbose_name='نام شرکت/مؤسسه')),
                ('position', models.CharField(blank=True, max_length=200, verbose_name='عنوان موقعیت یا زمینه همکاری')),
                ('message', models.TextField(max_length=5000, verbose_name='توضیحات')),
                ('resume_url', models.URLField(blank=True, max_length=1000, verbose_name='لینک رزومه')),
                ('status', models.CharField(choices=[('NEW', 'جدید'), ('REVIEWING', 'در حال بررسی'), ('CONTACTED', 'تماس گرفته شد'), ('REJECTED', 'بسته شده')], db_index=True, default='NEW', max_length=12, verbose_name='وضعیت بررسی')),
                ('admin_notes', models.TextField(blank=True, verbose_name='یادداشت مدیر')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان ثبت')),
            ],
            options={'verbose_name': 'درخواست همکاری/استخدام', 'verbose_name_plural': 'درخواست‌های همکاری/استخدام', 'ordering': ['-created_at']},
        ),
    ]
