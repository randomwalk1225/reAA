"""
관측소 데이터 로더

JSON 파일에서 관측소 정보를 로드하고 검색/필터링 기능 제공
프로그램 시작 시 한 번만 로드하여 메모리에 캐시
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from functools import lru_cache

# 데이터 파일 경로
DATA_FILE = Path(__file__).parent / 'data' / 'stations.json'

# 메모리 캐시
_stations_cache = None


def load_stations_data() -> Dict:
    """
    관측소 데이터 로드 (캐시 사용)

    Returns:
        dict: 전체 관측소 데이터
    """
    global _stations_cache

    if _stations_cache is not None:
        return _stations_cache

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            f"관측소 데이터 파일이 없습니다: {DATA_FILE}\n"
            "scripts/download_stations.py 를 실행하여 데이터를 다운로드하세요."
        )

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        _stations_cache = json.load(f)

    return _stations_cache


def get_rivers() -> List[str]:
    """강 목록 반환"""
    data = load_stations_data()
    return data.get('rivers', [])


def get_stations(
    station_type: str = 'waterlevel',
    river: Optional[str] = None,
    query: Optional[str] = None,
    limit: int = 50
) -> List[Dict]:
    """
    관측소 검색

    Args:
        station_type: 'waterlevel', 'rainfall', 'dam'
        river: 강 이름 필터 (예: '한강', '낙동강')
        query: 검색어 (지점명, 주소 등)
        limit: 최대 결과 수

    Returns:
        list: 매칭되는 관측소 목록
    """
    data = load_stations_data()
    stations = data.get('stations', {}).get(station_type, [])

    results = []

    for station in stations:
        # 강 필터
        if river and station.get('river') != river:
            continue

        # 검색어 필터
        if query:
            query_lower = query.lower()
            searchable = ' '.join([
                station.get('name', ''),
                station.get('code', ''),
                station.get('address', ''),
                station.get('detail_address', ''),
                station.get('agency', ''),
            ]).lower()

            if query_lower not in searchable:
                continue

        results.append(station)

        if len(results) >= limit:
            break

    return results


def get_station_by_code(code: str) -> Optional[Dict]:
    """
    코드로 관측소 조회

    Args:
        code: 관측소 코드

    Returns:
        dict or None: 관측소 정보
    """
    data = load_stations_data()

    for station_type in ['waterlevel', 'rainfall', 'dam']:
        stations = data.get('stations', {}).get(station_type, [])
        for station in stations:
            if station.get('code') == code:
                return station

    return None


def get_stations_by_river(river: str) -> Dict[str, List[Dict]]:
    """
    강별 관측소 그룹 반환

    Args:
        river: 강 이름

    Returns:
        dict: {station_type: [stations]}
    """
    data = load_stations_data()
    result = {
        'waterlevel': [],
        'rainfall': [],
        'dam': [],
    }

    for station_type, stations in data.get('stations', {}).items():
        result[station_type] = [
            s for s in stations if s.get('river') == river
        ]

    return result


def get_stats() -> Dict:
    """관측소 통계 반환"""
    data = load_stations_data()

    stats = {
        'total': data.get('meta', {}).get('total_count', 0),
        'by_type': {
            'waterlevel': data.get('meta', {}).get('waterlevel_count', 0),
            'rainfall': data.get('meta', {}).get('rainfall_count', 0),
            'dam': data.get('meta', {}).get('dam_count', 0),
        },
        'by_river': {},
    }

    for station_type, stations in data.get('stations', {}).items():
        for station in stations:
            river = station.get('river', '기타')
            if river not in stats['by_river']:
                stats['by_river'][river] = {'waterlevel': 0, 'rainfall': 0, 'dam': 0}
            stats['by_river'][river][station_type] += 1

    return stats


# 하위 호환성을 위한 기존 형식 변환 함수
def get_station_database() -> List[Dict]:
    """
    기존 STATION_DATABASE 형식으로 변환 (하위 호환)
    """
    stations = get_stations(station_type='waterlevel', limit=10000)

    return [
        {
            'code': s['code'],
            'name': s['name'],
            'river': s['river'],
            'dm_code': f"DM-{s['code']}",
            'region': s.get('address', '').split()[0] if s.get('address') else '',
        }
        for s in stations
    ]


def get_all_stations_dict() -> Dict[str, Dict[str, str]]:
    """
    기존 ALL_STATIONS 형식으로 변환 (하위 호환)
    """
    data = load_stations_data()

    return {
        'waterlevel': {
            s['code']: s['name']
            for s in data.get('stations', {}).get('waterlevel', [])
        },
        'rainfall': {
            s['code']: s['name']
            for s in data.get('stations', {}).get('rainfall', [])
        },
        'dam': {
            s['code']: s['name']
            for s in data.get('stations', {}).get('dam', [])
        },
    }
