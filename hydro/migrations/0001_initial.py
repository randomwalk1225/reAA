# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ETQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location_name', models.CharField(blank=True, max_length=100, verbose_name='지점명')),
                ('latitude', models.FloatField(verbose_name='위도')),
                ('longitude', models.FloatField(verbose_name='경도')),
                ('query_date', models.DateField(blank=True, null=True, verbose_name='조회 날짜')),
                ('et0', models.FloatField(default=5.0, verbose_name='기준증발산량(mm/day)')),
                ('ndvi', models.FloatField(blank=True, null=True, verbose_name='NDVI')),
                ('ndmi', models.FloatField(blank=True, null=True, verbose_name='NDMI')),
                ('ndwi', models.FloatField(blank=True, null=True, verbose_name='NDWI')),
                ('kc', models.FloatField(blank=True, null=True, verbose_name='작물계수(Kc)')),
                ('et_actual', models.FloatField(blank=True, null=True, verbose_name='실제증발산량(mm/day)')),
                ('soil_moisture', models.FloatField(blank=True, null=True, verbose_name='토양수분지수')),
                ('stress_index', models.FloatField(blank=True, null=True, verbose_name='수분스트레스지수')),
                ('raw_response', models.JSONField(blank=True, default=dict, verbose_name='원본 응답')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='조회일시')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='et_queries', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '증발산량 조회',
                'verbose_name_plural': '증발산량 조회',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='etquery',
            index=models.Index(fields=['user', '-created_at'], name='hydro_etque_user_id_abc123_idx'),
        ),
        migrations.CreateModel(
            name='WaterLevelQuery',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('station_code', models.CharField(max_length=20, verbose_name='관측소 코드')),
                ('station_name', models.CharField(max_length=100, verbose_name='관측소명')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='시작일')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='종료일')),
                ('water_level', models.FloatField(blank=True, null=True, verbose_name='수위(m)')),
                ('flow_rate', models.FloatField(blank=True, null=True, verbose_name='유량(m³/s)')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='조회일시')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='waterlevel_queries', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '수위 조회',
                'verbose_name_plural': '수위 조회',
                'ordering': ['-created_at'],
            },
        ),
    ]
