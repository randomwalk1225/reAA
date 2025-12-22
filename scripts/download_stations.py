"""
전국 홍수통제소 관측소 정보 다운로드 및 저장

HRFCO API에서 수위/강수량 관측소 정보를 다운받아 JSON 파일로 저장
"""
import requests
import xml.etree.ElementTree as ET
import json
import os
from pathlib import Path

HRFCO_API_KEY = '9E50673B-2D96-4436-BA86-756E81D3C738'
BASE_URL = 'https://api.hrfco.go.kr'

# 강 권역 매핑 (관측소 코드 prefix 기반)
RIVER_MAPPING = {
    '10': '한강',
    '11': '한강',
    '12': '한강',
    '13': '한강',
    '14': '한강',
    '15': '한강',
    '16': '한강',
    '17': '한강',
    '18': '한강',
    '19': '한강',
    '20': '낙동강',
    '21': '낙동강',
    '22': '낙동강',
    '23': '낙동강',
    '24': '낙동강',
    '25': '낙동강',
    '26': '낙동강',
    '27': '낙동강',
    '28': '낙동강',
    '29': '낙동강',
    '30': '금강',
    '31': '금강',
    '32': '금강',
    '33': '금강',
    '34': '금강',
    '35': '금강',
    '36': '금강',
    '37': '금강',
    '38': '금강',
    '39': '금강',
    '40': '영산강',
    '41': '영산강',
    '42': '영산강',
    '43': '영산강',
    '44': '영산강',
    '45': '영산강',
    '50': '섬진강',
    '51': '섬진강',
    '52': '섬진강',
    '53': '섬진강',
    '54': '섬진강',
    '55': '섬진강',
}


def get_river_name(station_code):
    """관측소 코드로 강 이름 반환"""
    prefix = station_code[:2] if station_code else ''
    return RIVER_MAPPING.get(prefix, '기타')


def fetch_waterlevel_stations():
    """수위 관측소 정보 조회"""
    url = f'{BASE_URL}/{HRFCO_API_KEY}/waterlevel/info.xml'

    resp = requests.get(url, timeout=60)
    resp.encoding = 'utf-8'

    stations = []
    root = ET.fromstring(resp.content)

    for item in root.findall('.//WaterlevelInfo'):
        code = get_text(item, 'wlobscd')
        if not code:
            continue

        station = {
            'code': code,
            'name': get_text(item, 'obsnm'),
            'type': 'waterlevel',
            'river': get_river_name(code),
            'address': get_text(item, 'addr'),
            'detail_address': get_text(item, 'etcaddr'),
            'agency': get_text(item, 'agcnm'),
            'lat': parse_dms(get_text(item, 'lat')),
            'lon': parse_dms(get_text(item, 'lon')),
            'ground_elevation': parse_float(get_text(item, 'gdt')),
            'flood_level': parse_float(get_text(item, 'pfh')),
            'warning_level': parse_float(get_text(item, 'wrnwl')),
            'alert_level': parse_float(get_text(item, 'almwl')),
            'attention_level': parse_float(get_text(item, 'attwl')),
            'serious_level': parse_float(get_text(item, 'srswl')),
            'is_forecast_station': get_text(item, 'fstnyn') == 'Y',
        }
        stations.append(station)

    return stations


def fetch_rainfall_stations():
    """강수량 관측소 정보 조회"""
    url = f'{BASE_URL}/{HRFCO_API_KEY}/rainfall/info.xml'

    resp = requests.get(url, timeout=60)
    resp.encoding = 'utf-8'

    stations = []
    root = ET.fromstring(resp.content)

    for item in root.findall('.//Rainfall'):
        code = get_text(item, 'rfobscd')
        if not code:
            continue

        station = {
            'code': code,
            'name': get_text(item, 'obsnm'),
            'type': 'rainfall',
            'river': get_river_name(code),
            'address': get_text(item, 'addr'),
            'detail_address': get_text(item, 'etcaddr'),
            'agency': get_text(item, 'agcnm'),
            'lat': parse_dms(get_text(item, 'lat')),
            'lon': parse_dms(get_text(item, 'lon')),
            'ground_elevation': parse_float(get_text(item, 'gdt')),
        }
        stations.append(station)

    return stations


def fetch_dam_stations():
    """댐 관측소 정보 조회"""
    url = f'{BASE_URL}/{HRFCO_API_KEY}/dam/info.xml'

    resp = requests.get(url, timeout=60)
    resp.encoding = 'utf-8'

    stations = []
    root = ET.fromstring(resp.content)

    for item in root.findall('.//Dam'):
        code = get_text(item, 'dmobscd')
        if not code:
            continue

        station = {
            'code': code,
            'name': get_text(item, 'obsnm'),
            'type': 'dam',
            'river': get_river_name(code),
            'address': get_text(item, 'addr'),
            'agency': get_text(item, 'agcnm'),
            'lat': parse_dms(get_text(item, 'lat')),
            'lon': parse_dms(get_text(item, 'lon')),
        }
        stations.append(station)

    return stations


def get_text(element, tag):
    """XML 요소에서 텍스트 추출"""
    child = element.find(tag)
    if child is not None and child.text:
        return child.text.strip()
    return ''


def parse_dms(dms_str):
    """도분초 문자열을 십진수 좌표로 변환 (예: '37-37-27' -> 37.6242)"""
    if not dms_str or not dms_str.strip():
        return None
    try:
        parts = dms_str.strip().split('-')
        if len(parts) >= 3:
            d = float(parts[0])
            m = float(parts[1])
            s = float(parts[2])
            return round(d + m/60 + s/3600, 6)
    except:
        pass
    return None


def parse_float(value):
    """문자열을 float로 변환"""
    if not value or not value.strip():
        return None
    try:
        return float(value.strip())
    except:
        return None


def main():
    print('=== 전국 관측소 정보 다운로드 ===')
    print()

    # 수위 관측소
    print('1. 수위 관측소 다운로드 중...')
    waterlevel_stations = fetch_waterlevel_stations()
    print(f'   {len(waterlevel_stations)}개 다운로드 완료')

    # 강수량 관측소
    print('2. 강수량 관측소 다운로드 중...')
    rainfall_stations = fetch_rainfall_stations()
    print(f'   {len(rainfall_stations)}개 다운로드 완료')

    # 댐 관측소
    print('3. 댐 관측소 다운로드 중...')
    dam_stations = fetch_dam_stations()
    print(f'   {len(dam_stations)}개 다운로드 완료')

    # 통계
    print()
    print('=== 강별 통계 ===')

    all_stations = waterlevel_stations + rainfall_stations + dam_stations

    river_stats = {}
    for s in all_stations:
        river = s['river']
        stype = s['type']
        if river not in river_stats:
            river_stats[river] = {'waterlevel': 0, 'rainfall': 0, 'dam': 0}
        river_stats[river][stype] += 1

    for river in ['한강', '낙동강', '금강', '영산강', '섬진강', '기타']:
        if river in river_stats:
            stats = river_stats[river]
            total = sum(stats.values())
            print(f'{river}: 수위 {stats["waterlevel"]}, 강수 {stats["rainfall"]}, 댐 {stats["dam"]} (총 {total}개)')

    # JSON 파일 저장
    output_dir = Path(__file__).parent.parent / 'hydro' / 'data'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / 'stations.json'

    data = {
        'meta': {
            'source': 'HRFCO Open API',
            'api_url': 'https://api.hrfco.go.kr',
            'total_count': len(all_stations),
            'waterlevel_count': len(waterlevel_stations),
            'rainfall_count': len(rainfall_stations),
            'dam_count': len(dam_stations),
        },
        'rivers': list(river_stats.keys()),
        'stations': {
            'waterlevel': waterlevel_stations,
            'rainfall': rainfall_stations,
            'dam': dam_stations,
        }
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print()
    print(f'=== 저장 완료: {output_file} ===')


if __name__ == '__main__':
    main()
