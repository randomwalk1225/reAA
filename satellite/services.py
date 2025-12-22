"""
GK-2A 위성 영상 서비스 레이어

케이웨더 (kweather.co.kr) API 기반
GK-2A: 천리안위성 2A호, 정지궤도 위성 (128.2°E)
"""
from datetime import datetime, timedelta, timezone as dt_timezone
from django.utils import timezone
import requests
import logging

logger = logging.getLogger(__name__)

# 케이웨더 이미지 서버 베이스 URL
KWEATHER_BASE_URL = "https://www.kweather.co.kr/data/GK2A"
KWEATHER_API_URL = "https://weather.kweather.co.kr/weather/rader_satellite/get_satellite_file_list"

# 영상 타입 매핑 (kweather API 기준)
IMAGE_TYPES = {
    'infrared': {
        'name': '적외선 (한반도)',
        'api_key': 'infrared',
        'interval': 2,
    },
    'composit': {
        'name': '합성영상 (한반도)',
        'api_key': 'composit',
        'interval': 2,
    },
    'visual': {
        'name': '가시광 (한반도)',
        'api_key': 'visual',
        'interval': 2,
    },
    'focused': {
        'name': '확대영상 (한반도)',
        'api_key': 'focused',
        'interval': 2,
    },
}

# 캐시 (API 호출 최소화)
_file_list_cache = {
    'data': None,
    'timestamp': None,
    'ttl': 60,  # 초
}


def fetch_kweather_file_list():
    """
    케이웨더 API에서 위성 영상 파일 목록 가져오기

    Returns:
        dict: 영상 타입별 파일 목록
    """
    global _file_list_cache

    # 캐시 확인
    now = timezone.now()
    if (_file_list_cache['data'] is not None and
        _file_list_cache['timestamp'] is not None and
        (now - _file_list_cache['timestamp']).total_seconds() < _file_list_cache['ttl']):
        return _file_list_cache['data']

    try:
        # SSL 인증서 검증 비활성화 (kweather 인증서 문제)
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        response = requests.get(
            KWEATHER_API_URL,
            timeout=10,
            verify=False,  # SSL 인증서 검증 비활성화
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://weather.kweather.co.kr/weather/satellite',
            }
        )
        response.raise_for_status()
        data = response.json()

        # 캐시 업데이트
        _file_list_cache['data'] = data
        _file_list_cache['timestamp'] = now

        return data
    except Exception as e:
        logger.error(f"kweather API 호출 실패: {e}")
        return _file_list_cache['data'] or {}


def generate_recent_frames(count=20, image_type='infrared'):
    """
    케이웨더 API에서 최근 프레임 목록 생성

    Args:
        count: 반환할 프레임 수
        image_type: 영상 타입 (infrared, composit, visual, focused)

    Returns:
        프레임 정보 딕셔너리 리스트
    """
    file_list = fetch_kweather_file_list()
    type_info = IMAGE_TYPES.get(image_type, IMAGE_TYPES['infrared'])
    api_key = type_info['api_key']

    frames = []

    if api_key in file_list:
        files = file_list[api_key]

        # 썸네일(.thn.png) 제외, 원본 파일만
        original_files = [f for f in files if '.thn.' not in f.get('path', '')]

        for i, file_info in enumerate(original_files[:count]):
            path = file_info.get('path', '')
            timestamp_str = file_info.get('timestamp', '')

            # 타임스탬프 파싱
            try:
                # "2025.12.22 16:12" 형식
                ts = datetime.strptime(timestamp_str, '%Y.%m.%d %H:%M')
                ts = ts.replace(tzinfo=dt_timezone(timedelta(hours=9)))  # KST
            except:
                ts = timezone.now()

            image_url = f"{KWEATHER_BASE_URL}/{path}"

            frames.append({
                'timestamp': ts,
                'timestamp_str': ts.strftime('%Y-%m-%d %H:%M'),
                'timestamp_kst': ts.strftime('%Y-%m-%d %H:%M KST'),
                'base_path': image_url,
                'image_url': image_url,
                'image_type': image_type,
                'image_type_name': type_info['name'],
            })

    return frames


def sync_frames_to_db(count=20, image_type='infrared'):
    """
    최근 프레임을 DB에 동기화

    Args:
        count: 동기화할 프레임 수
        image_type: 영상 타입

    Returns:
        새로 생성된 프레임 수
    """
    from .models import SatelliteFrame

    frames = generate_recent_frames(count=count, image_type=image_type)
    created_count = 0

    for frame in frames:
        _, created = SatelliteFrame.objects.get_or_create(
            timestamp=frame['timestamp'],
            defaults={
                'base_path': frame['image_url'],
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
