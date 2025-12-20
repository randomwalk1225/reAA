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

    # 시계열 데이터
    path('timeseries/', views.timeseries_list, name='timeseries_list'),
    path('timeseries/upload/', views.timeseries_upload, name='timeseries_upload'),
    path('timeseries/<int:station_id>/', views.timeseries_detail, name='timeseries_detail'),
    path('timeseries/generate-discharge/', views.generate_discharge_series, name='generate_discharge_series'),

    # 기저유출 분석
    path('baseflow/', views.baseflow_list, name='baseflow_list'),
    path('baseflow/new/', views.baseflow_new, name='baseflow_new'),
    path('baseflow/<int:pk>/', views.baseflow_detail, name='baseflow_detail'),
    path('baseflow/run/', views.run_baseflow_analysis, name='run_baseflow_analysis'),
]
