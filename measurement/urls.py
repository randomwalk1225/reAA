from django.urls import path
from . import views

app_name = 'measurement'

urlpatterns = [
    # 측정 관리
    path('', views.measurement_list, name='list'),
    path('new/', views.measurement_new, name='new'),
    path('<int:pk>/', views.measurement_detail, name='detail'),
    path('<int:pk>/edit/', views.measurement_edit, name='edit'),
    path('<int:pk>/delete/', views.measurement_delete, name='delete'),

    # 데이터 입력 및 결과
    path('data-input/', views.data_input, name='data_input'),
    path('result/', views.result, name='result'),

    # 사전 불확실도
    path('pre-uncertainty/', views.pre_uncertainty, name='pre_uncertainty'),

    # 유속계 관리
    path('meters/', views.meters, name='meters'),

    # 내보내기
    path('export/excel/', views.export_excel, name='export_excel'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),

    # 수위-유량곡선 (Rating Curve)
    path('rating-curve/', views.rating_curve_list, name='rating_curve_list'),
    path('rating-curve/new/', views.rating_curve_new, name='rating_curve_new'),
    path('rating-curve/<int:pk>/', views.rating_curve_detail, name='rating_curve_detail'),
    path('rating-curve/fit/', views.fit_rating_curve, name='fit_rating_curve'),
    path('api/rating-curve/save/', views.api_rating_curve_save, name='api_rating_curve_save'),

    # 시계열 데이터
    path('timeseries/', views.timeseries_list, name='timeseries_list'),
    path('timeseries/upload/', views.timeseries_upload, name='timeseries_upload'),
    path('timeseries/<int:station_id>/', views.timeseries_detail, name='timeseries_detail'),
    path('timeseries/generate-discharge/', views.generate_discharge_series, name='generate_discharge_series'),

    # 기저유출 분석
    path('baseflow/', views.baseflow_list, name='baseflow_list'),
    path('baseflow/new/', views.baseflow_new, name='baseflow_new'),
    path('baseflow/<int:pk>/', views.baseflow_detail, name='baseflow_detail'),
    path('baseflow/<int:pk>/pdf/', views.export_baseflow_pdf, name='export_baseflow_pdf'),
    path('baseflow/run/', views.run_baseflow_analysis, name='run_baseflow_analysis'),
    path('baseflow/save/', views.save_baseflow_analysis, name='save_baseflow_analysis'),

    # 측정 데이터 자동저장 및 히스토리 API
    path('api/session/autosave/', views.api_measurement_autosave, name='api_measurement_autosave'),
    path('api/session/history/', views.api_measurement_history, name='api_measurement_history'),
    path('api/session/<int:session_id>/load/', views.api_measurement_load, name='api_measurement_load'),
    path('api/session/<int:session_id>/delete/', views.api_measurement_delete, name='api_measurement_delete'),
    path('api/result/save/', views.api_result_save, name='api_result_save'),

    # 관측소 및 H-Q 곡선 API
    path('api/stations/search/', views.api_stations_search, name='api_stations_search'),
    path('api/stations/<int:station_id>/rating-curves/', views.api_rating_curves_by_station, name='api_rating_curves_by_station'),

    # HRFCO API 연동
    path('api/hrfco/discharge/', views.api_hrfco_discharge, name='api_hrfco_discharge'),

    # 내부 관측소 유량 API
    path('api/internal/discharge/', views.api_internal_discharge, name='api_internal_discharge'),

    # 개발용: 모의 데이터 생성
    path('api/dev/create-mock-data/', views.api_create_mock_data, name='api_create_mock_data'),
    path('api/dev/create-sample-upstream/', views.api_create_sample_upstream_downstream, name='api_create_sample_upstream'),

    # 유속계 API
    path('api/meters/', views.api_meters_list, name='api_meters_list'),
    path('api/meters/create/', views.api_meters_create, name='api_meters_create'),
    path('api/meters/<int:meter_id>/update/', views.api_meters_update, name='api_meters_update'),
    path('api/meters/<int:meter_id>/delete/', views.api_meters_delete, name='api_meters_delete'),

    # 분석결과표
    path('analysis/', views.analysis_summary_view, name='analysis_summary'),
    path('api/analysis/summary/', views.api_analysis_summary, name='api_analysis_summary'),
    path('api/analysis/<int:session_id>/recalculate/', views.api_analysis_recalculate, name='api_analysis_recalculate'),
    path('api/analysis/export/', views.api_analysis_export, name='api_analysis_export'),

    # 데이터 임포트
    path('api/import/parquet/', views.api_parquet_import, name='api_parquet_import'),
]
