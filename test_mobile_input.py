from playwright.sync_api import sync_playwright
import time

def test_mobile_input():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        console_errors = []

        # Test PC view (same URL, large viewport)
        print("=== Testing PC Layout (1280px) ===")
        page_pc = browser.new_page(viewport={'width': 1280, 'height': 800})
        page_pc.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
        page_pc.on("pageerror", lambda err: console_errors.append(f"pageerror: {str(err)}"))

        page_pc.goto('http://127.0.0.1:8000/measurement/data-input/?new=1')
        page_pc.wait_for_load_state('networkidle')
        time.sleep(1)

        page_pc.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/responsive_pc.png', full_page=True)
        print("  PC layout captured")

        # Check table is visible, cards are hidden
        table_visible = page_pc.locator('.data-grid').is_visible()
        cards_visible = page_pc.locator('.card-input').first.is_visible()
        print(f"  Table visible: {table_visible}, Cards visible: {cards_visible}")

        if console_errors:
            print("  Errors:", console_errors)
        console_errors.clear()

        # Test Mobile view (same URL, small viewport)
        print("\n=== Testing Mobile Layout (390px) ===")
        page_mobile = browser.new_page(viewport={'width': 390, 'height': 844})
        page_mobile.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
        page_mobile.on("pageerror", lambda err: console_errors.append(f"pageerror: {str(err)}"))

        page_mobile.goto('http://127.0.0.1:8000/measurement/data-input/?new=1')
        page_mobile.wait_for_load_state('networkidle')
        time.sleep(1)

        page_mobile.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/responsive_mobile.png', full_page=True)
        print("  Mobile layout captured")

        # Check cards are visible, table is hidden
        table_visible = page_mobile.locator('.data-grid').is_visible()
        cards_visible = page_mobile.locator('.card-input').first.is_visible()
        print(f"  Table visible: {table_visible}, Cards visible: {cards_visible}")

        # Test chart toggle on mobile
        chart_btn = page_mobile.locator('button:has-text("단면도")').first
        if chart_btn.is_visible():
            # Chart starts hidden on mobile (showChart=true but mobile chart area)
            chart_btn.click()
            time.sleep(0.5)
            page_mobile.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/responsive_mobile_chart.png', full_page=True)
            print("  Chart toggle - OK")

        if console_errors:
            print("  Errors:", console_errors)
        else:
            print("  No JS errors!")

        browser.close()
        print("\n=== ALL TESTS COMPLETE ===")

if __name__ == "__main__":
    import os
    os.makedirs('C:/Users/rando/repos/reAA/test_screenshots', exist_ok=True)
    test_mobile_input()
