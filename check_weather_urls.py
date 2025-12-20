"""
기상청 날씨누리에서 실제 위성 이미지 URL 캡처
"""
from playwright.sync_api import sync_playwright
import time

def capture_satellite_urls():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 이미지 관련 네트워크 요청 캡처
        image_urls = []

        def handle_response(response):
            url = response.url
            content_type = response.headers.get('content-type', '')

            # 이미지 요청 필터링
            if 'image' in content_type or url.endswith(('.png', '.jpg', '.gif')):
                if 'satellite' in url.lower() or 'sat' in url.lower() or 'gk2a' in url.lower() or 'kma' in url:
                    image_urls.append({
                        'url': url,
                        'status': response.status,
                        'content_type': content_type
                    })

        page.on('response', handle_response)

        print("1. 기상청 날씨누리 위성영상 페이지 접속...")
        page.goto('https://www.weather.go.kr/w/image/sat.do', timeout=60000)
        page.wait_for_load_state('networkidle')

        print("2. 페이지 로딩 대기...")
        time.sleep(5)

        # 추가 상호작용으로 더 많은 이미지 로드 시도
        print("3. 위성영상 탭/버튼 클릭 시도...")
        try:
            # 천리안 2A호 관련 요소 찾기
            buttons = page.locator('button, a, div[role="button"]').all()
            for btn in buttons[:10]:
                text = btn.inner_text()
                if '천리안' in text or '위성' in text or 'GK2A' in text:
                    print(f"   클릭: {text}")
                    btn.click()
                    time.sleep(2)
        except Exception as e:
            print(f"   버튼 클릭 실패: {e}")

        time.sleep(3)

        print("\n=== 캡처된 이미지 URL ===")
        for img in image_urls:
            print(f"\nURL: {img['url']}")
            print(f"Status: {img['status']}, Type: {img['content_type']}")

        # 페이지에서 이미지 src 직접 추출
        print("\n=== 페이지 내 img 태그 ===")
        images = page.locator('img').all()
        for img in images:
            src = img.get_attribute('src')
            if src and ('sat' in src.lower() or 'gk2a' in src.lower() or 'weather' in src):
                print(f"img src: {src}")

        # 스크린샷
        page.screenshot(path='C:/Users/rando/repos/reAA/weather_sat_page.png', full_page=True)
        print("\n스크린샷 저장: weather_sat_page.png")

        browser.close()

        return image_urls

if __name__ == '__main__':
    capture_satellite_urls()
