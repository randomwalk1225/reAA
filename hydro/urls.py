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
]
