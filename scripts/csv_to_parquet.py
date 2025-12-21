"""
CSV to Parquet 변환 스크립트
Usage: python scripts/csv_to_parquet.py <input_csv> [output_parquet]
"""
import sys
from pathlib import Path

import pandas as pd


def convert_csv_to_parquet(input_path: str, output_path: str = None, encoding: str = 'cp949'):
    """CSV 파일을 Parquet로 변환"""
    input_file = Path(input_path)

    if not input_file.exists():
        print(f"Error: 파일을 찾을 수 없습니다: {input_path}")
        return False

    # 출력 경로 설정
    if output_path is None:
        output_path = input_file.with_suffix('.parquet')
    else:
        output_path = Path(output_path)

    print(f"입력: {input_file}")
    print(f"출력: {output_path}")

    # CSV 읽기 (여러 인코딩 시도)
    encodings = [encoding, 'cp949', 'euc-kr', 'utf-8', 'utf-8-sig']
    df = None

    for enc in encodings:
        try:
            df = pd.read_csv(input_file, encoding=enc)
            print(f"인코딩: {enc}")
            break
        except (UnicodeDecodeError, UnicodeError):
            continue

    if df is None:
        print("Error: 지원되는 인코딩을 찾을 수 없습니다.")
        return False

    # 데이터 정보 출력
    print(f"\n컬럼: {list(df.columns)}")
    print(f"행 수: {len(df):,}")
    print(f"용량 (메모리): {df.memory_usage(deep=True).sum() / 1024:.1f} KB")

    # Parquet로 저장
    df.to_parquet(output_path, compression='snappy', index=False)

    # 결과 비교
    csv_size = input_file.stat().st_size
    parquet_size = output_path.stat().st_size
    ratio = (1 - parquet_size / csv_size) * 100

    print(f"\n=== 변환 완료 ===")
    print(f"CSV 크기:     {csv_size:,} bytes ({csv_size/1024:.1f} KB)")
    print(f"Parquet 크기: {parquet_size:,} bytes ({parquet_size/1024:.1f} KB)")
    print(f"압축률:       {ratio:.1f}% 절감")

    # 검증
    df_check = pd.read_parquet(output_path)
    print(f"검증: {len(df_check):,}행 읽기 성공")

    return True


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_csv = sys.argv[1]
    output_parquet = sys.argv[2] if len(sys.argv) > 2 else None

    success = convert_csv_to_parquet(input_csv, output_parquet)
    sys.exit(0 if success else 1)
