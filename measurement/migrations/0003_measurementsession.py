# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('measurement', '0002_add_user_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasurementSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_name', models.CharField(blank=True, max_length=100, verbose_name='관측소명')),
                ('measurement_date', models.DateField(blank=True, null=True, verbose_name='측정일')),
                ('session_number', models.PositiveSmallIntegerField(default=1, verbose_name='측정회차')),
                ('rows_data', models.JSONField(default=list, verbose_name='측선 데이터')),
                ('calibration_data', models.JSONField(default=dict, verbose_name='검정계수')),
                ('estimated_discharge', models.FloatField(blank=True, null=True, verbose_name='예상유량(m³/s)')),
                ('total_width', models.FloatField(blank=True, null=True, verbose_name='총폭(m)')),
                ('max_depth', models.FloatField(blank=True, null=True, verbose_name='최대수심(m)')),
                ('total_area', models.FloatField(blank=True, null=True, verbose_name='단면적(m²)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='수정일시')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='measurement_sessions', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '측정 세션',
                'verbose_name_plural': '측정 세션',
                'ordering': ['-updated_at'],
            },
        ),
        migrations.AddIndex(
            model_name='measurementsession',
            index=models.Index(fields=['user', '-updated_at'], name='measurement_user_id_session_idx'),
        ),
    ]
