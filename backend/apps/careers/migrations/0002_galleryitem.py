from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('careers', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='GalleryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='عنوان تصویر')),
                ('image_url', models.URLField(max_length=1000, verbose_name='آدرس تصویر')),
                ('alt_text', models.CharField(blank=True, max_length=250, verbose_name='متن جایگزین')),
                ('caption', models.CharField(blank=True, max_length=500, verbose_name='توضیح تصویر')),
                ('sort_order', models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')),
                ('is_active', models.BooleanField(db_index=True, default=True, verbose_name='نمایش داده شود')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ثبت')),
            ],
            options={'verbose_name': 'تصویر گالری', 'verbose_name_plural': 'گالری تصاویر', 'ordering': ['sort_order', '-created_at']},
        ),
    ]
