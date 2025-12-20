from django.db import models
from django.conf import settings


class ETQuery(models.Model):
    """증발산량(ET) 조회 기록"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='et_queries',
        verbose_name='사용자'
    )

    # 조회 위치
    location_name = models.CharField(max_length=100, blank=True, verbose_name='지점명')
    latitude = models.FloatField(verbose_name='위도')
    longitude = models.FloatField(verbose_name='경도')

    # 조회 파라미터
    query_date = models.DateField(null=True, blank=True, verbose_name='조회 날짜')
    et0 = models.FloatField(default=5.0, verbose_name='기준증발산량(mm/day)')

    # 결과 - 식생지수
    ndvi = models.FloatField(null=True, blank=True, verbose_name='NDVI')
    ndmi = models.FloatField(null=True, blank=True, verbose_name='NDMI')
    ndwi = models.FloatField(null=True, blank=True, verbose_name='NDWI')

    # 결과 - 증발산량
    kc = models.FloatField(null=True, blank=True, verbose_name='작물계수(Kc)')
    et_actual = models.FloatField(null=True, blank=True, verbose_name='실제증발산량(mm/day)')
    soil_moisture = models.FloatField(null=True, blank=True, verbose_name='토양수분지수')
    stress_index = models.FloatField(null=True, blank=True, verbose_name='수분스트레스지수')

    # 원본 응답 저장
    raw_response = models.JSONField(default=dict, blank=True, verbose_name='원본 응답')

    # 메타
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='조회일시')

    class Meta:
        verbose_name = '증발산량 조회'
        verbose_name_plural = '증발산량 조회'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        loc = self.location_name or f"({self.latitude:.4f}, {self.longitude:.4f})"
        return f"{self.user} - {loc} - ET={self.et_actual}"


class WaterLevelQuery(models.Model):
    """수위 조회 기록"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='waterlevel_queries',
        verbose_name='사용자'
    )

    station_code = models.CharField(max_length=20, verbose_name='관측소 코드')
    station_name = models.CharField(max_length=100, verbose_name='관측소명')

    # 조회 기간
    start_date = models.DateField(null=True, blank=True, verbose_name='시작일')
    end_date = models.DateField(null=True, blank=True, verbose_name='종료일')

    # 조회 시점 데이터
    water_level = models.FloatField(null=True, blank=True, verbose_name='수위(m)')
    flow_rate = models.FloatField(null=True, blank=True, verbose_name='유량(m³/s)')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='조회일시')

    class Meta:
        verbose_name = '수위 조회'
        verbose_name_plural = '수위 조회'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.station_name} - {self.created_at}"
