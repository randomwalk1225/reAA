"""
수위관측소 CSV → JSON 변환 스크립트
Usage: python scripts/convert_stations_json.py
"""
import json
from pathlib import Path

import pandas as pd


def convert_stations_to_json():
    """수자원공사 수위관측소 CSV를 JSON으로 변환"""

    # 입력 파일 경로
    csv_path = Path('resource/한국수자원공사_수위관측소 제원정보_20220502.csv')
    output_path = Path('static/data/stations.json')

    # 출력 디렉토리 생성
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # CSV 읽기 (여러 인코딩 시도)
    encodings = ['cp949', 'euc-kr', 'utf-8', 'utf-8-sig']
    df = None

    for enc in encodings:
        try:
            df = pd.read_csv(csv_path, encoding=enc)
            print(f"인코딩: {enc}")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if df is None:
        print("Error: 지원되는 인코딩을 찾을 수 없습니다.")
        return False

    print(f"원본 컬럼: {list(df.columns)}")
    print(f"행 수: {len(df)}")

    # 컬럼명 매핑
    column_map = {
        '수위관측소 코드': 'code',
        '수위관측소 명': 'name',
        '수계': 'river',
        '경도': 'lon',
        '위도': 'lat',
        '관측개시일': 'year'
    }

    # 하천 컬럼이 있으면 사용, 없으면 수계 사용
    if '하천' in df.columns:
        column_map['하천'] = 'river'
        if '수계' in column_map:
            del column_map['수계']

    # 필요한 컬럼만 추출하고 이름 변경
    available_cols = [col for col in column_map.keys() if col in df.columns]
    df_subset = df[available_cols].rename(columns=column_map)

    # 코드를 문자열로 변환
    df_subset['code'] = df_subset['code'].astype(str)

    # 연도 처리 (NaN이면 null)
    if 'year' in df_subset.columns:
        df_subset['year'] = df_subset['year'].apply(
            lambda x: int(x) if pd.notna(x) else None
        )

    # JSON 변환
    stations = df_subset.to_dict('records')

    # JSON 저장
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(stations, f, ensure_ascii=False, indent=2)

    print(f"\n=== 변환 완료 ===")
    print(f"출력: {output_path}")
    print(f"관측소 수: {len(stations)}")
    print(f"파일 크기: {output_path.stat().st_size:,} bytes")

    # 샘플 출력
    print(f"\n샘플 데이터:")
    for station in stations[:3]:
        print(f"  {station}")

    return True


if __name__ == '__main__':
    convert_stations_to_json()
