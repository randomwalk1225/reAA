# -*- coding: utf-8 -*-
"""
VBA 매크로 코드 추출 스크립트
"""
import sys
import io
import os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from oletools.olevba import VBA_Parser

def extract_vba(file_path, output_dir):
    """VBA 코드 추출"""
    os.makedirs(output_dir, exist_ok=True)

    print(f"Analyzing: {file_path}")

    try:
        vba_parser = VBA_Parser(file_path)

        if vba_parser.detect_vba_macros():
            print("VBA Macros detected!")

            # 모든 VBA 모듈 추출
            for (filename, stream_path, vba_filename, vba_code) in vba_parser.extract_macros():
                print(f"\n--- Module: {vba_filename} ---")
                print(f"    Stream: {stream_path}")

                # 파일로 저장
                safe_name = vba_filename.replace("/", "_").replace("\\", "_")
                output_path = os.path.join(output_dir, f"{safe_name}.vb")

                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"' Module: {vba_filename}\n")
                    f.write(f"' Stream: {stream_path}\n")
                    f.write(f"' Source: {filename}\n")
                    f.write("' " + "="*60 + "\n\n")
                    f.write(vba_code)

                print(f"    Saved to: {output_path}")
                print(f"    Lines: {len(vba_code.splitlines())}")

            # 분석 결과 요약
            print("\n" + "="*60)
            print("VBA Analysis Summary:")
            results = vba_parser.analyze_macros()
            for kw_type, keyword, description in results:
                print(f"  [{kw_type}] {keyword}: {description}")

        else:
            print("No VBA macros detected.")

        vba_parser.close()

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    base_path = r'C:\Users\rando\repos\reAA'
    xlsm_file = os.path.join(base_path, '경주대종천하류보20250501_unlocked.xlsm')
    output_dir = os.path.join(base_path, 'extracted_vba')

    extract_vba(xlsm_file, output_dir)

    # xls 파일도 확인
    for xls_file in ['경주_대종천_하류보.xls', '경주대종천하류보20250501.xls']:
        full_path = os.path.join(base_path, xls_file)
        if os.path.exists(full_path):
            print(f"\n{'='*60}")
            extract_vba(full_path, output_dir)
