"""
Google Earth Engine 서비스 레이어

Landsat 위성 데이터를 활용한 증발산량(ET) 계산
- NDVI (Normalized Difference Vegetation Index)
- NDMI (Normalized Difference Moisture Index)
- ET 추정 (NDVI 기반 간편법)

사용 전 GEE 인증 필요:
1. https://earthengine.google.com 에서 계정 등록
2. 서비스 계정 생성 후 JSON 키 파일 발급
3. 환경변수 GEE_SERVICE_ACCOUNT_KEY 설정

로컬 개발 시: pip install earthengine-api
"""
import os
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# GEE 사용 가능 여부
_gee_available = False
try:
    import ee
    _gee_available = True
except ImportError:
    ee = None

# GEE 초기화 상태
_gee_initialized = False
_gee_init_error = None


def init_gee():
    """Google Earth Engine 초기화"""
    global _gee_initialized, _gee_init_error

    if not _gee_available:
        _gee_init_error = "earthengine-api 미설치"
        return False

    if _gee_initialized:
        return True

    project_id = os.environ.get('GEE_PROJECT_ID', 'hydrolink-481811')
    key_info_str = ""

    try:
        import base64

        # 방법 1: Base64 인코딩된 개별 변수 (권장 - Railway용)
        client_email = os.environ.get('GEE_CLIENT_EMAIL', '')
        private_key_b64 = os.environ.get('GEE_PRIVATE_KEY', '')

        if client_email and private_key_b64:
            private_key = base64.b64decode(private_key_b64).decode('utf-8')
            key_info = {
                'type': 'service_account',
                'project_id': project_id,
                'client_email': client_email,
                'private_key': private_key
            }
            key_info_str = json.dumps(key_info)
            credentials = ee.ServiceAccountCredentials(client_email, key_data=key_info_str)
            ee.Initialize(credentials, project=project_id)

        # 방법 2: 파일 경로 (로컬 개발용)
        else:
            key_path = os.environ.get('GEE_SERVICE_ACCOUNT_JSON', '') or os.environ.get('GEE_SERVICE_ACCOUNT_KEY', '')

            if key_path and os.path.exists(key_path):
                with open(key_path) as f:
                    key_info_str = f.read()
                key_info = json.loads(key_info_str)
                credentials = ee.ServiceAccountCredentials(key_info['client_email'], key_data=key_info_str)
                ee.Initialize(credentials, project=project_id)
            else:
                # 기본 인증 (gcloud auth 필요)
                ee.Initialize(project=project_id)

        _gee_initialized = True
        return True

    except Exception as e:
        _gee_init_error = f"{e} | PROJECT={project_id} | EMAIL={bool(client_email)} | KEY_B64={bool(private_key_b64)}"
        logger.error(f"GEE 초기화 실패: {_gee_init_error}")
        return False


def is_gee_available():
    """GEE 사용 가능 여부 확인"""
    return _gee_available


def get_landsat_collection(region, start_date, end_date, cloud_cover=20):
    """
    Landsat 8/9 이미지 컬렉션 조회

    Args:
        region: 관심 지역 (dict with 'lat', 'lon' or GeoJSON)
        start_date: 시작일 (YYYY-MM-DD)
        end_date: 종료일 (YYYY-MM-DD)
        cloud_cover: 최대 구름량 (%)

    Returns:
        ee.ImageCollection or None
    """
    if not init_gee():
        return None

    import ee

    # 지역 정의
    if isinstance(region, dict) and 'lat' in region:
        point = ee.Geometry.Point([region['lon'], region['lat']])
        aoi = point.buffer(5000)  # 5km 버퍼
    else:
        aoi = ee.Geometry(region)

    # Landsat 8/9 Surface Reflectance
    collection = (ee.ImageCollection('LANDSAT/LC09/C02/T1_L2')
        .merge(ee.ImageCollection('LANDSAT/LC08/C02/T1_L2'))
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt('CLOUD_COVER', cloud_cover))
        .sort('system:time_start', False))  # 최신순

    return collection, aoi


def calculate_ndvi(image):
    """
    NDVI 계산 (Landsat 8/9)

    NDVI = (NIR - RED) / (NIR + RED)
    Landsat 8/9: (B5 - B4) / (B5 + B4)
    """
    import ee

    # Scale 적용 (Landsat C2 L2)
    nir = image.select('SR_B5').multiply(0.0000275).add(-0.2)
    red = image.select('SR_B4').multiply(0.0000275).add(-0.2)

    ndvi = nir.subtract(red).divide(nir.add(red)).rename('NDVI')
    return image.addBands(ndvi)


def calculate_ndmi(image):
    """
    NDMI 계산 - 토양수분 지수

    NDMI = (NIR - SWIR) / (NIR + SWIR)
    Landsat 8/9: (B5 - B6) / (B5 + B6)
    """
    import ee

    nir = image.select('SR_B5').multiply(0.0000275).add(-0.2)
    swir = image.select('SR_B6').multiply(0.0000275).add(-0.2)

    ndmi = nir.subtract(swir).divide(nir.add(swir)).rename('NDMI')
    return image.addBands(ndmi)


def calculate_ndwi(image):
    """
    NDWI 계산 - 수분 지수

    NDWI = (GREEN - NIR) / (GREEN + NIR)
    Landsat 8/9: (B3 - B5) / (B3 + B5)
    """
    import ee

    green = image.select('SR_B3').multiply(0.0000275).add(-0.2)
    nir = image.select('SR_B5').multiply(0.0000275).add(-0.2)

    ndwi = green.subtract(nir).divide(green.add(nir)).rename('NDWI')
    return image.addBands(ndwi)


def estimate_et_from_ndvi(ndvi_value, et0, kc_min=0.1, kc_max=1.2):
    """
    NDVI 기반 증발산량 추정 (간편법)

    ET = Kc × ET0
    Kc = kc_min + (kc_max - kc_min) × NDVI

    Args:
        ndvi_value: NDVI 값 (-1 ~ 1)
        et0: 기준증발산량 (mm/day)
        kc_min: 최소 작물계수
        kc_max: 최대 작물계수

    Returns:
        ET (mm/day)
    """
    # NDVI 정규화 (0~1)
    ndvi_normalized = max(0, min(1, (ndvi_value + 1) / 2))

    # 작물계수 계산
    kc = kc_min + (kc_max - kc_min) * ndvi_normalized

    # ET 계산
    et = kc * et0

    return et


def get_vegetation_indices(lat, lon, date=None, buffer_km=5):
    """
    특정 지점의 식생지수 조회

    Args:
        lat: 위도
        lon: 경도
        date: 조회 날짜 (None이면 최근 30일)
        buffer_km: 버퍼 반경 (km)

    Returns:
        dict: NDVI, NDMI, NDWI 값
    """
    if not _gee_available:
        return {
            'error': 'Google Earth Engine이 설치되지 않았습니다. 로컬에서 pip install earthengine-api 실행 필요.',
            'status': 'unavailable'
        }

    if not init_gee():
        return {'error': f'GEE 초기화 실패: {_gee_init_error}', 'status': 'unavailable'}

    import ee

    try:
        # 날짜 범위
        if date is None:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)
        else:
            end_date = datetime.strptime(date, '%Y-%m-%d')
            start_date = end_date - timedelta(days=30)

        # 컬렉션 조회
        region = {'lat': lat, 'lon': lon}
        collection, aoi = get_landsat_collection(
            region,
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d'),
            cloud_cover=30
        )

        if collection is None:
            return {'error': 'Landsat 데이터 조회 실패', 'status': 'error'}

        # 이미지 수 확인
        count = collection.size().getInfo()
        if count == 0:
            return {
                'error': '해당 기간에 사용 가능한 위성 영상이 없습니다',
                'status': 'no_data',
                'period': f"{start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')}"
            }

        # 최신 이미지 선택 및 지수 계산
        image = collection.first()
        image = calculate_ndvi(image)
        image = calculate_ndmi(image)
        image = calculate_ndwi(image)

        # 평균값 추출
        stats = image.select(['NDVI', 'NDMI', 'NDWI']).reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=aoi,
            scale=30,
            maxPixels=1e9
        ).getInfo()

        # 영상 날짜
        image_date = datetime.fromtimestamp(
            image.get('system:time_start').getInfo() / 1000
        ).strftime('%Y-%m-%d')

        return {
            'status': 'success',
            'date': image_date,
            'location': {'lat': lat, 'lon': lon},
            'indices': {
                'ndvi': round(stats.get('NDVI', 0), 4),
                'ndmi': round(stats.get('NDMI', 0), 4),
                'ndwi': round(stats.get('NDWI', 0), 4),
            },
            'image_count': count,
        }

    except Exception as e:
        return {'error': str(e), 'status': 'error'}


def calculate_water_balance_et(lat, lon, et0, date=None):
    """
    물수지 분석용 증발산량 계산

    Args:
        lat: 위도
        lon: 경도
        et0: 기준증발산량 (mm/day) - 기상자료에서 획득
        date: 조회 날짜

    Returns:
        dict: ET 계산 결과
    """
    # 식생지수 조회
    indices = get_vegetation_indices(lat, lon, date)

    if indices.get('status') != 'success':
        return indices

    ndvi = indices['indices']['ndvi']

    # ET 추정
    et = estimate_et_from_ndvi(ndvi, et0)

    return {
        'status': 'success',
        'date': indices['date'],
        'location': {'lat': lat, 'lon': lon},
        'ndvi': ndvi,
        'et0': et0,
        'et': round(et, 2),
        'kc': round(et / et0 if et0 > 0 else 0, 3),
        'unit': 'mm/day',
        'method': 'NDVI-based Kc estimation',
    }


# 한국 주요 지점 좌표 (테스트용)
KOREA_LOCATIONS = {
    '팔당댐': {'lat': 37.5219, 'lon': 127.2903},
    '충주댐': {'lat': 36.9917, 'lon': 127.9833},
    '소양댐': {'lat': 37.9442, 'lon': 127.8186},
    '서울': {'lat': 37.5665, 'lon': 126.9780},
    '대전': {'lat': 36.3504, 'lon': 127.3845},
    '부산': {'lat': 35.1796, 'lon': 129.0756},
}
