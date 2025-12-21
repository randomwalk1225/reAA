"""
모의 데이터 생성 명령어
Usage: python manage.py create_mock_data
       python manage.py create_mock_data --clean  # 기존 모의 데이터 삭제 후 생성
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta
import random


# 모의 데이터 식별자 (나중에 정리할 때 사용)
MOCK_PREFIX = "[모의]"


class Command(BaseCommand):
    help = '테스트용 모의 데이터를 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='기존 모의 데이터를 삭제 후 새로 생성',
        )

    def handle(self, *args, **options):
        from measurement.models import (
            Station, RatingCurve, HQDataPoint,
            MeasurementSession, WaterLevelTimeSeries,
            DischargeTimeSeries, BaseflowAnalysis, BaseflowDaily
        )

        if options['clean']:
            self.stdout.write('기존 모의 데이터 삭제 중...')
            Station.objects.filter(name__startswith=MOCK_PREFIX).delete()
            MeasurementSession.objects.filter(station_name__startswith=MOCK_PREFIX).delete()
            self.stdout.write(self.style.SUCCESS('기존 모의 데이터 삭제 완료'))

        self.stdout.write('모의 데이터 생성 시작...')

        # 1. 관측소 생성 (3개)
        stations_data = [
            {'name': f'{MOCK_PREFIX} 경주 대종천', 'river_name': '대종천', 'dm_number': 'DM-TEST-001'},
            {'name': f'{MOCK_PREFIX} 신태인', 'river_name': '동진강', 'dm_number': 'DM-TEST-002'},
            {'name': f'{MOCK_PREFIX} 평림천', 'river_name': '평림천', 'dm_number': 'DM-TEST-003'},
        ]

        stations = []
        for data in stations_data:
            station, created = Station.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            stations.append(station)
            action = '생성' if created else '이미 존재'
            self.stdout.write(f"  관측소: {station.name} ({action})")

        # 2. 수위-유량곡선 생성
        rating_curves_data = [
            {
                'station': stations[0],
                'year': 2025,
                'curve_type': 'open',
                'h_min': 0.24, 'h_max': 0.65,
                'coef_a': 3.22, 'coef_b': 1.941, 'coef_h0': 0.001,
                'r_squared': 0.985,
            },
            {
                'station': stations[1],
                'year': 2003,
                'curve_type': 'open',
                'h_min': 0.26, 'h_max': 4.45,
                'coef_a': 24.5898, 'coef_b': 1.6663, 'coef_h0': 0.034264,
                'r_squared': 0.977,
            },
            {
                'station': stations[1],
                'year': 2003,
                'curve_type': 'close',
                'h_min': 0.32, 'h_max': 2.03,
                'coef_a': 2.31208, 'coef_b': 4.14495, 'coef_h0': -0.262311,
                'r_squared': 0.934,
            },
            {
                'station': stations[2],
                'year': 2024,
                'curve_type': 'open',
                'h_min': 0.15, 'h_max': 1.20,
                'coef_a': 5.123, 'coef_b': 1.756, 'coef_h0': 0.05,
                'r_squared': 0.962,
            },
        ]

        rating_curves = []
        for data in rating_curves_data:
            curve, created = RatingCurve.objects.get_or_create(
                station=data['station'],
                year=data['year'],
                curve_type=data['curve_type'],
                defaults=data
            )
            rating_curves.append(curve)
            action = '생성' if created else '이미 존재'
            self.stdout.write(f"  H-Q 곡선: {curve} ({action})")

        # 3. 실측 H-Q 데이터 생성
        hq_data_sets = [
            # 경주 대종천
            [
                {'date': '2025-03-15', 'h': 0.24, 'q': 0.12},
                {'date': '2025-04-20', 'h': 0.32, 'q': 0.28},
                {'date': '2025-05-10', 'h': 0.48, 'q': 0.95},
                {'date': '2025-06-05', 'h': 0.65, 'q': 1.65},
            ],
            # 신태인 방류
            [
                {'date': '2003-03-01', 'h': 0.26, 'q': 1.2},
                {'date': '2003-04-15', 'h': 1.50, 'q': 35.5},
                {'date': '2003-06-20', 'h': 2.80, 'q': 95.2},
                {'date': '2003-08-10', 'h': 4.45, 'q': 245.8},
            ],
            # 신태인 저류
            [
                {'date': '2003-03-05', 'h': 0.32, 'q': 0.15},
                {'date': '2003-05-12', 'h': 0.85, 'q': 2.8},
                {'date': '2003-07-25', 'h': 1.45, 'q': 18.5},
                {'date': '2003-09-08', 'h': 2.03, 'q': 65.2},
            ],
            # 평림천
            [
                {'date': '2024-04-01', 'h': 0.15, 'q': 0.08},
                {'date': '2024-05-15', 'h': 0.45, 'q': 0.65},
                {'date': '2024-07-20', 'h': 0.85, 'q': 2.35},
                {'date': '2024-09-10', 'h': 1.20, 'q': 5.12},
            ],
        ]

        for i, curve in enumerate(rating_curves):
            for point in hq_data_sets[i]:
                hq, created = HQDataPoint.objects.get_or_create(
                    station=curve.station,
                    rating_curve=curve,
                    measured_date=datetime.strptime(point['date'], '%Y-%m-%d').date(),
                    defaults={
                        'stage': point['h'],
                        'discharge': point['q'],
                    }
                )
            self.stdout.write(f"  H-Q 데이터: {curve.station.name} - {len(hq_data_sets[i])}개")

        # 4. 측정 세션 생성
        sessions_data = [
            {
                'station_name': f'{MOCK_PREFIX} 경주 대종천',
                'measurement_date': datetime(2025, 5, 1).date(),
                'session_number': 1,
                'estimated_discharge': 1.234,
                'total_width': 10.5,
                'max_depth': 1.35,
                'total_area': 5.67,
                'rows_data': [
                    {'distance': 0.0, 'depth': 0.00, 'method': '1', 'n_06d': 0, 't_06d': 0},
                    {'distance': 1.5, 'depth': 0.45, 'method': '1', 'n_06d': 45, 't_06d': 60},
                    {'distance': 3.0, 'depth': 0.72, 'method': '2', 'n_02d': 52, 't_02d': 60, 'n_08d': 48, 't_08d': 60},
                    {'distance': 4.5, 'depth': 1.20, 'method': '3', 'n_02d': 65, 't_02d': 60, 'n_06d': 58, 't_06d': 60, 'n_08d': 52, 't_08d': 60},
                    {'distance': 6.0, 'depth': 1.35, 'method': '3', 'n_02d': 72, 't_02d': 60, 'n_06d': 64, 't_06d': 60, 'n_08d': 56, 't_08d': 60},
                    {'distance': 7.5, 'depth': 0.85, 'method': '2', 'n_02d': 58, 't_02d': 60, 'n_08d': 52, 't_08d': 60},
                    {'distance': 9.0, 'depth': 0.50, 'method': '1', 'n_06d': 42, 't_06d': 60},
                    {'distance': 10.5, 'depth': 0.00, 'method': '1', 'n_06d': 0, 't_06d': 0},
                ],
                'setup_data': {
                    'river_name': '대종천',
                    'weather': '맑음',
                    'measurer': '홍길동',
                    'final_discharge': 1.234,
                    'final_uncertainty': 4.2,
                },
            },
            {
                'station_name': f'{MOCK_PREFIX} 신태인',
                'measurement_date': datetime(2025, 4, 28).date(),
                'session_number': 1,
                'estimated_discharge': 15.67,
                'total_width': 25.0,
                'max_depth': 2.10,
                'total_area': 42.5,
                'rows_data': [
                    {'distance': 0.0, 'depth': 0.00, 'method': '1'},
                    {'distance': 5.0, 'depth': 1.20, 'method': '2'},
                    {'distance': 10.0, 'depth': 1.85, 'method': '3'},
                    {'distance': 15.0, 'depth': 2.10, 'method': '3'},
                    {'distance': 20.0, 'depth': 1.45, 'method': '2'},
                    {'distance': 25.0, 'depth': 0.00, 'method': '1'},
                ],
                'setup_data': {
                    'river_name': '동진강',
                    'weather': '흐림',
                    'final_discharge': 15.67,
                    'final_uncertainty': 3.8,
                },
            },
            {
                'station_name': f'{MOCK_PREFIX} 평림천',
                'measurement_date': datetime(2025, 4, 25).date(),
                'session_number': 1,
                'estimated_discharge': 0.856,
                'total_width': 8.0,
                'max_depth': 0.65,
                'total_area': 3.21,
                'rows_data': [
                    {'distance': 0.0, 'depth': 0.00, 'method': '1'},
                    {'distance': 2.0, 'depth': 0.35, 'method': '1'},
                    {'distance': 4.0, 'depth': 0.65, 'method': '2'},
                    {'distance': 6.0, 'depth': 0.45, 'method': '1'},
                    {'distance': 8.0, 'depth': 0.00, 'method': '1'},
                ],
                'setup_data': {
                    'river_name': '평림천',
                    'weather': '맑음',
                    'final_discharge': 0.856,
                    'final_uncertainty': 5.1,
                },
            },
        ]

        for data in sessions_data:
            session, created = MeasurementSession.objects.get_or_create(
                station_name=data['station_name'],
                measurement_date=data['measurement_date'],
                session_number=data['session_number'],
                defaults=data
            )
            action = '생성' if created else '이미 존재'
            self.stdout.write(f"  측정세션: {session.station_name} ({action})")

        # 5. 수위 시계열 생성 (90일간 시간별 데이터 - 약 2,160개/관측소)
        import math
        base_time = timezone.now().replace(minute=0, second=0, microsecond=0)
        days_to_generate = 90  # 3개월

        # 관측소별 기본 수위 특성 (base_stage, amplitude, seasonal_amplitude)
        station_characteristics = {
            0: (0.35, 0.10, 0.15),   # 경주 대종천 - 소하천
            1: (1.20, 0.30, 0.50),   # 신태인 - 중규모
            2: (0.25, 0.08, 0.12),   # 평림천 - 소하천
        }

        for idx, station in enumerate(stations):
            existing_count = WaterLevelTimeSeries.objects.filter(station=station).count()
            if existing_count >= days_to_generate * 24 * 0.9:  # 90% 이상 있으면 스킵
                self.stdout.write(f"  수위시계열: {station.name} (이미 존재 - {existing_count}개)")
                continue

            base_stage, amplitude, seasonal_amp = station_characteristics.get(idx, (0.5, 0.15, 0.20))
            records = []

            for hour in range(days_to_generate * 24):
                timestamp = base_time - timedelta(hours=hour)
                day_of_year = timestamp.timetuple().tm_yday

                # 계절 변동 (여름 장마철 높음)
                seasonal = seasonal_amp * math.sin(2 * math.pi * (day_of_year - 90) / 365)

                # 일변동 (낮에 약간 높음)
                daily = amplitude * 0.3 * math.sin(2 * math.pi * (hour % 24) / 24)

                # 홍수 이벤트 (랜덤하게 발생, 여름에 더 빈번)
                flood_prob = 0.002 if 150 < day_of_year < 250 else 0.0005
                flood = 0
                if random.random() < flood_prob:
                    flood = random.uniform(amplitude * 2, amplitude * 5)

                # 최종 수위
                stage = base_stage + seasonal + daily + flood + random.uniform(-amplitude * 0.2, amplitude * 0.2)
                stage = max(0.01, stage)  # 음수 방지

                # 품질 플래그
                quality = 'good'
                if random.random() < 0.01:  # 1% 결측
                    quality = 'missing'
                elif random.random() < 0.02:  # 2% 의심
                    quality = 'suspect'

                records.append(WaterLevelTimeSeries(
                    station=station,
                    timestamp=timestamp,
                    stage=round(stage, 3),
                    quality_flag=quality
                ))

                # 배치 저장 (메모리 관리)
                if len(records) >= 5000:
                    WaterLevelTimeSeries.objects.bulk_create(records, ignore_conflicts=True)
                    records = []

            # 남은 레코드 저장
            if records:
                WaterLevelTimeSeries.objects.bulk_create(records, ignore_conflicts=True)

            count = days_to_generate * 24
            self.stdout.write(f"  수위시계열: {station.name} - {count:,}개 (90일)")

        # 6. 기저유출 분석 생성
        for station in stations[:2]:
            analysis, created = BaseflowAnalysis.objects.get_or_create(
                station=station,
                start_date=datetime(2024, 1, 1).date(),
                end_date=datetime(2024, 12, 31).date(),
                method='lyne_hollick',
                defaults={
                    'alpha': 0.925,
                    'total_runoff': 850.5,
                    'baseflow': 425.2,
                    'direct_runoff': 425.3,
                    'bfi': 0.50,
                }
            )
            action = '생성' if created else '이미 존재'
            self.stdout.write(f"  기저유출분석: {station.name} ({action})")

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('모의 데이터 생성 완료!'))
        self.stdout.write(self.style.SUCCESS(f'식별자: "{MOCK_PREFIX}" 로 시작하는 이름'))
        self.stdout.write(self.style.SUCCESS('정리 명령: python manage.py create_mock_data --clean'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
