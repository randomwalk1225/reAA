# Generated manually
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('core', '0001_update_site'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserActivity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[
                    ('upload', '파일 업로드'),
                    ('analysis', '분석 실행'),
                    ('export_pdf', 'PDF 내보내기'),
                    ('export_excel', 'Excel 내보내기'),
                    ('export_csv', 'CSV 내보내기'),
                    ('save', '데이터 저장'),
                    ('delete', '데이터 삭제'),
                    ('view', '조회'),
                    ('login', '로그인'),
                    ('logout', '로그아웃'),
                ], max_length=20, verbose_name='활동 유형')),
                ('action_detail', models.CharField(max_length=200, verbose_name='상세 내용')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='관련 객체 ID')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP 주소')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('extra_data', models.JSONField(blank=True, default=dict, verbose_name='추가 데이터')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='contenttypes.contenttype', verbose_name='관련 모델')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
            options={
                'verbose_name': '사용자 활동',
                'verbose_name_plural': '사용자 활동',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='useractivity',
            index=models.Index(fields=['user', '-created_at'], name='core_userac_user_id_abc123_idx'),
        ),
        migrations.AddIndex(
            model_name='useractivity',
            index=models.Index(fields=['action_type', '-created_at'], name='core_userac_action__def456_idx'),
        ),
    ]
