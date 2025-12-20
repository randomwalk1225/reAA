"""
GK-2A 위성 영상 서비스 레이어

한국 기상청 날씨누리 (weather.go.kr)
GK-2A: 천리안위성 2A호, 정지궤도 위성 (128.2°E)
"""
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone

# 기상청 날씨누리 이미지 서버 베이스 URL
WEATHER_BASE_URL = "https://www.weather.go.kr/w/repositary/image/sat/gk2a"

# 영상 처리 지연 시간 (분) - 보통 5-10분 후 가용
GK2A_DELAY_MINUTES = 10

# 영상 타입 매핑
# 한반도(KO): 2분 간격, 동아시아(EA): 10분 간격
IMAGE_TYPES = {
    'ko_true': {
        'region': 'KO',
        'product': 'rgb-s-true',
        'code': 'ko020lc',
        'name': '자연색 (한반도)',
        'interval': 2,  # 분
    },
    'ko_daynight': {
        'region': 'KO',
        'product': 'rgb-s-daynight',
        'code': 'ko020lc',
        'name': '주야간합성 (한반도)',
        'interval': 2,
    },
    'ko_ir105': {
        'region': 'KO',
        'product': 'ir105',
        'code': 'ko020lc',
        'name': '적외선 (한반도)',
        'interval': 2,
    },
    'ea_true': {
        'region': 'EA',
        'product': 'rgb-s-true',
        'code': 'ea010lc',
        'name': '자연색 (동아시아)',
        'interval': 10,
    },
    'ea_daynight': {
        'region': 'EA',
        'product': 'rgb-s-daynight',
        'code': 'ea010lc',
        'name': '주야간합성 (동아시아)',
        'interval': 10,
    },
}


def get_latest_available_timestamp(interval=2):
    """
    최신 가용 타임스탬프 계산

    Args:
        interval: 영상 갱신 간격 (분)

    Returns:
        datetime 객체 (UTC)
    """
    now = timezone.now()

    # 지연 시간 적용
    adjusted = now - timedelta(minutes=GK2A_DELAY_MINUTES)

    # UTC로 변환
    if adjusted.tzinfo is not None:
        adjusted_utc = adjusted.astimezone(dt_timezone.utc)
    else:
        adjusted_utc = adjusted

    # interval 단위로 내림
    minute = (adjusted_utc.minute // interval) * interval

    return adjusted_utc.replace(minute=minute, second=0, microsecond=0)


def timestamp_to_weather_url(ts, image_type='ko_true'):
    """
    타임스탬프를 기상청 날씨누리 이미지 URL로 변환

    Args:
        ts: datetime 객체
        image_type: 영상 타입

    Returns:
        전체 이미지 URL

    URL 구조:
    https://www.weather.go.kr/w/repositary/image/sat/gk2a/{REGION}/gk2a_ami_le1b_{PRODUCT}_{CODE}_{TIMESTAMP}.png
    """
    type_info = IMAGE_TYPES.get(image_type, IMAGE_TYPES['ko_true'])

    # UTC로 변환
    if ts.tzinfo is not None:
        ts_utc = ts.astimezone(dt_timezone.utc)
    else:
        ts_utc = ts

    timestamp_str = ts_utc.strftime('%Y%m%d%H%M')
    filename = f"gk2a_ami_le1b_{type_info['product']}_{type_info['code']}_{timestamp_str}.png"

    return f"{WEATHER_BASE_URL}/{type_info['region']}/{filename}"


def generate_recent_frames(count=12, image_type='ko_true'):
    """
    최근 N개의 프레임 정보 생성

    Args:
        count: 생성할 프레임 수
        image_type: 영상 타입

    Returns:
        프레임 정보 딕셔너리 리스트
    """
    type_info = IMAGE_TYPES.get(image_type, IMAGE_TYPES['ko_true'])
    interval = type_info['interval']

    latest = get_latest_available_timestamp(interval)
    frames = []

    for i in range(count):
        ts = latest - timedelta(minutes=i * interval)
        image_url = timestamp_to_weather_url(ts, image_type)

        frames.append({
            'timestamp': ts,
            'timestamp_str': ts.strftime('%Y-%m-%d %H:%M'),
            'timestamp_utc': ts.strftime('%Y-%m-%d %H:%M UTC'),
            'base_path': image_url,
            'image_url': image_url,
            'image_type': image_type,
            'image_type_name': type_info['name'],
        })

    return frames


def sync_frames_to_db(count=12, image_type='ko_true'):
    """
    최근 프레임을 DB에 동기화

    Args:
        count: 동기화할 프레임 수
        image_type: 영상 타입

    Returns:
        새로 생성된 프레임 수
    """
    from .models import SatelliteFrame

    type_info = IMAGE_TYPES.get(image_type, IMAGE_TYPES['ko_true'])
    interval = type_info['interval']

    latest = get_latest_available_timestamp(interval)
    created_count = 0

    for i in range(count):
        ts = latest - timedelta(minutes=i * interval)
        image_url = timestamp_to_weather_url(ts, image_type)

        frame, created = SatelliteFrame.objects.get_or_create(
            timestamp=ts,
            defaults={
                'base_path': image_url,
                'image_type': image_type,
                'is_available': True,
            }
        )
        if created:
            created_count += 1

    # 24시간 이상 된 오래된 프레임 정리
    cutoff = timezone.now() - timedelta(hours=24)
    SatelliteFrame.objects.filter(timestamp__lt=cutoff).delete()

    return created_count
