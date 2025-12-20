"""
천리안 2A호 전용 페이지에서 이미지 URL 캡처
"""
from playwright.sync_api import sync_playwright
import time

def capture_gk2a_urls():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        image_urls = []

        def handle_response(response):
            url = response.url
            content_type = response.headers.get('content-type', '')
            content_length = response.headers.get('content-length', '0')

            # 이미지 요청 필터링 (작은 파일 제외)
            if ('image' in content_type or '.png' in url) and int(content_length) > 10000:
                image_urls.append({
                    'url': url,
                    'status': response.status,
                    'size': content_length
                })

        page.on('response', handle_response)

        # 천리안 2A호 위성영상 페이지
        print("1. 천리안 2A호 위성영상 페이지 접속...")
        page.goto('https://www.weather.go.kr/w/image/sat/gk2a.do', timeout=60000)
        page.wait_for_load_state('networkidle')
        time.sleep(5)

        print("\n=== 캡처된 위성 이미지 URL ===")
        for img in image_urls:
            print(f"\nURL: {img['url']}")
            print(f"Size: {img['size']} bytes")

        # 동아시아 영상도 확인
        print("\n2. 동아시아 영상 확인...")
        try:
            # 지역 선택 버튼 찾기
            ea_btn = page.locator('text=동아시아').first
            if ea_btn.count() > 0:
                ea_btn.click()
                time.sleep(3)

                for img in image_urls[-5:]:
                    print(f"\nURL: {img['url']}")
        except:
            pass

        browser.close()
        return image_urls

if __name__ == '__main__':
    urls = capture_gk2a_urls()

    print("\n" + "="*60)
    print("URL 패턴 분석:")
    for u in urls:
        if 'gk2a' in u['url'].lower():
            print(u['url'])
