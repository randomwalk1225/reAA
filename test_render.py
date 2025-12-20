from playwright.sync_api import sync_playwright
import time

BASE_URL = 'https://discharge-measurement.onrender.com'

def test_render_site():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        console_errors = []

        # Test PC Layout
        print("=== Testing PC Layout ===")
        page_pc = browser.new_page(viewport={'width': 1280, 'height': 800})
        page_pc.on("console", lambda msg: console_errors.append(f"[PC] {msg.type}: {msg.text}") if msg.type == "error" else None)
        page_pc.on("pageerror", lambda err: console_errors.append(f"[PC] pageerror: {str(err)}"))

        pages_to_test = [
            (f'{BASE_URL}/measurement/', '측정 목록'),
            (f'{BASE_URL}/measurement/data-input/?new=1', '데이터 입력'),
            (f'{BASE_URL}/measurement/timeseries/', '시계열 목록'),
            (f'{BASE_URL}/measurement/baseflow/', '기저유출 목록'),
            (f'{BASE_URL}/measurement/rating-curve/', 'H-Q 곡선'),
        ]

        for url, name in pages_to_test:
            print(f"\n  Testing: {name}")
            try:
                page_pc.goto(url, timeout=30000)
                page_pc.wait_for_load_state('networkidle', timeout=30000)
                time.sleep(1)
                print(f"    OK - loaded")
            except Exception as e:
                print(f"    FAILED: {e}")

        # Test data input specifically
        print("\n=== Testing Data Input Page ===")
        console_errors.clear()
        page_pc.goto(f'{BASE_URL}/measurement/data-input/?new=1', timeout=30000)
        page_pc.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(2)

        # Check chart is visible
        chart_visible = page_pc.locator('#crossSectionChartPC').is_visible()
        print(f"  Cross-section chart visible: {chart_visible}")

        page_pc.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/render_pc.png', full_page=True)
        print("  Screenshot saved: render_pc.png")

        # Test Mobile Layout
        print("\n=== Testing Mobile Layout ===")
        page_mobile = browser.new_page(viewport={'width': 390, 'height': 844})
        page_mobile.on("console", lambda msg: console_errors.append(f"[Mobile] {msg.type}: {msg.text}") if msg.type == "error" else None)
        page_mobile.on("pageerror", lambda err: console_errors.append(f"[Mobile] pageerror: {str(err)}"))

        page_mobile.goto(f'{BASE_URL}/measurement/data-input/?new=1', timeout=30000)
        page_mobile.wait_for_load_state('networkidle', timeout=30000)
        time.sleep(2)

        # Check cards visible
        cards_visible = page_mobile.locator('.card-input').first.is_visible()
        print(f"  Card layout visible: {cards_visible}")

        page_mobile.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/render_mobile.png', full_page=True)
        print("  Screenshot saved: render_mobile.png")

        # Test resize
        print("\n=== Testing Resize ===")
        page_pc.set_viewport_size({'width': 400, 'height': 800})
        time.sleep(1.5)
        mobile_chart = page_pc.locator('#crossSectionChartMobile').is_visible()
        print(f"  After resize - Mobile chart visible: {mobile_chart}")

        page_pc.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/render_resize.png', full_page=True)

        # Report errors
        print("\n=== Error Summary ===")
        js_errors = [e for e in console_errors if '404' not in e and 'favicon' not in e.lower()]
        if js_errors:
            print("  JS Errors found:")
            for err in js_errors:
                print(f"    - {err}")
        else:
            print("  No JS errors!")

        browser.close()
        print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    import os
    os.makedirs('C:/Users/rando/repos/reAA/test_screenshots', exist_ok=True)
    test_render_site()
