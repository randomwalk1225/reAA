# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('measurement', '0008_add_analysis_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='measurementsession',
            name='latitude',
            field=models.FloatField(blank=True, null=True, verbose_name='위도'),
        ),
        migrations.AddField(
            model_name='measurementsession',
            name='longitude',
            field=models.FloatField(blank=True, null=True, verbose_name='경도'),
        ),
        migrations.AddField(
            model_name='measurementsession',
            name='ph',
            field=models.FloatField(blank=True, null=True, verbose_name='PH'),
        ),
        migrations.AddField(
            model_name='measurementsession',
            name='orp',
            field=models.FloatField(blank=True, null=True, verbose_name='ORP'),
        ),
        migrations.AddField(
            model_name='measurementsession',
            name='water_temp',
            field=models.FloatField(blank=True, null=True, verbose_name='수온(℃)'),
        ),
        migrations.AddField(
            model_name='measurementsession',
            name='ec',
            field=models.FloatField(blank=True, null=True, verbose_name='EC(μS/cm)'),
        ),
        migrations.AddField(
            model_name='measurementsession',
            name='tds',
            field=models.FloatField(blank=True, null=True, verbose_name='TDS(mg/L)'),
        ),
    ]
