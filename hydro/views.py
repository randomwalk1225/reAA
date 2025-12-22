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
from .dam_discharge_service import (
    fetch_dam_discharge_info,
    check_dam_influence,
    get_today_discharges,
    get_active_discharges,
    DAM_INFO,
    STATION_UPSTREAM_DAMS,
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
        location_name = request.GET.get('location', '')

        result = calculate_water_balance_et(lat, lon, et0, date)

        # 로그인 사용자면 조회 기록 저장
        if request.user.is_authenticated and result.get('status') == 'success':
            from .models import ETQuery
            from datetime import datetime
            from core.tracking import log_activity

            query_date = None
            if date:
                try:
                    query_date = datetime.strptime(date, '%Y-%m-%d').date()
                except:
                    pass

            et_query = ETQuery.objects.create(
                user=request.user,
                location_name=location_name,
                latitude=lat,
                longitude=lon,
                query_date=query_date,
                et0=et0,
                ndvi=result.get('ndvi'),
                ndmi=result.get('ndmi'),
                ndwi=result.get('ndwi'),
                kc=result.get('kc'),
                et_actual=result.get('et_actual'),
                soil_moisture=result.get('soil_moisture'),
                stress_index=result.get('stress_index'),
                raw_response=result,
            )

            # 활동 로그
            log_activity(
                user=request.user,
                action_type='analysis',
                detail=f'증발산량 조회: {location_name or f"({lat:.4f}, {lon:.4f})"}',
                related_object=et_query,
                request=request
            )

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


@require_GET
def api_my_et_history(request):
    """API: 내 증발산량 조회 기록"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)

    from .models import ETQuery

    limit = int(request.GET.get('limit', 20))
    queries = ETQuery.objects.filter(user=request.user)[:limit]

    return JsonResponse({
        'history': [
            {
                'id': q.id,
                'location_name': q.location_name,
                'latitude': q.latitude,
                'longitude': q.longitude,
                'query_date': q.query_date.isoformat() if q.query_date else None,
                'et0': q.et0,
                'ndvi': q.ndvi,
                'et_actual': q.et_actual,
                'created_at': q.created_at.isoformat(),
            }
            for q in queries
        ],
        'count': queries.count(),
    })


def my_history(request):
    """내 조회/분석 기록 페이지"""
    if not request.user.is_authenticated:
        from django.shortcuts import redirect
        return redirect('account_login')

    from .models import ETQuery

    et_queries = ETQuery.objects.filter(user=request.user)[:20]

    return render(request, 'hydro/my_history.html', {
        'et_queries': et_queries,
    })


@require_GET
def api_debug_env(request):
    """디버그: GEE 환경변수 확인 (값은 숨김)"""
    import os

    gee_vars = {}
    for key in os.environ:
        if key.startswith('GEE_') or key.startswith('GOOGLE_'):
            val = os.environ.get(key, '')
            # 값이 있으면 길이와 처음 몇 글자만 표시
            if val:
                gee_vars[key] = f"SET (len={len(val)}, start={val[:20]}...)"
            else:
                gee_vars[key] = "EMPTY"

    # 모든 환경변수 이름만 (디버그용)
    all_env_keys = sorted([k for k in os.environ.keys()])

    return JsonResponse({
        'gee_variables': gee_vars,
        'all_env_count': len(all_env_keys),
        'all_env_keys': all_env_keys,  # 키만 노출
    })


# ============================================
# 댐 수문 방류정보 API
# ============================================

@require_GET
def api_dam_discharges(request):
    """
    API: 댐 수문 방류정보 조회

    Query params:
        date: 조회일 (YYYYMMDD, 기본 오늘)
        active_only: 현재 진행 중인 방류만 (true/false)
    """
    from datetime import datetime

    date_str = request.GET.get('date')
    active_only = request.GET.get('active_only', 'false').lower() == 'true'

    if active_only:
        discharges = get_active_discharges()
    elif date_str:
        discharges = fetch_dam_discharge_info(start_date=date_str, end_date=date_str)
    else:
        discharges = get_today_discharges()

    return JsonResponse({
        'discharges': [
            {
                'dam_code': d.get('dam_code'),
                'dam_name': d.get('dam_name'),
                'start_time': d.get('start_date'),
                'end_time': d.get('end_date'),
                'affect_area': d.get('affect_area'),
                'updated_at': d.get('updated_date'),
            }
            for d in discharges
        ],
        'count': len(discharges),
        'active_only': active_only,
    })


@require_GET
def api_check_dam_influence(request):
    """
    API: 관측소에서 특정 시각의 댐 방류 영향 여부 확인

    Query params:
        station: 관측소 코드 (필수)
        datetime: 측정 시각 (YYYY-MM-DD HH:MM 또는 YYYYMMDDHHmm, 기본 현재)
    """
    from datetime import datetime

    station_code = request.GET.get('station')
    datetime_str = request.GET.get('datetime')

    if not station_code:
        return JsonResponse({'error': 'station 파라미터가 필요합니다.'}, status=400)

    # 시간 파싱
    if datetime_str:
        measurement_time = None
        for fmt in ['%Y-%m-%d %H:%M', '%Y%m%d%H%M', '%Y-%m-%dT%H:%M']:
            try:
                measurement_time = datetime.strptime(datetime_str, fmt)
                break
            except ValueError:
                continue
        if not measurement_time:
            return JsonResponse({'error': '잘못된 datetime 형식입니다.'}, status=400)
    else:
        measurement_time = datetime.now()

    # 댐 영향 확인
    result = check_dam_influence(station_code, measurement_time)

    return JsonResponse({
        'station_code': station_code,
        'measurement_time': measurement_time.strftime('%Y-%m-%d %H:%M'),
        'is_influenced': result['is_influenced'],
        'influencing_dams': [
            {
                'dam_name': d['dam_name'],
                'river': d['river'],
                'start_time': d['start_time'].strftime('%Y-%m-%d %H:%M') if d['start_time'] else None,
                'end_time': d['end_time'].strftime('%Y-%m-%d %H:%M') if d['end_time'] else None,
                'affect_area': d['affect_area'],
                'travel_time_hours': d['travel_time_hours'],
            }
            for d in result['influencing_dams']
        ],
        'message': result['message'],
    })


@require_GET
def api_dam_list(request):
    """API: 댐 목록 및 관측소-댐 매핑 정보"""
    return JsonResponse({
        'dams': [
            {
                'key': key,
                'code': info['code'],
                'name': info['name'],
                'river': info['river'],
            }
            for key, info in DAM_INFO.items()
        ],
        'station_dam_mapping': {
            station_code: [
                {
                    'dam_key': upstream['dam'],
                    'dam_name': DAM_INFO.get(upstream['dam'], {}).get('name', upstream['dam']),
                    'travel_time_hours': upstream['travel_time_hours'],
                }
                for upstream in upstreams
            ]
            for station_code, upstreams in STATION_UPSTREAM_DAMS.items()
        },
    })
