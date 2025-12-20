from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class UserActivity(models.Model):
    """사용자 활동 로그 - 모든 사용자 활동 추적"""
    ACTION_TYPES = [
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
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='사용자'
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name='활동 유형'
    )
    action_detail = models.CharField(
        max_length=200,
        verbose_name='상세 내용'
    )

    # 관련 객체 (Generic Foreign Key) - 어떤 모델과 관련된 활동인지
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='관련 모델'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True, verbose_name='관련 객체 ID')
    content_object = GenericForeignKey('content_type', 'object_id')

    # 메타데이터
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name='IP 주소')
    user_agent = models.TextField(blank=True, verbose_name='User Agent')
    extra_data = models.JSONField(default=dict, blank=True, verbose_name='추가 데이터')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')

    class Meta:
        verbose_name = '사용자 활동'
        verbose_name_plural = '사용자 활동'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_action_type_display()} - {self.action_detail}"
