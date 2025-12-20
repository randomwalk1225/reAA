# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('measurement', '0001_initial'),
    ]

    operations = [
        # Station에 user 필드 추가
        migrations.AddField(
            model_name='station',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='stations',
                to=settings.AUTH_USER_MODEL,
                verbose_name='소유자'
            ),
        ),
        # RatingCurve에 user 필드 추가
        migrations.AddField(
            model_name='ratingcurve',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='rating_curves',
                to=settings.AUTH_USER_MODEL,
                verbose_name='소유자'
            ),
        ),
        # BaseflowAnalysis에 user 필드 추가
        migrations.AddField(
            model_name='baseflowanalysis',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='baseflow_analyses',
                to=settings.AUTH_USER_MODEL,
                verbose_name='소유자'
            ),
        ),
    ]
