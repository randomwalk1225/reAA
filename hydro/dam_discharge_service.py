"""
한국수자원공사 수문 방류정보 조회 서비스

댐 수문 개폐 시간 정보 조회 및 유량 측정 영향 판단
API 문서: https://www.data.go.kr/data/15140222/openapi.do
"""
import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

logger = logging.getLogger(__name__)

# API 설정
DAM_DISCHARGE_API_URL = "https://apis.data.go.kr/B500001/DamDisChargeInfo/flugdschginfo"
DAM_DISCHARGE_API_KEY = os.environ.get('DAM_DISCHARGE_API_KEY', '')

# 댐 코드 매핑 (K-water 관리 댐)
DAM_INFO = {
    'CHUNGJU': {'code': '1001', 'name': '충주댐', 'river': '남한강'},
    'SOYANGGANG': {'code': '1002', 'name': '소양강댐', 'river': '북한강'},
    'PALDANG': {'code': '1003', 'name': '팔당댐', 'river': '한강'},
    'CHUNGPYUNG': {'code': '1004', 'name': '청평댐', 'river': '북한강'},
    'EUIAM': {'code': '1005', 'name': '의암댐', 'river': '북한강'},
    'CHUNCHEON': {'code': '1006', 'name': '춘천댐', 'river': '북한강'},
    'HWACHEON': {'code': '1007', 'name': '화천댐', 'river': '북한강'},
    'GOESAN': {'code': '2001', 'name': '괴산댐', 'river': '달천'},
    'DAECHEONG': {'code': '3001', 'name': '대청댐', 'river': '금강'},
    'YONGDAM': {'code': '3002', 'name': '용담댐', 'river': '금강'},
    'HAPCHEON': {'code': '4001', 'name': '합천댐', 'river': '황강'},
    'NAMGANG': {'code': '4002', 'name': '남강댐', 'river': '남강'},
    'ANDONG': {'code': '4003', 'name': '안동댐', 'river': '낙동강'},
    'IMHA': {'code': '4004', 'name': '임하댐', 'river': '반변천'},
    'UNMUN': {'code': '4005', 'name': '운문댐', 'river': '운문천'},
    'JUAM': {'code': '5001', 'name': '주암댐', 'river': '보성강'},
    'JANGHEUNG': {'code': '5002', 'name': '장흥댐', 'river': '탐진강'},
    'SEOMJINGANG': {'code': '5003', 'name': '섬진강댐', 'river': '섬진강'},
}

# 관측소 → 상류 댐 매핑 (도달시간 포함, 단위: 시간)
# 실제 도달시간은 하천 상태, 유량에 따라 변동됨 - 참고용 기본값
STATION_UPSTREAM_DAMS = {
    # 한강대교 (팔당댐 하류)
    '1018683': [
        {'dam': 'PALDANG', 'travel_time_hours': 2},
    ],
    # 잠수교 (팔당댐 하류)
    '1018680': [
        {'dam': 'PALDANG', 'travel_time_hours': 2.5},
    ],
    # 팔당댐 (충주댐, 소양강댐 하류)
    '1018630': [
        {'dam': 'CHUNGJU', 'travel_time_hours': 8},
        {'dam': 'SOYANGGANG', 'travel_time_hours': 6},
    ],
    # 청담대교
    '1019665': [
        {'dam': 'PALDANG', 'travel_time_hours': 3},
    ],
    # 광진교
    '1018685': [
        {'dam': 'PALDANG', 'travel_time_hours': 2.5},
    ],
    # 미사리
    '1018640': [
        {'dam': 'PALDANG', 'travel_time_hours': 1},
    ],
    # 여주 (충주댐 하류)
    '1012690': [
        {'dam': 'CHUNGJU', 'travel_time_hours': 4},
    ],
    # 이포보 (충주댐 하류)
    '1012630': [
        {'dam': 'CHUNGJU', 'travel_time_hours': 5},
    ],
    # 충주댐 (직접)
    '1012640': [],
    # 의암댐 (소양강댐 하류)
    '1016640': [
        {'dam': 'SOYANGGANG', 'travel_time_hours': 2},
        {'dam': 'CHUNCHEON', 'travel_time_hours': 1},
    ],
    # 춘천댐
    '1016630': [
        {'dam': 'SOYANGGANG', 'travel_time_hours': 3},
    ],
    # 소양댐 (직접)
    '1016610': [],
    # 청평댐
    '1016680': [
        {'dam': 'EUIAM', 'travel_time_hours': 2},
        {'dam': 'CHUNCHEON', 'travel_time_hours': 3},
    ],
}


def fetch_dam_discharge_info(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    dam_code: Optional[str] = None,
    page_no: int = 1,
    num_of_rows: int = 100
) -> List[Dict]:
    """
    댐 수문 방류정보 조회

    Args:
        start_date: 시작일 (YYYYMMDD 형식, 없으면 오늘)
        end_date: 종료일 (YYYYMMDD 형식, 없으면 오늘)
        dam_code: 댐 코드 (없으면 전체)
        page_no: 페이지 번호
        num_of_rows: 페이지당 결과 수

    Returns:
        list: 방류정보 목록
    """
    if not DAM_DISCHARGE_API_KEY:
        logger.warning("DAM_DISCHARGE_API_KEY 환경변수가 설정되지 않았습니다.")
        return []

    today = datetime.now().strftime('%Y%m%d')

    params = {
        'serviceKey': DAM_DISCHARGE_API_KEY,
        'pageNo': str(page_no),
        'numOfRows': str(num_of_rows),
    }

    if start_date:
        params['stDt'] = start_date
    if end_date:
        params['edDt'] = end_date
    if dam_code:
        params['damCd'] = dam_code

    try:
        response = requests.get(DAM_DISCHARGE_API_URL, params=params, timeout=30)
        response.raise_for_status()

        # XML 파싱
        root = ET.fromstring(response.content)

        # 에러 체크
        result_code = root.find('.//resultCode')
        if result_code is not None and result_code.text != '00':
            result_msg = root.find('.//resultMsg')
            msg = result_msg.text if result_msg is not None else 'Unknown error'
            logger.error(f"API 오류: {msg}")
            return []

        items = []
        for item in root.findall('.//item'):
            discharge_info = {
                'dam_code': _get_text(item, 'DAMCD'),
                'dam_name': _get_text(item, 'DAMNM'),
                'dam_coord': _get_text(item, 'DAMCOORD'),
                'start_date': _get_text(item, 'STARTDATE'),
                'end_date': _get_text(item, 'ENDDATE'),
                'affect_area': _get_text(item, 'AFFECTAREA'),
                'created_date': _get_text(item, 'CREATEDDATE'),
                'updated_date': _get_text(item, 'UPDATEDDATE'),
            }

            # 시간 파싱
            if discharge_info['start_date']:
                discharge_info['start_datetime'] = _parse_datetime(discharge_info['start_date'])
            if discharge_info['end_date']:
                discharge_info['end_datetime'] = _parse_datetime(discharge_info['end_date'])

            items.append(discharge_info)

        return items

    except requests.RequestException as e:
        logger.error(f"API 요청 오류: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"XML 파싱 오류: {e}")
        return []


def _get_text(element, tag: str) -> str:
    """XML 요소에서 텍스트 추출"""
    child = element.find(tag)
    return child.text.strip() if child is not None and child.text else ''


def _parse_datetime(date_str: str) -> Optional[datetime]:
    """다양한 형식의 날짜 문자열 파싱"""
    formats = [
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d %H:%M',
        '%Y%m%d%H%M%S',
        '%Y%m%d%H%M',
        '%Y%m%d',
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def is_dam_discharging(dam_key: str, check_time: datetime) -> Dict:
    """
    특정 시각에 댐이 방류 중인지 확인

    Args:
        dam_key: 댐 키 (예: 'PALDANG', 'CHUNGJU')
        check_time: 확인할 시각

    Returns:
        dict: {
            'is_discharging': bool,
            'discharge_info': dict or None
        }
    """
    dam_info = DAM_INFO.get(dam_key)
    if not dam_info:
        return {'is_discharging': False, 'discharge_info': None}

    # 해당일 방류정보 조회
    date_str = check_time.strftime('%Y%m%d')
    discharges = fetch_dam_discharge_info(start_date=date_str, end_date=date_str)

    for discharge in discharges:
        if dam_info['name'] in discharge.get('dam_name', ''):
            start_dt = discharge.get('start_datetime')
            end_dt = discharge.get('end_datetime')

            if start_dt and end_dt:
                if start_dt <= check_time <= end_dt:
                    return {
                        'is_discharging': True,
                        'discharge_info': discharge
                    }
            elif start_dt and not end_dt:
                # 종료 시간이 없으면 현재 방류 중으로 간주
                if start_dt <= check_time:
                    return {
                        'is_discharging': True,
                        'discharge_info': discharge
                    }

    return {'is_discharging': False, 'discharge_info': None}


def check_dam_influence(station_code: str, measurement_time: datetime) -> Dict:
    """
    관측소에서 측정 시각에 댐 방류 영향 여부 확인

    도달시간을 고려하여 상류 댐의 방류가 측정 시점에 영향을 미치는지 판단

    Args:
        station_code: 관측소 코드
        measurement_time: 측정 시각

    Returns:
        dict: {
            'is_influenced': bool,
            'influencing_dams': [
                {
                    'dam_name': str,
                    'start_time': datetime,
                    'end_time': datetime,
                    'affect_area': str,
                    'travel_time_hours': float
                }
            ],
            'message': str
        }
    """
    upstream_dams = STATION_UPSTREAM_DAMS.get(station_code, [])

    if not upstream_dams:
        return {
            'is_influenced': False,
            'influencing_dams': [],
            'message': '상류 댐 정보 없음'
        }

    influencing_dams = []

    for upstream in upstream_dams:
        dam_key = upstream['dam']
        travel_time = upstream['travel_time_hours']

        # 방류 시작 후 도달시간이 지나야 영향이 나타남
        # 따라서 측정시각 - 도달시간 시점에 방류 중이었는지 확인
        effective_time = measurement_time - timedelta(hours=travel_time)

        result = is_dam_discharging(dam_key, effective_time)

        if result['is_discharging']:
            dam_info = DAM_INFO.get(dam_key, {})
            discharge = result['discharge_info']

            influencing_dams.append({
                'dam_key': dam_key,
                'dam_name': dam_info.get('name', dam_key),
                'river': dam_info.get('river', ''),
                'start_time': discharge.get('start_datetime'),
                'end_time': discharge.get('end_datetime'),
                'affect_area': discharge.get('affect_area', ''),
                'travel_time_hours': travel_time,
            })

    is_influenced = len(influencing_dams) > 0

    if is_influenced:
        dam_names = [d['dam_name'] for d in influencing_dams]
        message = f"댐 방류 영향: {', '.join(dam_names)}"
    else:
        message = "댐 방류 영향 없음"

    return {
        'is_influenced': is_influenced,
        'influencing_dams': influencing_dams,
        'message': message
    }


def get_today_discharges() -> List[Dict]:
    """
    오늘 진행 중인 모든 댐 방류 정보 조회

    Returns:
        list: 방류 정보 목록
    """
    today = datetime.now().strftime('%Y%m%d')
    return fetch_dam_discharge_info(start_date=today, end_date=today)


def get_active_discharges(check_time: Optional[datetime] = None) -> List[Dict]:
    """
    현재 진행 중인 방류만 필터링

    Args:
        check_time: 확인 시각 (없으면 현재)

    Returns:
        list: 현재 방류 중인 댐 목록
    """
    if check_time is None:
        check_time = datetime.now()

    all_discharges = get_today_discharges()
    active = []

    for discharge in all_discharges:
        start_dt = discharge.get('start_datetime')
        end_dt = discharge.get('end_datetime')

        if start_dt:
            if end_dt:
                if start_dt <= check_time <= end_dt:
                    active.append(discharge)
            else:
                # 종료 시간 미정 = 아직 방류 중
                if start_dt <= check_time:
                    active.append(discharge)

    return active
