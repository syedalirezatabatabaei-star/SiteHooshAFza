from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0001_initial'),
        ('orders', '0003_order_coupon_code_orderitem_payment_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='spotplayer_course_id',
            field=models.CharField(blank=True, db_index=True, max_length=100, verbose_name='شناسه دوره در SpotPlayer'),
        ),
        migrations.CreateModel(
            name='SpotPlayerLicense',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_license_id', models.CharField(blank=True, max_length=120, verbose_name='شناسه لایسنس خارجی')),
                ('license_key', models.CharField(blank=True, max_length=500, verbose_name='کد لایسنس')),
                ('license_url', models.CharField(blank=True, max_length=1000, verbose_name='آدرس دریافت لایسنس')),
                ('status', models.CharField(choices=[('PENDING', 'در انتظار صدور'), ('CREATED', 'صادر شده'), ('FAILED', 'ناموفق')], db_index=True, default='PENDING', max_length=10, verbose_name='وضعیت')),
                ('error_message', models.TextField(blank=True, verbose_name='خطا')),
                ('provider_response', models.JSONField(blank=True, default=dict, verbose_name='پاسخ سرویس')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')),
                ('order_item', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='spotplayer_license', to='orders.orderitem', verbose_name='آیتم سفارش')),
            ],
            options={'verbose_name': 'لایسنس SpotPlayer', 'verbose_name_plural': 'لایسنس‌های SpotPlayer', 'ordering': ['-created_at']},
        ),
    ]
