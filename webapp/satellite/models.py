from django.db import models


class SatelliteFrame(models.Model):
    """Himawari-9 위성 영상 프레임 메타데이터"""

    IMAGE_TYPES = [
        ('INFRARED_FULL', '적외선 (IR)'),
        ('VISIBLE_FULL', '가시광'),
        ('WATERVAPOR', '수증기'),
    ]

    timestamp = models.DateTimeField(unique=True, db_index=True)
    image_type = models.CharField(
        max_length=20,
        choices=IMAGE_TYPES,
        default='INFRARED_FULL'
    )
    base_path = models.CharField(max_length=200)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name = '위성 영상 프레임'
        verbose_name_plural = '위성 영상 프레임'

    def __str__(self):
        return f"Himawari {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    def get_tile_url(self):
        """NICT 타일 URL 반환"""
        return f"https://himawari8.nict.go.jp{self.base_path}_0_0.png"
