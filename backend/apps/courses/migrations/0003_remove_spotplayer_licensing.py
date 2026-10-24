from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('courses', '0002_spotplayer_mapping_and_license'),
    ]

    operations = [
        migrations.DeleteModel(name='SpotPlayerLicense'),
        migrations.RemoveField(
            model_name='course',
            name='spotplayer_course_id',
        ),
        migrations.AlterField(
            model_name='lesson',
            name='spotplayer_id',
            field=models.CharField(
                blank=True,
                max_length=100,
                verbose_name='شناسه ویدئو در SpotPlayer',
            ),
        ),
    ]
