from playwright.sync_api import sync_playwright
import time

BASE_URL = 'http://127.0.0.1:8000'

def test_local():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        console_errors = []

        pages_to_test = [
            (f'{BASE_URL}/measurement/', '측정 목록'),
            (f'{BASE_URL}/measurement/data-input/?new=1', '데이터 입력'),
            (f'{BASE_URL}/measurement/timeseries/', '시계열 목록'),
            (f'{BASE_URL}/measurement/timeseries/1/', '시계열 상세'),
            (f'{BASE_URL}/measurement/baseflow/', '기저유출 목록'),
            (f'{BASE_URL}/measurement/rating-curve/', 'H-Q 곡선'),
        ]

        print("=== Testing All Pages ===")
        page = browser.new_page(viewport={'width': 1280, 'height': 800})
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(f"pageerror: {str(err)}"))

        for url, name in pages_to_test:
            print(f"\n  {name}: ", end="")
            console_errors.clear()
            try:
                page.goto(url, timeout=10000)
                page.wait_for_load_state('networkidle')
                time.sleep(0.5)

                errors = [e for e in console_errors if '404' not in e]
                if errors:
                    print(f"ERRORS: {errors}")
                else:
                    print("OK")
            except Exception as e:
                print(f"FAILED: {e}")

        # Test Data Input in detail
        print("\n=== Data Input Page Details ===")
        console_errors.clear()

        # PC Layout
        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto(f'{BASE_URL}/measurement/data-input/?new=1')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        table_visible = page.locator('.data-grid').is_visible()
        pc_chart = page.locator('#crossSectionChartPC').is_visible()
        print(f"  PC: Table={table_visible}, Chart={pc_chart}")
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/local_pc.png', full_page=True)

        # Mobile Layout
        page.set_viewport_size({'width': 390, 'height': 844})
        time.sleep(1)

        cards_visible = page.locator('.card-input').first.is_visible()
        mobile_chart = page.locator('#crossSectionChartMobile').is_visible()
        print(f"  Mobile: Cards={cards_visible}, Chart={mobile_chart}")
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/local_mobile.png', full_page=True)

        # Timeseries chart toggle
        print("\n=== Timeseries Chart Toggle ===")
        page.set_viewport_size({'width': 1280, 'height': 800})
        page.goto(f'{BASE_URL}/measurement/timeseries/1/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)
        console_errors.clear()  # 페이지 로드 후 에러 초기화

        for btn_name in ['수위', '유량', '둘 다']:
            console_errors.clear()  # 각 버튼 클릭 전 에러 초기화
            btn = page.get_by_role("button", name=btn_name, exact=True)
            if btn.is_visible():
                btn.click()
                time.sleep(0.5)
                errors = [e for e in console_errors if '404' not in e]
                status = "ERROR" if errors else "OK"
                print(f"  {btn_name}: {status}")
                if errors:
                    print(f"    {errors}")

        # Summary
        print("\n=== Summary ===")
        all_errors = [e for e in console_errors if '404' not in e]
        if all_errors:
            print(f"  Total errors: {len(all_errors)}")
            for e in all_errors[:5]:
                print(f"    - {e}")
        else:
            print("  All tests passed!")

        browser.close()

if __name__ == "__main__":
    import os
    os.makedirs('C:/Users/rando/repos/reAA/test_screenshots', exist_ok=True)
    test_local()
