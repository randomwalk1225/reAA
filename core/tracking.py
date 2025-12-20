"""
사용자 활동 추적 유틸리티
"""
from functools import wraps
from django.contrib.contenttypes.models import ContentType


def get_client_ip(request):
    """클라이언트 IP 주소 추출"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(user, action_type, detail, related_object=None, request=None, extra_data=None):
    """
    사용자 활동 로그 기록

    Args:
        user: 사용자 객체
        action_type: 활동 유형 ('save', 'export_pdf', 'analysis', etc.)
        detail: 상세 설명
        related_object: 관련된 모델 인스턴스 (optional)
        request: HTTP 요청 객체 (optional, IP/UA 추출용)
        extra_data: 추가 데이터 dict (optional)
    """
    from .models import UserActivity

    if not user or not user.is_authenticated:
        return None

    activity_data = {
        'user': user,
        'action_type': action_type,
        'action_detail': detail[:200],  # max_length 제한
    }

    # 관련 객체 설정
    if related_object:
        activity_data['content_type'] = ContentType.objects.get_for_model(related_object)
        activity_data['object_id'] = related_object.pk

    # 요청 정보 추출
    if request:
        activity_data['ip_address'] = get_client_ip(request)
        activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]

    # 추가 데이터
    if extra_data:
        activity_data['extra_data'] = extra_data

    return UserActivity.objects.create(**activity_data)


def track_activity(action_type, detail_func=None):
    """
    활동 추적 데코레이터

    Args:
        action_type: 활동 유형
        detail_func: 상세 설명 생성 함수 (request, *args, **kwargs를 받아 문자열 반환)
                    또는 고정 문자열

    Usage:
        @track_activity('export_pdf', '기저유출 PDF 다운로드')
        def export_baseflow_pdf(request, pk):
            ...

        @track_activity('save', lambda r, *a, **k: f"분석 저장: {k.get('pk')}")
        def save_analysis(request, pk):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)

            # 성공적인 응답이고 인증된 사용자인 경우에만 기록
            if hasattr(response, 'status_code') and response.status_code < 400:
                if request.user.is_authenticated:
                    # 상세 설명 생성
                    if callable(detail_func):
                        detail = detail_func(request, *args, **kwargs)
                    else:
                        detail = detail_func or view_func.__name__

                    log_activity(
                        user=request.user,
                        action_type=action_type,
                        detail=detail,
                        request=request
                    )

            return response
        return wrapper
    return decorator
