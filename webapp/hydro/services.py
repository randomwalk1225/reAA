"""
한강홍수통제소 Open API 서비스 레이어

실시간 수위, 유량, 강수량 데이터 조회
API 문서: https://www.hrfco.go.kr/web/openapiPage/reference.do
"""
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from django.conf import settings

# API 기본 설정
HRFCO_BASE_URL = "https://api.hrfco.go.kr"
HRFCO_API_KEY = os.environ.get('HRFCO_API_KEY', '9E50673B-2D96-4436-BA86-756E81D3C738')

# 전체 관측소 목록 (한강홍수통제소 관할) - 상세 정보 포함
# https://www.hrfco.go.kr 관측소 정보 참고
# 형식: code -> {name, river, dm_code, region}
STATION_DATABASE = [
    # 한강본류
    {'code': '1018683', 'name': '한강대교', 'river': '한강', 'dm_code': 'DM-1018683', 'region': '서울'},
    {'code': '1018680', 'name': '잠수교', 'river': '한강', 'dm_code': 'DM-1018680', 'region': '서울'},
    {'code': '1018630', 'name': '팔당댐', 'river': '한강', 'dm_code': 'DM-1018630', 'region': '경기'},
    {'code': '1019665', 'name': '청담대교', 'river': '한강', 'dm_code': 'DM-1019665', 'region': '서울'},
    {'code': '1018685', 'name': '광진교', 'river': '한강', 'dm_code': 'DM-1018685', 'region': '서울'},
    {'code': '1018640', 'name': '미사리', 'river': '한강', 'dm_code': 'DM-1018640', 'region': '경기'},
    {'code': '1018620', 'name': '강천보', 'river': '남한강', 'dm_code': 'DM-1018620', 'region': '경기'},
    {'code': '1012690', 'name': '여주', 'river': '남한강', 'dm_code': 'DM-1012690', 'region': '경기'},
    {'code': '1012630', 'name': '이포보', 'river': '남한강', 'dm_code': 'DM-1012630', 'region': '경기'},
    {'code': '1012610', 'name': '흥천', 'river': '남한강', 'dm_code': 'DM-1012610', 'region': '충북'},
    {'code': '1012640', 'name': '충주댐', 'river': '남한강', 'dm_code': 'DM-1012640', 'region': '충북'},
    {'code': '1012660', 'name': '목계', 'river': '남한강', 'dm_code': 'DM-1012660', 'region': '충북'},
    {'code': '1012680', 'name': '양평', 'river': '남한강', 'dm_code': 'DM-1012680', 'region': '경기'},
    {'code': '1012620', 'name': '원주천합류', 'river': '남한강', 'dm_code': 'DM-1012620', 'region': '강원'},
    # 북한강
    {'code': '1016640', 'name': '의암댐', 'river': '북한강', 'dm_code': 'DM-1016640', 'region': '강원'},
    {'code': '1016630', 'name': '춘천댐', 'river': '북한강', 'dm_code': 'DM-1016630', 'region': '강원'},
    {'code': '1016610', 'name': '소양댐', 'river': '북한강', 'dm_code': 'DM-1016610', 'region': '강원'},
    {'code': '1016680', 'name': '청평댐', 'river': '북한강', 'dm_code': 'DM-1016680', 'region': '경기'},
    # 임진강
    {'code': '1002620', 'name': '전곡', 'river': '임진강', 'dm_code': 'DM-1002620', 'region': '경기'},
    {'code': '1002640', 'name': '문산', 'river': '임진강', 'dm_code': 'DM-1002640', 'region': '경기'},
    {'code': '1002680', 'name': '적성', 'river': '임진강', 'dm_code': 'DM-1002680', 'region': '경기'},
    # 경안천
    {'code': '1018660', 'name': '경안교', 'river': '경안천', 'dm_code': 'DM-1018660', 'region': '경기'},
    # 중랑천
    {'code': '1018690', 'name': '중랑천', 'river': '중랑천', 'dm_code': 'DM-1018690', 'region': '서울'},
    # 안양천
    {'code': '1018695', 'name': '안양천', 'river': '안양천', 'dm_code': 'DM-1018695', 'region': '서울'},
    # 탄천
    {'code': '1018700', 'name': '탄천', 'river': '탄천', 'dm_code': 'DM-1018700', 'region': '서울'},
    # 청미천
    {'code': '1012650', 'name': '장호원', 'river': '청미천', 'dm_code': 'DM-1012650', 'region': '경기'},
    # 섬강
    {'code': '1012670', 'name': '부론', 'river': '섬강', 'dm_code': 'DM-1012670', 'region': '강원'},
    # 달천
    {'code': '1012645', 'name': '수안보', 'river': '달천', 'dm_code': 'DM-1012645', 'region': '충북'},
    # 홍천강
    {'code': '1016650', 'name': '홍천', 'river': '홍천강', 'dm_code': 'DM-1016650', 'region': '강원'},
    # 조종천
    {'code': '1016670', 'name': '조종천', 'river': '조종천', 'dm_code': 'DM-1016670', 'region': '경기'},
]

# 하위 호환성을 위한 기존 형식 유지
ALL_STATIONS = {
    'waterlevel': {s['code']: s['name'] for s in STATION_DATABASE},
    'rainfall': {
        '10184100': '서울(대곡교)',
        '10181700': '수원',
        '10186100': '인천',
        '10181610': '광주',
        '10183100': '춘천',
        '10182700': '원주',
        '10181410': '양평',
        '10182710': '충주',
        '10184410': '파주',
        '10183410': '홍천',
        '10182610': '횡성',
        '10182100': '이천',
    }
}


def search_stations(query, limit=20):
    """
    관측소 검색 (지점명, 하천명, DM코드로 검색)

    Args:
        query: 검색어
        limit: 최대 결과 수

    Returns:
        list: 매칭되는 관측소 목록
    """
    if not query:
        return STATION_DATABASE[:limit]

    query_lower = query.lower()
    results = []

    for station in STATION_DATABASE:
        # 지점명, 하천명, DM코드, 지역으로 검색
        if (query_lower in station['name'].lower() or
            query_lower in station['river'].lower() or
            query_lower in station['dm_code'].lower() or
            query_lower in station['region'].lower() or
            query_lower in station['code']):
            results.append(station)

    return results[:limit]

# 기본 선택 관측소
DEFAULT_STATIONS = {
    'waterlevel': ['1018630', '1018680', '1018683', '1019665', '1018685'],
    'rainfall': ['10184100', '10181700', '10183100', '10182700', '10181410'],
}


def parse_xml_response(xml_text):
    """XML 응답 파싱"""
    try:
        root = ET.fromstring(xml_text)
        items = []

        # content 내의 모든 아이템 찾기
        for content in root.findall('.//content'):
            for child in content:
                item = {}
                for field in child:
                    item[field.tag] = field.text.strip() if field.text else ''
                items.append(item)

        return items
    except ET.ParseError as e:
        print(f"XML 파싱 오류: {e}")
        return []


def get_realtime_waterlevel(station_code=None):
    """
    실시간 수위 데이터 조회

    Args:
        station_code: 관측소 코드 (None이면 전체)

    Returns:
        list of dict: 수위 데이터 목록
    """
    if station_code:
        url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/waterlevel/list/10M/{station_code}.xml"
    else:
        url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/waterlevel/list/10M.xml"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        items = parse_xml_response(response.text)

        # 데이터 정제
        for item in items:
            item['wl'] = float(item.get('wl', 0)) if item.get('wl') else None
            item['fw'] = float(item.get('fw', 0)) if item.get('fw', '').strip() else None
            item['station_name'] = ALL_STATIONS['waterlevel'].get(item.get('wlobscd'), item.get('wlobscd'))

            # 시간 파싱
            ymdhm = item.get('ymdhm', '')
            if ymdhm:
                try:
                    item['datetime'] = datetime.strptime(ymdhm, '%Y%m%d%H%M')
                    item['time_str'] = item['datetime'].strftime('%Y-%m-%d %H:%M')
                except:
                    item['datetime'] = None
                    item['time_str'] = ymdhm

        return items
    except requests.RequestException as e:
        print(f"API 요청 오류: {e}")
        return []


def get_realtime_rainfall(station_code=None):
    """
    실시간 강수량 데이터 조회

    Args:
        station_code: 관측소 코드 (None이면 전체)

    Returns:
        list of dict: 강수량 데이터 목록
    """
    if station_code:
        url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/rainfall/list/10M/{station_code}.xml"
    else:
        url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/rainfall/list/10M.xml"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        items = parse_xml_response(response.text)

        # 데이터 정제
        for item in items:
            item['rf'] = float(item.get('rf', 0)) if item.get('rf') else 0.0
            item['station_name'] = ALL_STATIONS['rainfall'].get(item.get('rfobscd'), item.get('rfobscd'))

            # 시간 파싱
            ymdhm = item.get('ymdhm', '')
            if ymdhm:
                try:
                    item['datetime'] = datetime.strptime(ymdhm, '%Y%m%d%H%M')
                    item['time_str'] = item['datetime'].strftime('%Y-%m-%d %H:%M')
                except:
                    item['datetime'] = None
                    item['time_str'] = ymdhm

        return items
    except requests.RequestException as e:
        print(f"API 요청 오류: {e}")
        return []


def get_waterlevel_history(station_code, start_dt, end_dt):
    """
    기간별 수위 데이터 조회

    Args:
        station_code: 관측소 코드
        start_dt: 시작 시간 (datetime 또는 'YYYYMMDDHHmm' 문자열)
        end_dt: 종료 시간

    Returns:
        list of dict: 수위 데이터 목록
    """
    if isinstance(start_dt, datetime):
        start_str = start_dt.strftime('%Y%m%d%H%M')
    else:
        start_str = start_dt

    if isinstance(end_dt, datetime):
        end_str = end_dt.strftime('%Y%m%d%H%M')
    else:
        end_str = end_dt

    url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/waterlevel/list/10M/{station_code}/{start_str}/{end_str}.xml"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        items = parse_xml_response(response.text)

        for item in items:
            item['wl'] = float(item.get('wl', 0)) if item.get('wl') else None
            item['fw'] = float(item.get('fw', 0)) if item.get('fw', '').strip() else None

            ymdhm = item.get('ymdhm', '')
            if ymdhm:
                try:
                    item['datetime'] = datetime.strptime(ymdhm, '%Y%m%d%H%M')
                    item['time_str'] = item['datetime'].strftime('%Y-%m-%d %H:%M')
                except:
                    item['datetime'] = None

        return items
    except requests.RequestException as e:
        print(f"API 요청 오류: {e}")
        return []


def get_rainfall_history(station_code, start_dt, end_dt):
    """
    기간별 강수량 데이터 조회
    """
    if isinstance(start_dt, datetime):
        start_str = start_dt.strftime('%Y%m%d%H%M')
    else:
        start_str = start_dt

    if isinstance(end_dt, datetime):
        end_str = end_dt.strftime('%Y%m%d%H%M')
    else:
        end_str = end_dt

    url = f"{HRFCO_BASE_URL}/{HRFCO_API_KEY}/rainfall/list/10M/{station_code}/{start_str}/{end_str}.xml"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        items = parse_xml_response(response.text)

        for item in items:
            item['rf'] = float(item.get('rf', 0)) if item.get('rf') else 0.0

            ymdhm = item.get('ymdhm', '')
            if ymdhm:
                try:
                    item['datetime'] = datetime.strptime(ymdhm, '%Y%m%d%H%M')
                    item['time_str'] = item['datetime'].strftime('%Y-%m-%d %H:%M')
                except:
                    item['datetime'] = None

        return items
    except requests.RequestException as e:
        print(f"API 요청 오류: {e}")
        return []


def get_stations_data(waterlevel_codes=None, rainfall_codes=None):
    """
    선택된 관측소 실시간 데이터 조회

    Args:
        waterlevel_codes: 수위 관측소 코드 리스트 (None이면 기본값)
        rainfall_codes: 강수 관측소 코드 리스트 (None이면 기본값)
    """
    if waterlevel_codes is None:
        waterlevel_codes = DEFAULT_STATIONS['waterlevel']
    if rainfall_codes is None:
        rainfall_codes = DEFAULT_STATIONS['rainfall']

    all_waterlevel = get_realtime_waterlevel()
    all_rainfall = get_realtime_rainfall()

    # 선택된 관측소만 필터링
    filtered_waterlevel = [
        item for item in all_waterlevel
        if item.get('wlobscd') in waterlevel_codes
    ]

    filtered_rainfall = [
        item for item in all_rainfall
        if item.get('rfobscd') in rainfall_codes
    ]

    return {
        'waterlevel': filtered_waterlevel,
        'rainfall': filtered_rainfall,
        'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }


def get_major_stations_data():
    """
    기본 관측소 실시간 데이터 조회 (하위 호환용)
    """
    return get_stations_data()
