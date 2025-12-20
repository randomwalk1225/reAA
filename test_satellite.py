"""
위성 영상 뷰어 테스트 - GK-2A 이미지 로딩 확인
"""
from playwright.sync_api import sync_playwright
import time

def test_satellite_viewer():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 네트워크 요청 로그
        image_requests = []
        def handle_request(request):
            if 'proxy' in request.url or 'nmsc.kma.go.kr' in request.url:
                image_requests.append({
                    'url': request.url,
                    'method': request.method
                })

        image_responses = []
        def handle_response(response):
            if 'proxy' in response.url or 'nmsc.kma.go.kr' in response.url:
                image_responses.append({
                    'url': response.url,
                    'status': response.status,
                    'content_type': response.headers.get('content-type', '')
                })

        page.on('request', handle_request)
        page.on('response', handle_response)

        print("1. 위성 영상 뷰어 페이지 접속...")
        page.goto('http://127.0.0.1:8000/satellite/')
        page.wait_for_load_state('networkidle')

        # 맵이 로드될 때까지 대기
        print("2. 지도 로딩 대기...")
        page.wait_for_selector('#satellite-map', state='visible')
        time.sleep(3)  # 이미지 로딩을 위한 추가 대기

        # 현재 시각 표시 확인
        current_time = page.locator('.time-display').first.inner_text()
        print(f"3. 현재 영상 시각: {current_time}")

        # 이미지 타입 선택기 확인
        image_type_selector = page.locator('select')
        current_type = image_type_selector.input_value()
        print(f"4. 현재 영상 타입: {current_type}")

        # 스크린샷 촬영
        print("5. 스크린샷 촬영...")
        page.screenshot(path='C:/Users/rando/repos/reAA/satellite_test.png', full_page=True)

        # 로딩 오버레이 상태 확인
        loading_overlay = page.locator('.loading-overlay')
        is_loading = loading_overlay.is_visible()
        print(f"6. 로딩 중: {is_loading}")

        # 네트워크 요청 확인
        print("\n=== 네트워크 요청 ===")
        for req in image_requests:
            print(f"  요청: {req['url'][:100]}...")

        print("\n=== 네트워크 응답 ===")
        for resp in image_responses:
            print(f"  응답: {resp['status']} - {resp['content_type']}")
            print(f"       URL: {resp['url'][:100]}...")

        # 이미지 레이어 확인
        satellite_layers = page.locator('.leaflet-image-layer')
        layer_count = satellite_layers.count()
        print(f"\n7. Leaflet 이미지 레이어 수: {layer_count}")

        if layer_count > 0:
            # 이미지 레이어 src 확인
            for i in range(layer_count):
                src = satellite_layers.nth(i).get_attribute('src')
                if src:
                    print(f"   레이어 {i+1} src: {src[:80]}...")

        # 프레임 수 확인
        frame_info = page.locator('text=/\\d+ \\/ \\d+/')
        if frame_info.count() > 0:
            print(f"8. 프레임 정보: {frame_info.first.inner_text()}")

        browser.close()

        # 결과 판정
        print("\n" + "="*50)
        if len(image_responses) > 0 and any(r['status'] == 200 for r in image_responses):
            print("✅ 성공: 위성 이미지가 정상적으로 로드되었습니다!")
            return True
        else:
            print("❌ 실패: 위성 이미지 로드에 문제가 있습니다.")
            return False

if __name__ == '__main__':
    test_satellite_viewer()
