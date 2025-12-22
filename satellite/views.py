from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET


def satellite_viewer(request):
    """메인 위성영상 뷰어 페이지 - iframe 임베딩"""
    return render(request, 'satellite/viewer.html')


@require_GET
def api_frames(request):
    """API: (레거시) 빈 프레임 반환"""
    return JsonResponse({'frames': [], 'message': 'iframe 임베딩 방식으로 변경됨'})


@require_GET
def api_latest_frame(request):
    """API: (레거시) 빈 응답"""
    return JsonResponse({'message': 'iframe 임베딩 방식으로 변경됨'})


def api_refresh(request):
    """API: (레거시) 빈 응답"""
    return JsonResponse({'message': 'iframe 임베딩 방식으로 변경됨'})


def proxy_image(request):
    """프록시 (레거시) - 더 이상 사용하지 않음"""
    return JsonResponse({'message': 'iframe 임베딩 방식으로 변경됨'})
