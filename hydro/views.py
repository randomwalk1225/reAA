from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .services import (
    get_realtime_waterlevel,
    get_realtime_rainfall,
    get_waterlevel_history,
    get_rainfall_history,
    get_stations_data,
    get_major_stations_data,
    search_stations,
    ALL_STATIONS,
    DEFAULT_STATIONS,
    STATION_DATABASE,
)
from .gee_service import (
    get_vegetation_indices,
    calculate_water_balance_et,
    is_gee_available,
    KOREA_LOCATIONS,
)


def dashboard(request):
    """실시간 수문 데이터 대시보드 - 비동기 로딩"""
    # 쿠키에서 선택된 관측소 가져오기 (없으면 기본값)
    wl_selected = request.COOKIES.get('hydro_wl_stations', '')
    rf_selected = request.COOKIES.get('hydro_rf_stations', '')

    wl_codes = wl_selected.split(',') if wl_selected else DEFAULT_STATIONS['waterlevel']
    rf_codes = rf_selected.split(',') if rf_selected else DEFAULT_STATIONS['rainfall']

    # 페이지만 먼저 렌더링, 데이터는 AJAX로 로드
    return render(request, 'hydro/dashboard.html', {
        'waterlevel_data': [],
        'rainfall_data': [],
        'updated_at': '로딩 중...',
        'all_waterlevel_stations': ALL_STATIONS['waterlevel'],
        'all_rainfall_stations': ALL_STATIONS['rainfall'],
        'selected_wl_stations': wl_codes,
        'selected_rf_stations': rf_codes,
        'async_load': True,
    })


@require_GET
def api_waterlevel(request):
    """API: 실시간 수위 데이터"""
    station_code = request.GET.get('station')
    data = get_realtime_waterlevel(station_code)

    return JsonResponse({
        'data': [
            {
                'station_code': item.get('wlobscd'),
                'station_name': item.get('station_name'),
                'water_level': item.get('wl'),
                'flow_rate': item.get('fw'),
                'time': item.get('time_str'),
            }
            for item in data
        ],
        'count': len(data),
    })


@require_GET
def api_rainfall(request):
    """API: 실시간 강수량 데이터"""
    station_code = request.GET.get('station')
    data = get_realtime_rainfall(station_code)

    return JsonResponse({
        'data': [
            {
                'station_code': item.get('rfobscd'),
                'station_name': item.get('station_name'),
                'rainfall': item.get('rf'),
                'time': item.get('time_str'),
            }
            for item in data
        ],
        'count': len(data),
    })


@require_GET
def api_waterlevel_history(request):
    """API: 기간별 수위 데이터"""
    station_code = request.GET.get('station', '1018683')  # 기본: 한강대교
    start = request.GET.get('start')
    end = request.GET.get('end')

    if not start or not end:
        return JsonResponse({'error': 'start and end parameters required'}, status=400)

    data = get_waterlevel_history(station_code, start, end)

    return JsonResponse({
        'station': station_code,
        'data': [
            {
                'time': item.get('time_str'),
                'water_level': item.get('wl'),
                'flow_rate': item.get('fw'),
            }
            for item in data
        ],
        'count': len(data),
    })


@require_GET
def api_major_stations(request):
    """API: 선택된 관측소 실시간 데이터"""
    # 쿼리 파라미터로 관측소 선택 지원
    wl_param = request.GET.get('wl_stations', '')
    rf_param = request.GET.get('rf_stations', '')

    wl_codes = wl_param.split(',') if wl_param else None
    rf_codes = rf_param.split(',') if rf_param else None

    data = get_stations_data(wl_codes, rf_codes)

    return JsonResponse({
        'waterlevel': [
            {
                'station_code': item.get('wlobscd'),
                'station_name': item.get('station_name'),
                'water_level': item.get('wl'),
                'flow_rate': item.get('fw'),
                'time': item.get('time_str'),
            }
            for item in data['waterlevel']
        ],
        'rainfall': [
            {
                'station_code': item.get('rfobscd'),
                'station_name': item.get('station_name'),
                'rainfall': item.get('rf'),
                'time': item.get('time_str'),
            }
            for item in data['rainfall']
        ],
        'updated_at': data['updated_at'],
    })


@require_GET
def api_all_stations(request):
    """API: 전체 관측소 목록"""
    return JsonResponse({
        'waterlevel': [
            {'code': code, 'name': name}
            for code, name in ALL_STATIONS['waterlevel'].items()
        ],
        'rainfall': [
            {'code': code, 'name': name}
            for code, name in ALL_STATIONS['rainfall'].items()
        ],
    })


@require_GET
def api_search_stations(request):
    """API: 관측소 검색 (지점명, 하천명, DM코드)"""
    query = request.GET.get('q', '')
    limit = int(request.GET.get('limit', 20))

    results = search_stations(query, limit)

    return JsonResponse({
        'query': query,
        'results': results,
        'count': len(results),
    })


# ============================================
# Google Earth Engine - 증발산량 분석
# ============================================

def et_dashboard(request):
    """증발산량(ET) 분석 대시보드"""
    return render(request, 'hydro/et_dashboard.html', {
        'locations': KOREA_LOCATIONS,
        'gee_available': is_gee_available(),
    })


@require_GET
def api_vegetation_indices(request):
    """API: 위성기반 식생지수 조회 (NDVI, NDMI, NDWI)"""
    try:
        lat = float(request.GET.get('lat', 37.5665))
        lon = float(request.GET.get('lon', 126.9780))
        date = request.GET.get('date')  # YYYY-MM-DD 또는 None

        result = get_vegetation_indices(lat, lon, date)

        return JsonResponse(result)

    except ValueError as e:
        return JsonResponse({'error': f'잘못된 좌표값: {e}', 'status': 'error'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)


@require_GET
def api_calculate_et(request):
    """API: 증발산량(ET) 계산"""
    try:
        lat = float(request.GET.get('lat', 37.5665))
        lon = float(request.GET.get('lon', 126.9780))
        et0 = float(request.GET.get('et0', 5.0))  # 기준증발산량 (mm/day)
        date = request.GET.get('date')

        result = calculate_water_balance_et(lat, lon, et0, date)

        return JsonResponse(result)

    except ValueError as e:
        return JsonResponse({'error': f'잘못된 파라미터: {e}', 'status': 'error'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e), 'status': 'error'}, status=500)


@require_GET
def api_preset_locations(request):
    """API: 사전정의된 한국 주요 지점 목록"""
    return JsonResponse({
        'locations': [
            {'name': name, 'lat': coords['lat'], 'lon': coords['lon']}
            for name, coords in KOREA_LOCATIONS.items()
        ]
    })
