"""
위성 영상 뷰어 최종 테스트 - weather.go.kr URL
"""
from playwright.sync_api import sync_playwright
import time

def test_satellite():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        image_responses = []
        def handle_response(response):
            url = response.url
            if 'proxy' in url or 'weather.go.kr' in url:
                content_type = response.headers.get('content-type', '')
                content_length = response.headers.get('content-length', '0')
                image_responses.append({
                    'url': url[:100],
                    'status': response.status,
                    'type': content_type,
                    'size': content_length
                })

        page.on('response', handle_response)

        print("1. Satellite viewer page...")
        page.goto('http://127.0.0.1:8000/satellite/')
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        print("2. Checking responses...")
        for resp in image_responses:
            print(f"   {resp['status']} | {resp['type'][:20]:20} | {resp['size']:>10} | {resp['url']}")

        # Screenshot
        page.screenshot(path='C:/Users/rando/repos/reAA/satellite_final_test.png', full_page=True)
        print("\n3. Screenshot saved: satellite_final_test.png")

        # Check if any image loaded successfully
        success = any(r['status'] == 200 and 'image' in r['type'] and int(r['size']) > 100000 for r in image_responses)

        print("\n" + "="*50)
        if success:
            print("SUCCESS: Satellite image loaded!")
        else:
            print("FAILED: No satellite image loaded")

        browser.close()

if __name__ == '__main__':
    test_satellite()
