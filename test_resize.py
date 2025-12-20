from playwright.sync_api import sync_playwright
import time

def test_resize():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        console_errors = []
        page.on("console", lambda msg: console_errors.append(f"{msg.type}: {msg.text}") if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(f"pageerror: {str(err)}"))

        page.goto('http://127.0.0.1:8000/measurement/data-input/?new=1')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        print("=== PC Layout (1280px) ===")
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/resize_1_pc.png', full_page=True)
        print("  Screenshot captured")

        # Resize to mobile
        print("\n=== Resizing to Mobile (400px) ===")
        page.set_viewport_size({'width': 400, 'height': 800})
        time.sleep(1)  # Wait for resize event and chart redraw
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/resize_2_mobile.png', full_page=True)
        print("  Screenshot captured")

        # Check if mobile chart is visible
        mobile_chart = page.locator('#crossSectionChartMobile')
        print(f"  Mobile chart visible: {mobile_chart.is_visible()}")

        # Resize back to PC
        print("\n=== Resizing back to PC (1280px) ===")
        page.set_viewport_size({'width': 1280, 'height': 800})
        time.sleep(1)
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/resize_3_pc_back.png', full_page=True)
        print("  Screenshot captured")

        if console_errors:
            print("\nErrors:", [e for e in console_errors if '404' not in e])
        else:
            print("\nNo JS errors!")

        browser.close()
        print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    import os
    os.makedirs('C:/Users/rando/repos/reAA/test_screenshots', exist_ok=True)
    test_resize()
