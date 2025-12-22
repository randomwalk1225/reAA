from django.urls import path
from . import views

app_name = 'hydro'

urlpatterns = [
    # 대시보드
    path('', views.dashboard, name='dashboard'),

    # API 엔드포인트
    path('api/waterlevel/', views.api_waterlevel, name='api_waterlevel'),
    path('api/rainfall/', views.api_rainfall, name='api_rainfall'),
    path('api/waterlevel/history/', views.api_waterlevel_history, name='api_waterlevel_history'),
    path('api/stations/', views.api_major_stations, name='api_stations'),
    path('api/stations/all/', views.api_all_stations, name='api_all_stations'),
    path('api/stations/search/', views.api_search_stations, name='api_search_stations'),

    # 증발산량(ET) 분석 - Google Earth Engine
    path('et/', views.et_dashboard, name='et_dashboard'),
    path('api/et/indices/', views.api_vegetation_indices, name='api_vegetation_indices'),
    path('api/et/calculate/', views.api_calculate_et, name='api_calculate_et'),
    path('api/et/locations/', views.api_preset_locations, name='api_preset_locations'),

    # 내 기록
    path('my-history/', views.my_history, name='my_history'),
    path('api/my/et-history/', views.api_my_et_history, name='api_my_et_history'),

    # 댐 수문 방류정보 API
    path('api/dam/discharges/', views.api_dam_discharges, name='api_dam_discharges'),
    path('api/dam/check-influence/', views.api_check_dam_influence, name='api_check_dam_influence'),
    path('api/dam/list/', views.api_dam_list, name='api_dam_list'),

    # 관측소 데이터 API (파일 기반)
    path('api/v2/stations/rivers/', views.api_station_rivers, name='api_station_rivers'),
    path('api/v2/stations/search/', views.api_station_search, name='api_station_search'),
    path('api/v2/stations/<str:code>/', views.api_station_detail, name='api_station_detail'),
    path('api/v2/stations/stats/', views.api_station_stats, name='api_station_stats'),

    # 디버그 (임시)
    path('api/debug/env/', views.api_debug_env, name='api_debug_env'),
]
