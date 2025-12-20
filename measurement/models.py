from django.db import models
from django.conf import settings


class Station(models.Model):
    """관측소"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='stations',
        verbose_name='소유자'
    )
    name = models.CharField(max_length=100, verbose_name='지점명')
    river_name = models.CharField(max_length=100, blank=True, verbose_name='하천명')
    dm_number = models.CharField(max_length=50, blank=True, verbose_name='DM번호')
    description = models.TextField(blank=True, verbose_name='설명')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '관측소'
        verbose_name_plural = '관측소'

    def __str__(self):
        return self.name


class RatingCurve(models.Model):
    """수위-유량곡선"""
    CURVE_TYPE_CHOICES = [
        ('open', '방류(Open)'),
        ('close', '저류(Close)'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='rating_curves',
        verbose_name='소유자'
    )
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='rating_curves', verbose_name='관측소')
    year = models.IntegerField(verbose_name='연도')
    curve_type = models.CharField(max_length=10, choices=CURVE_TYPE_CHOICES, default='open', verbose_name='곡선유형')

    # 수위 범위
    h_min = models.FloatField(verbose_name='최소수위(m)')
    h_max = models.FloatField(verbose_name='최대수위(m)')

    # 회귀식 계수: Q = a * (h - h0)^b
    coef_a = models.FloatField(verbose_name='계수 a')
    coef_b = models.FloatField(verbose_name='지수 b')
    coef_h0 = models.FloatField(default=0, verbose_name='영점수위 h0')

    # 통계
    r_squared = models.FloatField(null=True, blank=True, verbose_name='결정계수(R²)')
    rmse = models.FloatField(null=True, blank=True, verbose_name='RMSE')

    note = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '수위-유량곡선'
        verbose_name_plural = '수위-유량곡선'
        ordering = ['-year', 'curve_type']

    def __str__(self):
        return f"{self.station.name} {self.year}년 ({self.get_curve_type_display()})"

    def get_equation_display(self):
        """회귀식 문자열 반환"""
        if self.coef_h0 >= 0:
            return f"Q = {self.coef_a:.4f}(h - {self.coef_h0:.4f})^{self.coef_b:.4f}"
        else:
            return f"Q = {self.coef_a:.4f}(h + {abs(self.coef_h0):.4f})^{self.coef_b:.4f}"

    def calculate_discharge(self, h):
        """주어진 수위에서 유량 계산"""
        if h < self.h_min or h > self.h_max:
            return None
        return self.coef_a * ((h - self.coef_h0) ** self.coef_b)


class HQDataPoint(models.Model):
    """수위-유량 실측 데이터"""
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='hq_data', verbose_name='관측소')
    rating_curve = models.ForeignKey(RatingCurve, on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name='data_points', verbose_name='적용곡선')

    measured_date = models.DateField(verbose_name='측정일')
    stage = models.FloatField(verbose_name='수위(m)')
    discharge = models.FloatField(verbose_name='유량(m³/s)')

    # 측정 정보
    measurement_method = models.CharField(max_length=50, blank=True, verbose_name='측정방법')
    note = models.TextField(blank=True, verbose_name='비고')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '수위-유량 데이터'
        verbose_name_plural = '수위-유량 데이터'
        ordering = ['-measured_date']

    def __str__(self):
        return f"{self.station.name} {self.measured_date} H={self.stage}m Q={self.discharge}m³/s"


class WaterLevelTimeSeries(models.Model):
    """수위 시계열 데이터 (자동계측)"""
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='water_levels', verbose_name='관측소')
    timestamp = models.DateTimeField(verbose_name='측정시각')
    stage = models.FloatField(verbose_name='수위(m)')

    # 데이터 품질
    quality_flag = models.CharField(max_length=10, default='good', choices=[
        ('good', '정상'),
        ('suspect', '의심'),
        ('missing', '결측'),
        ('estimated', '추정'),
    ], verbose_name='품질플래그')

    class Meta:
        verbose_name = '수위 시계열'
        verbose_name_plural = '수위 시계열'
        ordering = ['-timestamp']
        unique_together = ['station', 'timestamp']
        indexes = [
            models.Index(fields=['station', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.station.name} {self.timestamp} H={self.stage}m"


class DischargeTimeSeries(models.Model):
    """유량 시계열 데이터 (Rating Curve 적용)"""
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='discharges', verbose_name='관측소')
    timestamp = models.DateTimeField(verbose_name='시각')

    stage = models.FloatField(verbose_name='수위(m)')
    discharge = models.FloatField(verbose_name='유량(m³/s)')

    # 적용된 Rating Curve
    rating_curve = models.ForeignKey(RatingCurve, on_delete=models.SET_NULL, null=True,
                                      related_name='discharge_series', verbose_name='적용곡선')

    # 품질 플래그
    quality_flag = models.CharField(max_length=15, default='good', choices=[
        ('good', '정상'),
        ('extrapolated', '외삽'),
        ('suspect', '의심'),
    ], verbose_name='품질플래그')

    class Meta:
        verbose_name = '유량 시계열'
        verbose_name_plural = '유량 시계열'
        ordering = ['-timestamp']
        unique_together = ['station', 'timestamp']
        indexes = [
            models.Index(fields=['station', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.station.name} {self.timestamp} Q={self.discharge}m³/s"


class BaseflowAnalysis(models.Model):
    """기저유출 분석"""
    METHOD_CHOICES = [
        ('lyne_hollick', 'Lyne-Hollick 필터'),
        ('eckhardt', 'Eckhardt 필터'),
        ('fixed_interval', '고정간격법'),
        ('local_minimum', '국부최소법'),
        ('sliding_interval', '이동간격법'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='baseflow_analyses',
        verbose_name='소유자'
    )
    station = models.ForeignKey(Station, on_delete=models.CASCADE, related_name='baseflow_analyses', verbose_name='관측소')

    # 분석 기간
    start_date = models.DateField(verbose_name='시작일')
    end_date = models.DateField(verbose_name='종료일')

    # 분석 방법 및 파라미터
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, verbose_name='분석방법')
    alpha = models.FloatField(default=0.925, verbose_name='필터계수(α)')  # recession constant
    bfi_max = models.FloatField(default=0.80, null=True, blank=True, verbose_name='최대BFI')  # for Eckhardt

    # 결과
    total_runoff = models.FloatField(null=True, blank=True, verbose_name='총유출량(mm)')
    baseflow = models.FloatField(null=True, blank=True, verbose_name='기저유출량(mm)')
    direct_runoff = models.FloatField(null=True, blank=True, verbose_name='직접유출량(mm)')
    bfi = models.FloatField(null=True, blank=True, verbose_name='기저유출지수(BFI)')

    # 메타
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, verbose_name='비고')

    class Meta:
        verbose_name = '기저유출 분석'
        verbose_name_plural = '기저유출 분석'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.station.name} {self.start_date}~{self.end_date} BFI={self.bfi}"


class BaseflowDaily(models.Model):
    """일별 기저유출 결과"""
    analysis = models.ForeignKey(BaseflowAnalysis, on_delete=models.CASCADE, related_name='daily_results', verbose_name='분석')
    date = models.DateField(verbose_name='날짜')

    total_discharge = models.FloatField(verbose_name='총유량(m³/s)')
    baseflow = models.FloatField(verbose_name='기저유출(m³/s)')
    direct_runoff = models.FloatField(verbose_name='직접유출(m³/s)')

    class Meta:
        verbose_name = '일별 기저유출'
        verbose_name_plural = '일별 기저유출'
        ordering = ['date']
        unique_together = ['analysis', 'date']

    def __str__(self):
        return f"{self.date} Q={self.total_discharge} BF={self.baseflow}"
