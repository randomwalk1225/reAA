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


class MeasurementSession(models.Model):
    """측정 데이터 입력 세션 (자동저장)"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='measurement_sessions',
        verbose_name='사용자'
    )
    session_key = models.CharField(max_length=40, blank=True, verbose_name='세션키')  # 비로그인용

    # 측정 정보
    station_name = models.CharField(max_length=100, blank=True, verbose_name='관측소명')
    measurement_date = models.DateField(null=True, blank=True, verbose_name='측정일')
    session_number = models.PositiveSmallIntegerField(default=1, verbose_name='측정회차')

    # 데이터 저장 (JSON)
    rows_data = models.JSONField(default=list, verbose_name='측선 데이터')
    calibration_data = models.JSONField(default=dict, verbose_name='검정계수')
    setup_data = models.JSONField(default=dict, verbose_name='추가 설정')  # 하천명, 기상, 측정자 등

    # 계산 결과
    estimated_discharge = models.FloatField(null=True, blank=True, verbose_name='예상유량(m³/s)')
    total_width = models.FloatField(null=True, blank=True, verbose_name='총폭(m)')
    max_depth = models.FloatField(null=True, blank=True, verbose_name='최대수심(m)')
    total_area = models.FloatField(null=True, blank=True, verbose_name='단면적(m²)')

    # 추가 계산 결과 (분석결과표용)
    wetted_perimeter = models.FloatField(null=True, blank=True, verbose_name='윤변(m)')
    hydraulic_radius = models.FloatField(null=True, blank=True, verbose_name='동수반경(m)')
    mean_velocity = models.FloatField(null=True, blank=True, verbose_name='평균유속(m/s)')
    velocity_verticals = models.IntegerField(null=True, blank=True, verbose_name='유속측선수')
    stage = models.FloatField(null=True, blank=True, verbose_name='수위(m)')
    uncertainty = models.FloatField(null=True, blank=True, verbose_name='불확실도(%)')
    quality_grade = models.CharField(max_length=5, blank=True, verbose_name='등급')  # E, G, F, P

    # 메타
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        verbose_name = '측정 세션'
        verbose_name_plural = '측정 세션'
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
        ]

    def __str__(self):
        loc = self.station_name or '미지정'
        date_str = self.measurement_date.strftime('%Y-%m-%d') if self.measurement_date else '미지정'
        return f"{self.user} - {loc} ({date_str}) #{self.session_number}"

    def calculate_analysis_results(self):
        """측선 데이터로 분석결과표 항목 계산"""
        import math

        rows = self.rows_data or []
        if not rows:
            return

        # 유효한 데이터만 필터링
        valid_rows = [r for r in rows if r.get('depth') and float(r.get('depth', 0)) > 0]
        if not valid_rows:
            return

        # 거리, 수심, 유속 추출
        distances = [float(r.get('distance', 0)) for r in valid_rows]
        depths = [float(r.get('depth', 0)) for r in valid_rows]
        velocities = [float(r.get('velocity', 0)) for r in valid_rows]

        # 1. 수면폭 (총폭)
        if distances:
            self.total_width = max(distances) - min(distances)

        # 2. 최대수심
        if depths:
            self.max_depth = max(depths)

        # 3. 단면적 (중앙단면법)
        total_area = 0
        for i, row in enumerate(valid_rows):
            d = depths[i]
            # 폭 계산 (중앙단면법)
            if i == 0:
                w = (distances[1] - distances[0]) / 2 if len(distances) > 1 else 0
            elif i == len(valid_rows) - 1:
                w = (distances[i] - distances[i-1]) / 2
            else:
                w = (distances[i+1] - distances[i-1]) / 2
            total_area += w * d
        self.total_area = total_area

        # 4. 윤변 (wetted perimeter) - 수심 변화를 따라가는 경로 길이
        wetted_perimeter = 0
        for i in range(len(valid_rows)):
            if i == 0:
                # 시작점 수직 깊이
                wetted_perimeter += depths[i]
            else:
                # 이전 점과의 거리 (바닥 따라)
                dx = distances[i] - distances[i-1]
                dy = depths[i] - depths[i-1]
                wetted_perimeter += math.sqrt(dx**2 + dy**2)
        # 마지막 점 수직
        if depths:
            wetted_perimeter += depths[-1]
        self.wetted_perimeter = wetted_perimeter

        # 5. 동수반경 = 단면적 / 윤변
        if self.wetted_perimeter and self.wetted_perimeter > 0:
            self.hydraulic_radius = self.total_area / self.wetted_perimeter

        # 6. 유속 측선 수 (유속 > 0인 측선)
        self.velocity_verticals = len([v for v in velocities if v and v > 0])

        # 7. 평균유속 = 유량 / 단면적
        if self.estimated_discharge and self.total_area and self.total_area > 0:
            self.mean_velocity = self.estimated_discharge / self.total_area
        elif velocities:
            # 또는 유속 평균
            valid_v = [v for v in velocities if v and v > 0]
            if valid_v:
                self.mean_velocity = sum(valid_v) / len(valid_v)

        # 8. 불확실도 계산 (ISO 748 간이 방식)
        n = self.velocity_verticals or 1
        if n >= 20:
            u_m = 5  # 측선 20개 이상
        elif n >= 10:
            u_m = 7.5
        elif n >= 5:
            u_m = 10
        else:
            u_m = 15  # 측선 5개 미만
        self.uncertainty = u_m

        # 9. 등급 판정
        if self.uncertainty <= 5:
            self.quality_grade = 'E'  # Excellent
        elif self.uncertainty <= 8:
            self.quality_grade = 'G'  # Good
        elif self.uncertainty <= 12:
            self.quality_grade = 'F'  # Fair
        else:
            self.quality_grade = 'P'  # Poor

    def to_summary_dict(self):
        """분석결과표용 딕셔너리 반환"""
        return {
            'id': self.id,
            'station_name': self.station_name,
            'measurement_date': self.measurement_date.strftime('%Y-%m-%d') if self.measurement_date else None,
            'session_number': self.session_number,
            'location': self.setup_data.get('location_desc', ''),
            'stage': self.stage,
            'total_width': round(self.total_width, 2) if self.total_width else None,
            'total_area': round(self.total_area, 4) if self.total_area else None,
            'wetted_perimeter': round(self.wetted_perimeter, 4) if self.wetted_perimeter else None,
            'hydraulic_radius': round(self.hydraulic_radius, 4) if self.hydraulic_radius else None,
            'mean_velocity': round(self.mean_velocity, 6) if self.mean_velocity else None,
            'discharge': round(self.estimated_discharge, 6) if self.estimated_discharge else None,
            'velocity_verticals': self.velocity_verticals,
            'uncertainty': round(self.uncertainty, 2) if self.uncertainty else None,
            'quality_grade': self.quality_grade,
            'max_depth': round(self.max_depth, 2) if self.max_depth else None,
        }


class Meter(models.Model):
    """유속계 검정 정보"""
    METER_TYPE_CHOICES = [
        ('propeller', '프로펠러형'),
        ('electronic', '전자식'),
    ]

    STATUS_CHOICES = [
        ('valid', '유효'),
        ('expiring', '만료 임박'),
        ('expired', '만료'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='meters',
        verbose_name='소유자'
    )

    meter_id = models.CharField(max_length=50, verbose_name='유속계 번호')
    meter_type = models.CharField(max_length=20, choices=METER_TYPE_CHOICES, default='propeller', verbose_name='종류')

    # 검정식 계수: V = a + b * (N/T)
    coef_a = models.FloatField(default=0.0, verbose_name='시동유속 a (m/s)')
    coef_b = models.FloatField(default=1.0, verbose_name='검정상수 b')

    # 유효 범위
    range_min = models.FloatField(default=0.0, verbose_name='최소 유속 (m/s)')
    range_max = models.FloatField(default=6.0, verbose_name='최대 유속 (m/s)')

    # 검정 정보
    uncertainty = models.FloatField(default=1.0, verbose_name='검정 불확실도 (%)')
    calibration_date = models.DateField(null=True, blank=True, verbose_name='검정일')
    calibration_expiry = models.DateField(null=True, blank=True, verbose_name='검정 유효기간')
    calibration_org = models.CharField(max_length=100, blank=True, verbose_name='검정기관')

    # 상태
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='valid', verbose_name='상태')

    # 메타
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '유속계'
        verbose_name_plural = '유속계'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.meter_id} ({self.get_meter_type_display()})"

    @property
    def range_display(self):
        return f"{self.range_min:.2f}-{self.range_max:.1f} m/s"

    def calculate_velocity(self, n, t):
        """회전수와 시간으로 유속 계산: V = a + b * (N/T)"""
        if t <= 0:
            return 0
        return self.coef_a + self.coef_b * (n / t)
