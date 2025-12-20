from playwright.sync_api import sync_playwright
import time

def test_all_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(f"pageerror: {str(err)}"))

        pages_to_test = [
            ('http://127.0.0.1:8000/measurement/', '측정 관리'),
            ('http://127.0.0.1:8000/measurement/timeseries/', '시계열 목록'),
            ('http://127.0.0.1:8000/measurement/timeseries/1/', '시계열 상세 1'),
            ('http://127.0.0.1:8000/measurement/timeseries/2/', '시계열 상세 2'),
            ('http://127.0.0.1:8000/measurement/baseflow/', '기저유출 목록'),
            ('http://127.0.0.1:8000/measurement/baseflow/new/', '기저유출 새로만들기'),
            ('http://127.0.0.1:8000/measurement/baseflow/1/', '기저유출 상세'),
            ('http://127.0.0.1:8000/measurement/rating-curve/', 'H-Q 곡선 목록'),
        ]

        for url, name in pages_to_test:
            print(f"\n=== Testing: {name} ({url}) ===")
            console_errors.clear()

            try:
                page.goto(url, timeout=10000)
                page.wait_for_load_state('networkidle')
                time.sleep(1)

                # Take screenshot
                filename = name.replace(' ', '_').replace('/', '_')
                page.screenshot(path=f'C:/Users/rando/repos/reAA/test_screenshots/{filename}.png', full_page=True)

                if console_errors:
                    print(f"  ERRORS found:")
                    for err in console_errors:
                        if '404' not in err:  # Ignore 404 for missing resources
                            print(f"    - {err}")
                else:
                    print(f"  OK - No errors")

            except Exception as e:
                print(f"  FAILED: {e}")

        # Test timeseries chart toggle on fresh page
        print("\n\n=== Testing Chart Toggle (Fresh Load) ===")
        console_errors.clear()
        page.goto('http://127.0.0.1:8000/measurement/timeseries/1/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Click each button
        for btn_name in ['수위', '유량', '둘 다']:
            btn = page.get_by_role("button", name=btn_name, exact=True)
            if btn.is_visible():
                btn.click()
                time.sleep(0.5)
                print(f"  Clicked '{btn_name}' - OK")
            else:
                print(f"  Button '{btn_name}' not visible!")

        if console_errors:
            print("\n  Chart Toggle Errors:")
            for err in console_errors:
                if '404' not in err:
                    print(f"    - {err}")
        else:
            print("\n  Chart Toggle - No errors!")

        # Test baseflow analysis
        print("\n\n=== Testing Baseflow Analysis ===")
        console_errors.clear()
        page.goto('http://127.0.0.1:8000/measurement/baseflow/new/?station=1')
        page.wait_for_load_state('networkidle')
        time.sleep(2)  # Wait for analysis to run

        if console_errors:
            print("  Errors:")
            for err in console_errors:
                if '404' not in err:
                    print(f"    - {err}")
        else:
            print("  OK - No errors")

        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/baseflow_analysis.png', full_page=True)

        browser.close()
        print("\n\n=== ALL TESTS COMPLETE ===")

if __name__ == "__main__":
    import os
    os.makedirs('C:/Users/rando/repos/reAA/test_screenshots', exist_ok=True)
    test_all_pages()
