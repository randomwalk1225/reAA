from playwright.sync_api import sync_playwright
import time

def test_timeseries_chart():
    errors = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False to see what's happening
        page = browser.new_page()

        # Capture console errors
        console_errors = []
        page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # Test station 1
        print("Testing /measurement/timeseries/1/")
        page.goto('http://127.0.0.1:8000/measurement/timeseries/1/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        # Take initial screenshot
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/timeseries1_initial.png', full_page=True)
        print("Initial screenshot taken")

        # Find buttons
        buttons = page.locator('button').all()
        print(f"Found {len(buttons)} buttons")

        # Find specific chart toggle buttons (exact match)
        stage_btn = page.get_by_role("button", name="수위", exact=True)
        discharge_btn = page.get_by_role("button", name="유량", exact=True)
        both_btn = page.get_by_role("button", name="둘 다", exact=True)

        print(f"Stage button visible: {stage_btn.is_visible()}")
        print(f"Discharge button visible: {discharge_btn.is_visible()}")
        print(f"Both button visible: {both_btn.is_visible()}")

        # Click 수위 button
        print("\nClicking 수위 button...")
        stage_btn.click()
        time.sleep(0.5)
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/timeseries1_stage.png', full_page=True)

        # Check button state
        stage_class = stage_btn.get_attribute('class')
        print(f"Stage button class after click: {stage_class}")

        # Click 유량 button
        print("\nClicking 유량 button...")
        discharge_btn.click()
        time.sleep(0.5)
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/timeseries1_discharge.png', full_page=True)

        discharge_class = discharge_btn.get_attribute('class')
        print(f"Discharge button class after click: {discharge_class}")

        # Click 둘 다 button
        print("\nClicking 둘 다 button...")
        both_btn.click()
        time.sleep(0.5)
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/timeseries1_both.png', full_page=True)

        both_class = both_btn.get_attribute('class')
        print(f"Both button class after click: {both_class}")

        # Test station 2
        print("\n\nTesting /measurement/timeseries/2/")
        page.goto('http://127.0.0.1:8000/measurement/timeseries/2/')
        page.wait_for_load_state('networkidle')
        time.sleep(1)

        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/timeseries2_initial.png', full_page=True)

        # Click buttons on station 2
        stage_btn = page.get_by_role("button", name="수위", exact=True)
        discharge_btn = page.get_by_role("button", name="유량", exact=True)

        print("Clicking 수위 button on station 2...")
        stage_btn.click()
        time.sleep(0.5)
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/timeseries2_stage.png', full_page=True)

        print("Clicking 유량 button on station 2...")
        discharge_btn.click()
        time.sleep(0.5)
        page.screenshot(path='C:/Users/rando/repos/reAA/test_screenshots/timeseries2_discharge.png', full_page=True)

        # Print console errors
        if console_errors:
            print("\n=== CONSOLE ERRORS ===")
            for err in console_errors:
                print(f"  {err}")
        else:
            print("\nNo console errors detected")

        # Check page for JavaScript errors by evaluating
        print("\n=== Checking Alpine.js data ===")
        try:
            alpine_data = page.evaluate('''() => {
                const el = document.querySelector('[x-data]');
                if (el && el._x_dataStack) {
                    return JSON.stringify(el._x_dataStack[0]);
                }
                return 'No Alpine data found';
            }''')
            print(f"Alpine data: {alpine_data}")
        except Exception as e:
            print(f"Error getting Alpine data: {e}")

        browser.close()

    print("\n=== TEST COMPLETE ===")
    print("Screenshots saved in C:/Users/rando/repos/reAA/test_screenshots/")

if __name__ == "__main__":
    import os
    os.makedirs('C:/Users/rando/repos/reAA/test_screenshots', exist_ok=True)
    test_timeseries_chart()
