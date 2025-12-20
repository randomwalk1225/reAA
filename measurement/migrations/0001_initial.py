# Generated manually
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Station',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='지점명')),
                ('river_name', models.CharField(blank=True, max_length=100, verbose_name='하천명')),
                ('dm_number', models.CharField(blank=True, max_length=50, verbose_name='DM번호')),
                ('description', models.TextField(blank=True, verbose_name='설명')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': '관측소',
                'verbose_name_plural': '관측소',
            },
        ),
        migrations.CreateModel(
            name='RatingCurve',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(verbose_name='연도')),
                ('curve_type', models.CharField(choices=[('open', '방류(Open)'), ('close', '저류(Close)')], default='open', max_length=10, verbose_name='곡선유형')),
                ('h_min', models.FloatField(verbose_name='최소수위(m)')),
                ('h_max', models.FloatField(verbose_name='최대수위(m)')),
                ('coef_a', models.FloatField(verbose_name='계수 a')),
                ('coef_b', models.FloatField(verbose_name='지수 b')),
                ('coef_h0', models.FloatField(default=0, verbose_name='영점수위 h0')),
                ('r_squared', models.FloatField(blank=True, null=True, verbose_name='결정계수(R²)')),
                ('rmse', models.FloatField(blank=True, null=True, verbose_name='RMSE')),
                ('note', models.TextField(blank=True, verbose_name='비고')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rating_curves', to='measurement.station', verbose_name='관측소')),
            ],
            options={
                'verbose_name': '수위-유량곡선',
                'verbose_name_plural': '수위-유량곡선',
                'ordering': ['-year', 'curve_type'],
            },
        ),
        migrations.CreateModel(
            name='HQDataPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('measured_date', models.DateField(verbose_name='측정일')),
                ('stage', models.FloatField(verbose_name='수위(m)')),
                ('discharge', models.FloatField(verbose_name='유량(m³/s)')),
                ('measurement_method', models.CharField(blank=True, max_length=50, verbose_name='측정방법')),
                ('note', models.TextField(blank=True, verbose_name='비고')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hq_data', to='measurement.station', verbose_name='관측소')),
                ('rating_curve', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='data_points', to='measurement.ratingcurve', verbose_name='적용곡선')),
            ],
            options={
                'verbose_name': '수위-유량 데이터',
                'verbose_name_plural': '수위-유량 데이터',
                'ordering': ['-measured_date'],
            },
        ),
        migrations.CreateModel(
            name='WaterLevelTimeSeries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='측정시각')),
                ('stage', models.FloatField(verbose_name='수위(m)')),
                ('quality_flag', models.CharField(choices=[('good', '정상'), ('suspect', '의심'), ('missing', '결측'), ('estimated', '추정')], default='good', max_length=10, verbose_name='품질플래그')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='water_levels', to='measurement.station', verbose_name='관측소')),
            ],
            options={
                'verbose_name': '수위 시계열',
                'verbose_name_plural': '수위 시계열',
                'ordering': ['-timestamp'],
                'unique_together': {('station', 'timestamp')},
            },
        ),
        migrations.AddIndex(
            model_name='waterleveltimeseries',
            index=models.Index(fields=['station', 'timestamp'], name='measurement_station_10833b_idx'),
        ),
        migrations.CreateModel(
            name='DischargeTimeSeries',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(verbose_name='시각')),
                ('stage', models.FloatField(verbose_name='수위(m)')),
                ('discharge', models.FloatField(verbose_name='유량(m³/s)')),
                ('quality_flag', models.CharField(choices=[('good', '정상'), ('extrapolated', '외삽'), ('suspect', '의심')], default='good', max_length=15, verbose_name='품질플래그')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discharges', to='measurement.station', verbose_name='관측소')),
                ('rating_curve', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='discharge_series', to='measurement.ratingcurve', verbose_name='적용곡선')),
            ],
            options={
                'verbose_name': '유량 시계열',
                'verbose_name_plural': '유량 시계열',
                'ordering': ['-timestamp'],
                'unique_together': {('station', 'timestamp')},
            },
        ),
        migrations.AddIndex(
            model_name='dischargetimeseries',
            index=models.Index(fields=['station', 'timestamp'], name='measurement_station_a1b2c3_idx'),
        ),
        migrations.CreateModel(
            name='BaseflowAnalysis',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField(verbose_name='시작일')),
                ('end_date', models.DateField(verbose_name='종료일')),
                ('method', models.CharField(choices=[('lyne_hollick', 'Lyne-Hollick 필터'), ('eckhardt', 'Eckhardt 필터'), ('fixed_interval', '고정간격법'), ('local_minimum', '국부최소법'), ('sliding_interval', '이동간격법')], max_length=20, verbose_name='분석방법')),
                ('alpha', models.FloatField(default=0.925, verbose_name='필터계수(α)')),
                ('bfi_max', models.FloatField(blank=True, default=0.80, null=True, verbose_name='최대BFI')),
                ('total_runoff', models.FloatField(blank=True, null=True, verbose_name='총유출량(mm)')),
                ('baseflow', models.FloatField(blank=True, null=True, verbose_name='기저유출량(mm)')),
                ('direct_runoff', models.FloatField(blank=True, null=True, verbose_name='직접유출량(mm)')),
                ('bfi', models.FloatField(blank=True, null=True, verbose_name='기저유출지수(BFI)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(blank=True, verbose_name='비고')),
                ('station', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='baseflow_analyses', to='measurement.station', verbose_name='관측소')),
            ],
            options={
                'verbose_name': '기저유출 분석',
                'verbose_name_plural': '기저유출 분석',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='BaseflowDaily',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='날짜')),
                ('total_discharge', models.FloatField(verbose_name='총유량(m³/s)')),
                ('baseflow', models.FloatField(verbose_name='기저유출(m³/s)')),
                ('direct_runoff', models.FloatField(verbose_name='직접유출(m³/s)')),
                ('analysis', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='daily_results', to='measurement.baseflowanalysis', verbose_name='분석')),
            ],
            options={
                'verbose_name': '일별 기저유출',
                'verbose_name_plural': '일별 기저유출',
                'ordering': ['date'],
                'unique_together': {('analysis', 'date')},
            },
        ),
    ]
