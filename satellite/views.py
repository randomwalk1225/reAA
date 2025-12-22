from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
import requests

from .services import generate_recent_frames, sync_frames_to_db, IMAGE_TYPES


def satellite_viewer(request):
    """메인 위성영상 뷰어 페이지"""
    image_type = request.GET.get('type', 'infrared')
    frames = generate_recent_frames(count=20, image_type=image_type)

    return render(request, 'satellite/viewer.html', {
        'frames': frames,
        'latest_frame': frames[0] if frames else None,
        'image_types': IMAGE_TYPES,
        'current_type': image_type,
    })


@require_GET
def api_frames(request):
    """API: 가용 프레임 목록 반환"""
    count = int(request.GET.get('count', 20))
    image_type = request.GET.get('type', 'infrared')

    frames = generate_recent_frames(count=count, image_type=image_type)

    return JsonResponse({
        'frames': [
            {
                'timestamp': f['timestamp'].isoformat(),
                'timestamp_str': f['timestamp_str'],
                'base_path': f['base_path'],
                'image_url': f['image_url'],
            }
            for f in frames
        ]
    })


@require_GET
def api_latest_frame(request):
    """API: 최신 프레임 반환"""
    image_type = request.GET.get('type', 'infrared')
    frames = generate_recent_frames(count=1, image_type=image_type)

    if frames:
        f = frames[0]
        return JsonResponse({
            'timestamp': f['timestamp'].isoformat(),
            'timestamp_str': f['timestamp_str'],
            'base_path': f['base_path'],
            'image_url': f['image_url'],
        })

    return JsonResponse({'error': 'No frames available'}, status=404)


@require_POST
def api_refresh(request):
    """API: 프레임 수동 갱신 (DB 동기화)"""
    count = sync_frames_to_db(count=20)
    return JsonResponse({'synced': count})


def proxy_image(request):
    """
    위성 이미지 프록시 (CORS/Referer 우회용)

    kweather 서버는 Referer 체크를 하므로 프록시를 통해 이미지를 가져옴
    URL: /satellite/proxy/?url=<encoded_url>
    """
    image_url = request.GET.get('url', '')

    if not image_url:
        return HttpResponse('Missing url parameter', status=400)

    # 허용된 도메인만 프록시
    allowed_domains = ['kweather.co.kr', 'weather.go.kr', 'nmsc.kma.go.kr', 'kma.go.kr']
    if not any(domain in image_url for domain in allowed_domains):
        return HttpResponse('Domain not allowed', status=403)

    # 도메인별 Referer 설정
    if 'kweather.co.kr' in image_url:
        referer = 'https://weather.kweather.co.kr/weather/satellite'
    else:
        referer = 'https://www.weather.go.kr/'

    try:
        response = requests.get(
            image_url,
            timeout=30,
            stream=True,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': referer,
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            }
        )

        if response.status_code == 200:
            return HttpResponse(
                response.content,
                content_type=response.headers.get('Content-Type', 'image/png'),
            )
        else:
            return HttpResponse(status=response.status_code)

    except requests.RequestException as e:
        return HttpResponse(f"Proxy error: {e}", status=502)
