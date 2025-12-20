from django.urls import path
from . import views

app_name = 'satellite'

urlpatterns = [
    # 메인 뷰어 페이지
    path('', views.satellite_viewer, name='viewer'),

    # API 엔드포인트
    path('api/frames/', views.api_frames, name='api_frames'),
    path('api/frames/latest/', views.api_latest_frame, name='api_latest'),
    path('api/refresh/', views.api_refresh, name='api_refresh'),

    # CORS 우회용 프록시
    path('proxy/', views.proxy_image, name='proxy_image'),
]
