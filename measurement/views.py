from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from datetime import datetime, timedelta
import json
import math


def measurement_list(request):
    """측정 목록"""
    from .models import MeasurementSession

    # DB에서 측정 세션 조회 (모든 사용자)
    sessions = MeasurementSession.objects.order_by('-updated_at')[:50]

    measurements = []
    for s in sessions:
        measurements.append({
            'id': s.pk,
            'station_name': s.station_name or '미지정',
            'river_name': '',
            'measurement_date': s.measurement_date.strftime('%Y-%m-%d') if s.measurement_date else '-',
            'discharge': s.estimated_discharge or 0,
            'uncertainty': '-',
            'status': 'completed' if s.estimated_discharge else 'draft',
            'session_number': s.session_number,
            'updated_at': s.updated_at.strftime('%Y-%m-%d %H:%M') if s.updated_at else '',
        })

    return render(request, 'measurement/list.html', {
        'measurements': measurements,
    })


def measurement_new(request):
    """새 측정 생성 마법사"""
    if request.method == 'POST':
        # 폼 처리 (추후 구현)
        return redirect('measurement:data_input')
    return render(request, 'measurement/new.html')


def measurement_detail(request, pk):
    """측정 상세 (결과 보기) - DB에서 데이터 로드"""
    from .models import MeasurementSession

    session = get_object_or_404(MeasurementSession, pk=pk)

    # 세션에 rows_data가 있으면 계산 수행, 없으면 저장된 값 사용
    if session.rows_data:
        calibration = session.calibration_data or {'a': 0.0012, 'b': 0.2534}
        result_data = calculate_discharge(session.rows_data, calibration)
    else:
        # rows_data가 없으면 저장된 값으로 표시
        setup = session.setup_data or {}
        result_data = {
            'discharge': session.estimated_discharge or 0,
            'area': session.total_area or 0,
            'width': session.total_width or 0,
            'avg_depth': session.max_depth or 0,
            'avg_velocity': setup.get('final_avg_velocity', 0),
            'max_velocity': 0,
            'min_velocity': 0,
            'uncertainty': setup.get('final_uncertainty', 0),
            'uncertainty_abs': 0,
            'verticals': [],
        }
        if result_data['discharge'] and result_data['uncertainty']:
            result_data['uncertainty_abs'] = round(
                result_data['discharge'] * result_data['uncertainty'] / 100, 3
            )

    # 세션 정보 추가
    result_data['session_id'] = session.pk
    result_data['station_name'] = session.station_name or ''
    result_data['measurement_date'] = session.measurement_date.strftime('%Y-%m-%d') if session.measurement_date else ''
    result_data['setup_data'] = session.setup_data or {}

    # measurement 객체도 전달 (템플릿 호환성)
    result_data['measurement'] = {
        'id': session.pk,
        'station_name': session.station_name,
        'date': result_data['measurement_date'],
    }

    return render(request, 'measurement/result.html', result_data)


def measurement_edit(request, pk):
    """측정 수정 - 세션 ID를 전달하여 data_input으로 이동"""
    return redirect(f'/measurement/data-input/?session_id={pk}')


def measurement_delete(request, pk):
    """측정 삭제"""
    from .models import MeasurementSession

    if request.method == 'DELETE':
        try:
            session = MeasurementSession.objects.get(pk=pk)
            session.delete()
            return HttpResponse(status=200)
        except MeasurementSession.DoesNotExist:
            return HttpResponse(status=404)
    return HttpResponse(status=405)


def data_input(request):
    """데이터 입력 그리드"""
    from django.conf import settings
    return render(request, 'measurement/data_input.html', {
        'debug': settings.DEBUG,
    })


def result(request):
    """계산 결과"""
    from .models import MeasurementSession

    # GET 요청: session_id로 데이터 로드 후 계산 (권장 방식)
    session_id = request.GET.get('session_id')
    if session_id:
        try:
            session = MeasurementSession.objects.get(pk=session_id)
            rows = session.rows_data or []
            calibration = session.calibration_data or {'a': 0.0012, 'b': 0.2534}

            # 계산 수행
            result_data = calculate_discharge(rows, calibration)

            # 세션 정보 추가
            result_data['session_id'] = session.pk
            result_data['station_name'] = session.station_name or ''
            result_data['measurement_date'] = session.measurement_date.strftime('%Y-%m-%d') if session.measurement_date else ''
            result_data['setup_data'] = session.setup_data or {}

            # 계산 결과를 세션에 저장 (자동 저장)
            session.estimated_discharge = result_data['discharge']
            session.total_area = result_data['area']
            session.total_width = result_data['width']
            session.max_depth = result_data['avg_depth']
            if not session.setup_data:
                session.setup_data = {}
            session.setup_data['final_discharge'] = result_data['discharge']
            session.setup_data['final_uncertainty'] = result_data['uncertainty']
            session.setup_data['final_avg_velocity'] = result_data['avg_velocity']
            session.save()

            return render(request, 'measurement/result.html', result_data)
        except MeasurementSession.DoesNotExist:
            return render(request, 'measurement/result.html', {'error': '세션을 찾을 수 없습니다.'})

    # POST 요청: 레거시 방식 (deprecated - 추후 제거 예정)
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rows = data.get('rows', [])
            calibration = data.get('calibration', {'a': 0.0012, 'b': 0.2534})

            # 세션 정보 추출
            session_id = data.get('session_id')
            station_name = data.get('station_name', '')
            measurement_date = data.get('measurement_date', '')
            setup_data = data.get('setup_data', {})

            # 계산 수행
            result_data = calculate_discharge(rows, calibration)

            # 세션 정보 추가
            result_data['session_id'] = session_id
            result_data['station_name'] = station_name
            result_data['measurement_date'] = measurement_date
            result_data['setup_data'] = setup_data

            return render(request, 'measurement/result.html', result_data)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    return render(request, 'measurement/result.html')


def calculate_discharge(rows, calibration):
    """
    유량 계산 (ISO 748 중앙단면법)

    Returns dict with:
    - discharge: 총 유량 (m³/s)
    - area: 총 단면적 (m²)
    - avg_velocity: 평균유속 (m/s)
    - uncertainty: 불확실도 (%)
    - verticals: 각 측선별 상세 결과
    """
    a = calibration.get('a', 0.0012)
    b = calibration.get('b', 0.2534)

    def calc_velocity(n, t):
        """프로펠러 유속계 유속 계산: V = a + b * (N/T)"""
        if not n or not t or t == 0:
            return 0
        return a + b * (n / t)

    # 각 측선별 유속 계산
    verticals = []
    for i, row in enumerate(rows):
        method = row.get('method', '1')
        velocity = 0

        if method == '1':  # 1점법
            velocity = calc_velocity(row.get('n_06d'), row.get('t_06d'))
        elif method == '2':  # 2점법
            v02 = calc_velocity(row.get('n_02d'), row.get('t_02d'))
            v08 = calc_velocity(row.get('n_08d'), row.get('t_08d'))
            if v02 and v08:
                velocity = (v02 + v08) / 2
        elif method == '3':  # 3점법
            v02 = calc_velocity(row.get('n_02d'), row.get('t_02d'))
            v06 = calc_velocity(row.get('n_06d'), row.get('t_06d'))
            v08 = calc_velocity(row.get('n_08d'), row.get('t_08d'))
            if v02 and v06 and v08:
                velocity = (v02 + 2 * v06 + v08) / 4

        verticals.append({
            'id': i + 1,
            'distance': float(row.get('distance', 0) or 0),
            'depth': float(row.get('depth', 0) or 0),
            'velocity': velocity,
            'method': method,
            'area': 0,
            'discharge': 0,
            'ratio': 0
        })

    # 중앙단면법으로 유량 계산
    total_discharge = 0
    total_area = 0

    for i in range(1, len(verticals)):
        prev = verticals[i - 1]
        curr = verticals[i]

        width = curr['distance'] - prev['distance']
        avg_depth = (curr['depth'] + prev['depth']) / 2
        avg_velocity = (curr['velocity'] + prev['velocity']) / 2

        section_area = width * avg_depth
        section_discharge = section_area * avg_velocity

        # 현재 측선에 값 저장 (중앙단면법에서 각 구간의 값)
        curr['width'] = width
        curr['area'] = section_area
        curr['discharge'] = section_discharge

        total_area += section_area
        total_discharge += section_discharge

    # 비율 계산
    for v in verticals:
        if total_discharge > 0:
            v['ratio'] = (v['discharge'] / total_discharge) * 100

    # 평균유속
    avg_velocity = total_discharge / total_area if total_area > 0 else 0

    # 최대/최소 유속 (0이 아닌 값 중에서)
    velocities = [v['velocity'] for v in verticals if v['velocity'] > 0]
    max_velocity = max(velocities) if velocities else 0
    min_velocity = min(velocities) if velocities else 0

    # 하폭
    distances = [v['distance'] for v in verticals]
    total_width = max(distances) - min(distances) if distances else 0

    # 평균수심
    avg_depth = total_area / total_width if total_width > 0 else 0

    # ISO 748 불확실도 계산 (간략화)
    n_verticals = len([v for v in verticals if v['velocity'] > 0])

    # Xe: 측점 불확실도 (측선 수에 따라)
    if n_verticals >= 20:
        Xe = 1.0
    elif n_verticals >= 10:
        Xe = 2.0
    else:
        Xe = 3.0

    # Xp: 수심측정 불확실도
    Xp = 2.0

    # Xc: 검정 불확실도
    Xc = 1.0

    # Xm: 측정 불확실도 (측정법에 따라)
    methods = [v['method'] for v in verticals if v['method'] in ['1', '2', '3']]
    if methods:
        method_uncertainties = {'1': 3.0, '2': 2.5, '3': 2.0}
        Xm = sum(method_uncertainties.get(m, 3.0) for m in methods) / len(methods)
    else:
        Xm = 3.0

    # 합성불확실도 (RSS)
    import math
    combined_uncertainty = math.sqrt(Xe**2 + Xp**2 + Xc**2 + Xm**2)

    # 확장불확실도 (95%, k=2)
    expanded_uncertainty = combined_uncertainty * 2
    uncertainty_abs = total_discharge * expanded_uncertainty / 100

    return {
        'discharge': round(total_discharge, 3),
        'area': round(total_area, 2),
        'avg_velocity': round(avg_velocity, 3),
        'max_velocity': round(max_velocity, 3),
        'min_velocity': round(min_velocity, 3),
        'width': round(total_width, 1),
        'avg_depth': round(avg_depth, 2),
        'uncertainty': round(expanded_uncertainty, 1),
        'uncertainty_abs': round(uncertainty_abs, 3),
        'Xe': round(Xe, 1),
        'Xp': round(Xp, 1),
        'Xc': round(Xc, 1),
        'Xm': round(Xm, 1),
        'combined_uncertainty': round(combined_uncertainty, 1),
        'verticals': verticals,
        'n_verticals': n_verticals,
    }


def pre_uncertainty(request):
    """사전 불확실도 분석"""
    return render(request, 'measurement/pre_uncertainty.html')


def meters(request):
    """유속계 관리"""
    return render(request, 'measurement/meters.html')


def export_excel(request):
    """Excel 다운로드 - session_id로 DB에서 데이터 로드"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
    from .models import MeasurementSession

    session_id = request.GET.get('session_id')

    if session_id:
        try:
            session = MeasurementSession.objects.get(pk=session_id)
            calibration = session.calibration_data or {'a': 0.0012, 'b': 0.2534}

            if session.rows_data:
                result = calculate_discharge(session.rows_data, calibration)
                rows = []
                for v in result.get('verticals', []):
                    rows.append({
                        'no': v['id'],
                        'distance': v['distance'],
                        'depth': v['depth'],
                        'velocity': round(v['velocity'], 3),
                        'area': round(v.get('area', 0), 3),
                        'discharge': round(v.get('discharge', 0), 3),
                        'ratio': round(v.get('ratio', 0), 1),
                    })
                data = {
                    'station_name': session.station_name or '미지정',
                    'date': session.measurement_date.strftime('%Y-%m-%d') if session.measurement_date else '-',
                    'discharge': result['discharge'],
                    'uncertainty': result['uncertainty'],
                    'area': result['area'],
                    'avg_velocity': result['avg_velocity'],
                    'rows': rows,
                }
            else:
                setup = session.setup_data or {}
                data = {
                    'station_name': session.station_name or '미지정',
                    'date': session.measurement_date.strftime('%Y-%m-%d') if session.measurement_date else '-',
                    'discharge': session.estimated_discharge or 0,
                    'uncertainty': setup.get('final_uncertainty', 0),
                    'area': session.total_area or 0,
                    'avg_velocity': setup.get('final_avg_velocity', 0),
                    'rows': [],
                }
        except MeasurementSession.DoesNotExist:
            return HttpResponse('세션을 찾을 수 없습니다.', status=404)
    else:
        return HttpResponse('session_id 파라미터가 필요합니다.', status=400)

    wb = Workbook()
    ws = wb.active
    ws.title = "유량측정 결과"

    # 스타일 정의
    header_font = Font(bold=True, size=12)
    title_font = Font(bold=True, size=14)
    header_fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
    header_font_white = Font(bold=True, color="FFFFFF")
    thin_border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
    )
    center_align = Alignment(horizontal='center', vertical='center')

    # 제목
    ws['A1'] = "유량측정 결과 보고서"
    ws['A1'].font = title_font
    ws.merge_cells('A1:G1')

    # 기본 정보
    ws['A3'] = "지점명"
    ws['B3'] = data['station_name']
    ws['A4'] = "측정일"
    ws['B4'] = data['date']
    ws['D3'] = "유량 (m³/s)"
    ws['E3'] = data['discharge']
    ws['D4'] = "불확실도 (%)"
    ws['E4'] = f"± {data['uncertainty']}"

    # 데이터 테이블 헤더 (7행부터)
    headers = ['측선', '거리 (m)', '수심 (m)', '유속 (m/s)', '단면적 (m²)', '유량 (m³/s)', '비율 (%)']
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=7, column=col, value=header)
        cell.font = header_font_white
        cell.fill = header_fill
        cell.alignment = center_align
        cell.border = thin_border

    # 데이터 행
    for row_idx, row_data in enumerate(data['rows'], 8):
        ws.cell(row=row_idx, column=1, value=row_data['no']).border = thin_border
        ws.cell(row=row_idx, column=2, value=row_data['distance']).border = thin_border
        ws.cell(row=row_idx, column=3, value=row_data['depth']).border = thin_border
        ws.cell(row=row_idx, column=4, value=row_data['velocity']).border = thin_border
        ws.cell(row=row_idx, column=5, value=row_data['area']).border = thin_border
        ws.cell(row=row_idx, column=6, value=row_data['discharge']).border = thin_border
        ws.cell(row=row_idx, column=7, value=row_data['ratio']).border = thin_border
        for col in range(1, 8):
            ws.cell(row=row_idx, column=col).alignment = center_align

    # 합계 행
    sum_row = 8 + len(data['rows'])
    ws.cell(row=sum_row, column=1, value='합계').font = Font(bold=True)
    ws.merge_cells(f'A{sum_row}:D{sum_row}')
    ws.cell(row=sum_row, column=5, value=data['area']).font = Font(bold=True)
    ws.cell(row=sum_row, column=6, value=data['discharge']).font = Font(bold=True)
    ws.cell(row=sum_row, column=7, value=100.0).font = Font(bold=True)
    for col in range(1, 8):
        ws.cell(row=sum_row, column=col).border = thin_border
        ws.cell(row=sum_row, column=col).alignment = center_align

    # 열 너비 조정
    ws.column_dimensions['A'].width = 10
    ws.column_dimensions['B'].width = 12
    ws.column_dimensions['C'].width = 12
    ws.column_dimensions['D'].width = 12
    ws.column_dimensions['E'].width = 14
    ws.column_dimensions['F'].width = 14
    ws.column_dimensions['G'].width = 12

    # 응답 생성
    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)

    filename = f"measurement_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def export_pdf(request):
    """PDF 출력 - session_id로 DB에서 데이터 로드"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from .models import MeasurementSession
    import os

    session_id = request.GET.get('session_id')

    if session_id:
        try:
            session = MeasurementSession.objects.get(pk=session_id)
            calibration = session.calibration_data or {'a': 0.0012, 'b': 0.2534}

            if session.rows_data:
                result = calculate_discharge(session.rows_data, calibration)
                rows = []
                for v in result.get('verticals', []):
                    rows.append([
                        v['id'],
                        v['distance'],
                        round(v['depth'], 2),
                        round(v['velocity'], 3),
                        round(v.get('area', 0), 3),
                        round(v.get('discharge', 0), 3),
                        f"{round(v.get('ratio', 0), 1)}%",
                    ])
                data = {
                    'station_name': session.station_name or '미지정',
                    'date': session.measurement_date.strftime('%Y-%m-%d') if session.measurement_date else '-',
                    'discharge': result['discharge'],
                    'uncertainty': result['uncertainty'],
                    'area': result['area'],
                    'avg_velocity': result['avg_velocity'],
                    'rows': rows,
                }
            else:
                setup = session.setup_data or {}
                data = {
                    'station_name': session.station_name or '미지정',
                    'date': session.measurement_date.strftime('%Y-%m-%d') if session.measurement_date else '-',
                    'discharge': session.estimated_discharge or 0,
                    'uncertainty': setup.get('final_uncertainty', 0),
                    'area': session.total_area or 0,
                    'avg_velocity': setup.get('final_avg_velocity', 0),
                    'rows': [],
                }
        except MeasurementSession.DoesNotExist:
            return HttpResponse('세션을 찾을 수 없습니다.', status=404)
    else:
        return HttpResponse('session_id 파라미터가 필요합니다.', status=400)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=20*mm, bottomMargin=20*mm)
    elements = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=12,
        alignment=1  # center
    )
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )

    # 제목
    elements.append(Paragraph("Discharge Measurement Report", title_style))
    elements.append(Paragraph("유량측정 결과 보고서", title_style))
    elements.append(Spacer(1, 10*mm))

    # 기본 정보 테이블
    info_data = [
        ['Station', data['station_name'], 'Date', data['date']],
        ['Discharge', f"{data['discharge']} m³/s", 'Uncertainty', f"± {data['uncertainty']}%"],
        ['Area', f"{data['area']} m²", 'Avg. Velocity', f"{data['avg_velocity']} m/s"],
    ]
    info_table = Table(info_data, colWidths=[35*mm, 55*mm, 35*mm, 45*mm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.9)),
        ('BACKGROUND', (2, 0), (2, -1), colors.Color(0.9, 0.9, 0.9)),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 10*mm))

    # 상세 데이터 테이블
    elements.append(Paragraph("Detailed Results by Vertical", styles['Heading2']))
    elements.append(Spacer(1, 5*mm))

    table_data = [['No.', 'Distance(m)', 'Depth(m)', 'Velocity(m/s)', 'Area(m²)', 'Discharge(m³/s)', 'Ratio']]
    table_data.extend(data['rows'])
    table_data.append(['Total', '', '', '', data['area'], data['discharge'], '100%'])

    detail_table = Table(table_data, colWidths=[15*mm, 25*mm, 22*mm, 28*mm, 22*mm, 32*mm, 20*mm])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.27, 0.45, 0.77)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.9, 0.9, 0.9)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(detail_table)
    elements.append(Spacer(1, 10*mm))

    # 불확실도 정보
    elements.append(Paragraph("Uncertainty Analysis (ISO 748)", styles['Heading2']))
    elements.append(Spacer(1, 5*mm))

    unc_data = [
        ['Component', 'Value', 'Description'],
        ['Xe', '1.8%', 'Limited number of verticals'],
        ['Xp', '2.1%', 'Depth measurement uncertainty'],
        ['Xc', '1.0%', 'Calibration uncertainty'],
        ['Xm', '2.8%', 'Velocity measurement uncertainty'],
        ['u(Q)', '4.2%', 'Combined standard uncertainty (RSS)'],
    ]
    unc_table = Table(unc_data, colWidths=[30*mm, 25*mm, 80*mm])
    unc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.27, 0.45, 0.77)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (1, -1), 'CENTER'),
        ('ALIGN', (2, 0), (2, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, -1), (-1, -1), colors.Color(0.85, 0.92, 0.98)),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(unc_table)

    doc.build(elements)
    buffer.seek(0)

    filename = f"measurement_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


def rating_curve_list(request):
    """수위-유량곡선 목록"""
    from .models import RatingCurve

    curves_qs = RatingCurve.objects.select_related('station').all()

    # 템플릿용 데이터 변환
    curves = []
    for curve in curves_qs:
        curves.append({
            'id': curve.pk,
            'station_name': curve.station.name,
            'year': curve.year,
            'curve_type': curve.get_curve_type_display(),
            'h_range': f'{curve.h_min:.2f} ≤ h ≤ {curve.h_max:.2f}',
            'equation': curve.get_equation_display(),
            'r_squared': curve.r_squared,
        })

    return render(request, 'measurement/rating_curve_list.html', {
        'curves': curves,
    })


def rating_curve_detail(request, pk):
    """수위-유량곡선 상세"""
    from .models import RatingCurve, HQDataPoint
    from django.shortcuts import get_object_or_404

    curve = get_object_or_404(RatingCurve.objects.select_related('station'), pk=pk)

    # 실측 데이터 조회
    data_points = HQDataPoint.objects.filter(rating_curve=curve).order_by('measured_date')
    data_points_list = [
        {
            'date': dp.measured_date.strftime('%Y-%m-%d'),
            'stage': dp.stage,
            'discharge': dp.discharge,
        }
        for dp in data_points
    ]

    curve_data = {
        'id': curve.pk,
        'station_name': curve.station.name,
        'year': curve.year,
        'curve_type': curve.curve_type,
        'curve_type_display': curve.get_curve_type_display(),
        'h_min': curve.h_min,
        'h_max': curve.h_max,
        'coef_a': curve.coef_a,
        'coef_b': curve.coef_b,
        'coef_h0': curve.coef_h0,
        'r_squared': curve.r_squared,
        'equation': curve.get_equation_display(),
        'data_points': data_points_list,
        'note': curve.note,
    }

    return render(request, 'measurement/rating_curve_detail.html', {
        'curve': curve_data,
    })


def rating_curve_new(request):
    """새 수위-유량곡선 생성"""
    return render(request, 'measurement/rating_curve_new.html')


@require_http_methods(["POST"])
def fit_rating_curve(request):
    """수위-유량 데이터로 곡선 피팅 (AJAX)"""
    import numpy as np
    from scipy.optimize import curve_fit

    try:
        data = json.loads(request.body)
        h_values = np.array(data.get('h', []))
        q_values = np.array(data.get('q', []))
        h0_fixed = data.get('h0', None)  # 고정 영점수위 (선택)

        if len(h_values) < 3 or len(q_values) < 3:
            return JsonResponse({'error': '최소 3개 이상의 데이터가 필요합니다.'}, status=400)

        # 멱함수: Q = a * (h - h0)^b
        if h0_fixed is not None:
            # h0 고정
            def power_func(h, a, b):
                return a * np.power(h - h0_fixed, b)

            popt, pcov = curve_fit(power_func, h_values, q_values, p0=[1, 1.5], maxfev=10000)
            a, b = popt
            h0 = h0_fixed
        else:
            # h0도 피팅
            def power_func_h0(h, a, b, h0):
                return a * np.power(np.maximum(h - h0, 1e-10), b)

            # 초기값 추정
            h0_init = min(h_values) * 0.9
            popt, pcov = curve_fit(power_func_h0, h_values, q_values, p0=[1, 1.5, h0_init], maxfev=10000)
            a, b, h0 = popt

        # 예측값 및 통계
        if h0_fixed is not None:
            q_pred = power_func(h_values, a, b)
        else:
            q_pred = power_func_h0(h_values, a, b, h0)

        # R² 계산
        ss_res = np.sum((q_values - q_pred) ** 2)
        ss_tot = np.sum((q_values - np.mean(q_values)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0

        # RMSE 계산
        rmse = np.sqrt(np.mean((q_values - q_pred) ** 2))

        # 곡선 데이터 생성 (그래프용)
        h_curve = np.linspace(min(h_values), max(h_values), 50)
        if h0_fixed is not None:
            q_curve = power_func(h_curve, a, b)
        else:
            q_curve = power_func_h0(h_curve, a, b, h0)

        return JsonResponse({
            'success': True,
            'coefficients': {
                'a': round(float(a), 6),
                'b': round(float(b), 6),
                'h0': round(float(h0), 6),
            },
            'statistics': {
                'r_squared': round(float(r_squared), 4),
                'rmse': round(float(rmse), 6),
            },
            'equation': f"Q = {a:.4f}(h - {h0:.4f})^{b:.4f}",
            'h_range': {
                'min': round(float(min(h_values)), 3),
                'max': round(float(max(h_values)), 3),
            },
            'curve_points': {
                'h': h_curve.tolist(),
                'q': q_curve.tolist(),
            },
            'fitted_values': q_pred.tolist(),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def api_rating_curve_save(request):
    """수위-유량곡선 저장 API"""
    from .models import Station, RatingCurve, HQDataPoint

    try:
        data = json.loads(request.body)

        station_name = data.get('station_name', '').strip()
        year = int(data.get('year', datetime.now().year))
        curve_type = data.get('curve_type', 'open')
        coef_a = float(data.get('coef_a', 0))
        coef_b = float(data.get('coef_b', 0))
        coef_h0 = float(data.get('coef_h0', 0))
        h_min = float(data.get('h_min', 0))
        h_max = float(data.get('h_max', 0))
        r_squared = data.get('r_squared')
        rmse = data.get('rmse')
        data_points = data.get('data_points', [])

        if not station_name:
            return JsonResponse({'error': '지점명을 입력하세요.'}, status=400)

        # 사용자 정보
        user = request.user if request.user.is_authenticated else None

        # Station 찾거나 생성
        station, created = Station.objects.get_or_create(
            name=station_name,
            defaults={'user': user}
        )

        # RatingCurve 생성
        rating_curve = RatingCurve.objects.create(
            user=user,
            station=station,
            year=year,
            curve_type=curve_type,
            h_min=h_min,
            h_max=h_max,
            coef_a=coef_a,
            coef_b=coef_b,
            coef_h0=coef_h0,
            r_squared=r_squared,
            rmse=rmse,
        )

        # 실측 데이터 저장
        for dp in data_points:
            if dp.get('h') and dp.get('q'):
                HQDataPoint.objects.create(
                    station=station,
                    rating_curve=rating_curve,
                    measured_date=dp.get('date') or datetime.now().date(),
                    stage=float(dp['h']),
                    discharge=float(dp['q']),
                )

        return JsonResponse({
            'success': True,
            'curve_id': rating_curve.pk,
            'message': '저장되었습니다.',
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def timeseries_list(request):
    """시계열 데이터 관리"""
    from .models import Station, WaterLevelTimeSeries, RatingCurve
    from django.db.models import Count, Min, Max

    # DB에서 수위 시계열 데이터가 있는 관측소 조회
    stations_with_data = WaterLevelTimeSeries.objects.values('station').annotate(
        data_count=Count('id'),
        first_time=Min('timestamp'),
        last_time=Max('timestamp'),
    )

    stations = []
    for item in stations_with_data:
        station = Station.objects.get(pk=item['station'])
        has_rating = RatingCurve.objects.filter(station=station).exists()

        first_time = item['first_time']
        last_time = item['last_time']
        period = f"{first_time.strftime('%Y-%m-%d')} ~ {last_time.strftime('%Y-%m-%d')}" if first_time and last_time else '-'

        stations.append({
            'id': station.pk,
            'name': station.name,
            'has_rating_curve': has_rating,
            'data_count': item['data_count'],
            'last_update': last_time.strftime('%Y-%m-%d %H:%M') if last_time else '-',
            'period': period,
        })

    return render(request, 'measurement/timeseries_list.html', {
        'stations': stations,
    })


def timeseries_upload(request):
    """수위 데이터 업로드"""
    from .models import Station, RatingCurve

    if request.method == 'POST':
        # CSV 파싱 및 저장 로직 (추후 구현)
        return JsonResponse({'success': True, 'message': '업로드 완료'})

    # 관측소 및 H-Q 곡선 목록
    stations = Station.objects.all().order_by('name')
    rating_curves = RatingCurve.objects.select_related('station').order_by('station__name', '-year')

    return render(request, 'measurement/timeseries_upload.html', {
        'stations': stations,
        'rating_curves': rating_curves,
    })


@require_GET
def api_stations_search(request):
    """관측소 검색 API"""
    from .models import Station

    query = request.GET.get('q', '').strip()
    limit = int(request.GET.get('limit', 20))

    stations = Station.objects.all()

    if query:
        stations = stations.filter(name__icontains=query)

    stations = stations.order_by('name')[:limit]

    results = []
    for s in stations:
        results.append({
            'id': s.pk,
            'name': s.name,
            'river_name': s.river_name or '',
        })

    return JsonResponse({
        'stations': results,
        'query': query,
    })


@require_GET
def api_rating_curves_by_station(request, station_id):
    """관측소별 H-Q 곡선 목록 API"""
    from .models import RatingCurve

    curves = RatingCurve.objects.filter(station_id=station_id).order_by('-year', 'curve_type')

    results = []
    for c in curves:
        results.append({
            'id': c.pk,
            'year': c.year,
            'curve_type': c.curve_type,
            'curve_type_display': c.get_curve_type_display(),
            'equation': c.get_equation_display(),
            'h_range': f'{c.h_min} ≤ h ≤ {c.h_max}',
        })

    return JsonResponse({
        'rating_curves': results,
        'station_id': station_id,
    })


def timeseries_detail(request, station_id):
    """관측소별 시계열 상세 - DB에서 데이터 로드"""
    from .models import Station, WaterLevelTimeSeries, RatingCurve

    station = get_object_or_404(Station, pk=station_id)

    # 수위 시계열 데이터 조회 (최신순 1000개)
    water_levels = WaterLevelTimeSeries.objects.filter(
        station=station
    ).order_by('-timestamp')[:1000]

    total_count = WaterLevelTimeSeries.objects.filter(station=station).count()

    # Rating Curve 조회 (가장 최신)
    rating_curve = RatingCurve.objects.filter(station=station).order_by('-year').first()

    # 시계열 데이터 변환
    data = []
    for wl in water_levels:
        discharge = None
        if rating_curve and wl.stage is not None:
            # Q = a * (h - h0) ^ b
            h_diff = wl.stage - rating_curve.coef_h0
            if h_diff > 0:
                discharge = round(rating_curve.coef_a * (h_diff ** rating_curve.coef_b), 4)

        data.append({
            'timestamp': wl.timestamp.strftime('%Y-%m-%d %H:%M'),
            'stage': wl.stage,
            'discharge': discharge,
        })

    # Rating Curve 수식 생성
    rating_curve_eq = None
    if rating_curve:
        rating_curve_eq = f"Q = {rating_curve.coef_a}(h - {rating_curve.coef_h0})^{rating_curve.coef_b}"

    station_data = {
        'id': station.pk,
        'name': station.name,
        'rating_curve': rating_curve_eq,
    }

    return render(request, 'measurement/timeseries_detail.html', {
        'station': station_data,
        'data': data[:100],  # 최근 100개만 템플릿에 전달
        'total_count': total_count,
    })


@require_http_methods(["POST"])
def generate_discharge_series(request):
    """Rating Curve 적용하여 유량 시계열 생성 (AJAX)"""
    from .models import Station, WaterLevelTimeSeries, RatingCurve, DischargeTimeSeries

    try:
        data = json.loads(request.body)
        station_id = data.get('station_id')
        rating_curve_id = data.get('rating_curve_id')

        if not station_id or not rating_curve_id:
            return JsonResponse({'error': 'station_id와 rating_curve_id가 필요합니다.'}, status=400)

        # 관측소 및 Rating Curve 조회
        station = get_object_or_404(Station, pk=station_id)
        rating_curve = get_object_or_404(RatingCurve, pk=rating_curve_id)

        # 수위 시계열 조회
        water_levels = WaterLevelTimeSeries.objects.filter(station=station)

        if not water_levels.exists():
            return JsonResponse({'error': '수위 시계열 데이터가 없습니다.'}, status=400)

        # 기존 유량 시계열 삭제 (같은 station + rating_curve 조합)
        DischargeTimeSeries.objects.filter(
            station=station,
            rating_curve=rating_curve
        ).delete()

        # 유량 계산 및 저장
        created_count = 0
        extrapolated_count = 0

        discharge_records = []
        for wl in water_levels:
            if wl.stage is None:
                continue

            # Q = a * (h - h0) ^ b
            h_diff = wl.stage - rating_curve.coef_h0

            if h_diff <= 0:
                # 수위가 h0 이하면 유량 0
                discharge = 0
                quality_flag = 'suspect'
            else:
                discharge = rating_curve.coef_a * (h_diff ** rating_curve.coef_b)

                # 외삽 여부 확인
                if wl.stage < rating_curve.h_min or wl.stage > rating_curve.h_max:
                    quality_flag = 'extrapolated'
                    extrapolated_count += 1
                else:
                    quality_flag = 'good'

            discharge_records.append(DischargeTimeSeries(
                station=station,
                timestamp=wl.timestamp,
                stage=wl.stage,
                discharge=round(discharge, 4),
                rating_curve=rating_curve,
                quality_flag=quality_flag,
            ))
            created_count += 1

        # 일괄 생성
        DischargeTimeSeries.objects.bulk_create(discharge_records, batch_size=1000)

        return JsonResponse({
            'success': True,
            'message': f'유량 시계열 생성 완료 ({created_count}개)',
            'count': created_count,
            'extrapolated': extrapolated_count,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def baseflow_list(request):
    """기저유출 분석 목록"""
    from .models import BaseflowAnalysis

    # DB에서 분석 목록 조회
    db_analyses = BaseflowAnalysis.objects.select_related('station').order_by('-created_at')

    analyses = []
    for a in db_analyses:
        analyses.append({
            'id': a.pk,
            'station_name': a.station.name if a.station else 'Unknown',
            'period': f'{a.start_date} ~ {a.end_date}',
            'method': a.get_method_display(),
            'bfi': a.bfi,
            'total_runoff': a.total_runoff,
            'baseflow': a.baseflow,
            'created_at': a.created_at.strftime('%Y-%m-%d') if a.created_at else '',
        })

    return render(request, 'measurement/baseflow_list.html', {
        'analyses': analyses,
    })


def baseflow_new(request):
    """새 기저유출 분석"""
    from hydro.services import STATION_DATABASE

    # HRFCO 관측소 목록 전달
    return render(request, 'measurement/baseflow_new.html', {
        'hrfco_stations': STATION_DATABASE,
    })


@require_GET
def api_hrfco_discharge(request):
    """HRFCO API에서 유량 데이터 가져오기"""
    from hydro.services import get_waterlevel_history
    from datetime import datetime, timedelta

    station_code = request.GET.get('station_code')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not station_code:
        return JsonResponse({'error': '관측소 코드가 필요합니다.'}, status=400)

    try:
        # 기본 기간: 최근 1년
        if not end_date:
            end_dt = datetime.now()
        else:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d')

        if not start_date:
            start_dt = end_dt - timedelta(days=365)
        else:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')

        # HRFCO API 호출
        data = get_waterlevel_history(station_code, start_dt, end_dt)

        # 일별 평균 유량으로 집계 (기저유출 분석용)
        daily_data = {}
        for item in data:
            if item.get('fw') is not None:  # 유량 데이터가 있는 경우만
                date_key = item['datetime'].strftime('%Y-%m-%d') if item.get('datetime') else None
                if date_key:
                    if date_key not in daily_data:
                        daily_data[date_key] = []
                    daily_data[date_key].append(item['fw'])

        # 일평균 계산
        discharge_series = []
        dates = []
        for date_key in sorted(daily_data.keys()):
            values = daily_data[date_key]
            avg_discharge = sum(values) / len(values)
            dates.append(date_key)
            discharge_series.append(round(avg_discharge, 4))

        return JsonResponse({
            'success': True,
            'station_code': station_code,
            'dates': dates,
            'discharge': discharge_series,
            'count': len(discharge_series),
            'start_date': dates[0] if dates else None,
            'end_date': dates[-1] if dates else None,
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def baseflow_detail(request, pk):
    """기저유출 분석 상세"""
    from .models import BaseflowAnalysis

    try:
        # DB에서 분석 결과 조회
        analysis_obj = BaseflowAnalysis.objects.select_related('station').get(pk=pk)
        daily_results = analysis_obj.daily_results.all().order_by('date')

        # 일별 데이터 변환
        daily_data = []
        for d in daily_results:
            direct = d.total_discharge - d.baseflow if d.total_discharge and d.baseflow else 0
            daily_data.append({
                'date': d.date.strftime('%Y-%m-%d'),
                'total': round(d.total_discharge, 3) if d.total_discharge else 0,
                'baseflow': round(d.baseflow, 3) if d.baseflow else 0,
                'direct': round(max(0, direct), 3),
            })

        # 분석 결과 객체 (템플릿에서 .pk 접근 가능)
        class AnalysisWrapper:
            def __init__(self, obj):
                self.pk = obj.pk
                self.id = obj.pk
                self.station_name = obj.station.name if obj.station else 'Unknown'
                self.start_date = obj.start_date
                self.end_date = obj.end_date
                self.method = obj.method
                self.method_display = obj.get_method_display()
                self.alpha = obj.alpha
                self.bfi_max = obj.bfi_max
                self.total_runoff = obj.total_runoff
                self.baseflow = obj.baseflow
                self.direct_runoff = obj.direct_runoff
                self.bfi = obj.bfi

        analysis = AnalysisWrapper(analysis_obj)

        return render(request, 'measurement/baseflow_detail.html', {
            'analysis': analysis,
            'daily_data': daily_data,
        })

    except BaseflowAnalysis.DoesNotExist:
        from django.http import Http404
        raise Http404("분석 결과를 찾을 수 없습니다.")


@require_http_methods(["POST"])
def run_baseflow_analysis(request):
    """기저유출 분석 실행 (AJAX)"""
    import numpy as np

    try:
        data = json.loads(request.body)
        method = data.get('method', 'lyne_hollick')
        alpha = float(data.get('alpha', 0.925))
        discharge = np.array(data.get('discharge', []))

        if len(discharge) < 30:
            return JsonResponse({'error': '최소 30일 이상의 데이터가 필요합니다.'}, status=400)

        # Lyne-Hollick 디지털 필터
        if method == 'lyne_hollick':
            baseflow = np.zeros_like(discharge)
            baseflow[0] = discharge[0] * 0.5

            for i in range(1, len(discharge)):
                # b(i) = α * b(i-1) + (1-α)/2 * (Q(i) + Q(i-1))
                baseflow[i] = alpha * baseflow[i-1] + (1 - alpha) / 2 * (discharge[i] + discharge[i-1])
                baseflow[i] = min(baseflow[i], discharge[i])

        # Eckhardt 필터
        elif method == 'eckhardt':
            bfi_max = float(data.get('bfi_max', 0.80))
            baseflow = np.zeros_like(discharge)
            baseflow[0] = discharge[0] * bfi_max

            for i in range(1, len(discharge)):
                baseflow[i] = ((1 - bfi_max) * alpha * baseflow[i-1] +
                               (1 - alpha) * bfi_max * discharge[i]) / (1 - alpha * bfi_max)
                baseflow[i] = min(baseflow[i], discharge[i])

        else:
            return JsonResponse({'error': '지원하지 않는 분석 방법입니다.'}, status=400)

        # 결과 계산
        direct_runoff = discharge - baseflow
        total_sum = float(np.sum(discharge))
        baseflow_sum = float(np.sum(baseflow))
        bfi = baseflow_sum / total_sum if total_sum > 0 else 0

        return JsonResponse({
            'success': True,
            'baseflow': baseflow.tolist(),
            'direct_runoff': direct_runoff.tolist(),
            'statistics': {
                'total_runoff': round(total_sum, 2),
                'baseflow': round(baseflow_sum, 2),
                'direct_runoff': round(float(np.sum(direct_runoff)), 2),
                'bfi': round(bfi, 4),
            }
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["POST"])
def save_baseflow_analysis(request):
    """기저유출 분석 결과 저장"""
    from .models import Station, BaseflowAnalysis, BaseflowDaily
    from datetime import datetime

    # 로그인 체크
    if not request.user.is_authenticated:
        return JsonResponse({'error': '로그인이 필요합니다.'}, status=401)

    try:
        data = json.loads(request.body)

        # 필수 데이터
        station_id = data.get('station_id')
        station_name = data.get('station_name', '')
        method = data.get('method', 'lyne_hollick')
        alpha = float(data.get('alpha', 0.925))
        bfi_max = float(data.get('bfi_max', 0.80)) if data.get('bfi_max') else None
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        # 분석 결과
        statistics = data.get('statistics', {})
        daily_data = data.get('daily_data', [])  # [{date, total, baseflow, direct}, ...]

        # 관측소 조회 또는 생성
        station = None
        if station_id:
            try:
                station = Station.objects.get(id=station_id)
            except Station.DoesNotExist:
                pass

        if not station and station_name:
            station, _ = Station.objects.get_or_create(
                name=station_name,
                defaults={'description': '자동 생성'}
            )

        if not station:
            return JsonResponse({'error': '관측소 정보가 필요합니다.'}, status=400)

        # BaseflowAnalysis 생성
        analysis = BaseflowAnalysis.objects.create(
            user=request.user,  # 사용자 연결
            station=station,
            start_date=datetime.strptime(start_date, '%Y-%m-%d').date(),
            end_date=datetime.strptime(end_date, '%Y-%m-%d').date(),
            method=method,
            alpha=alpha,
            bfi_max=bfi_max,
            total_runoff=statistics.get('total_runoff'),
            baseflow=statistics.get('baseflow'),
            direct_runoff=statistics.get('direct_runoff'),
            bfi=statistics.get('bfi'),
        )

        # 활동 로그 기록
        from core.tracking import log_activity
        log_activity(
            user=request.user,
            action_type='save',
            detail=f'기저유출 분석 저장: {station.name} ({start_date}~{end_date})',
            related_object=analysis,
            request=request,
            extra_data={'method': method, 'bfi': statistics.get('bfi')}
        )

        # 일별 데이터 저장
        daily_objects = []
        for d in daily_data:
            daily_objects.append(BaseflowDaily(
                analysis=analysis,
                date=datetime.strptime(d['date'], '%Y-%m-%d').date(),
                total_discharge=d['total'],
                baseflow=d['baseflow'],
                direct_runoff=d['direct'],
            ))

        if daily_objects:
            BaseflowDaily.objects.bulk_create(daily_objects)

        return JsonResponse({
            'success': True,
            'analysis_id': analysis.id,
            'message': f'분석 결과가 저장되었습니다. (ID: {analysis.id})'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def export_baseflow_pdf(request, pk):
    """기저유출 분석 PDF 리포트 다운로드"""
    from django.http import HttpResponse
    from .models import BaseflowAnalysis
    from .pdf_service import generate_baseflow_report
    import urllib.parse

    try:
        analysis = BaseflowAnalysis.objects.select_related('station').get(pk=pk)
        daily_data = list(analysis.daily_results.all().order_by('date'))

        # PDF 생성
        pdf_buffer = generate_baseflow_report(analysis, daily_data)

        # 안전한 파일명 생성
        station_name = analysis.station.name if analysis.station else 'unknown'
        safe_filename = urllib.parse.quote(f"baseflow_{station_name}_{analysis.start_date}.pdf")

        # 응답 생성
        response = HttpResponse(pdf_buffer.read(), content_type='application/pdf')
        response['Content-Disposition'] = f"attachment; filename*=UTF-8''{safe_filename}"

        # 활동 로그 기록
        if request.user.is_authenticated:
            from core.tracking import log_activity
            log_activity(
                user=request.user,
                action_type='export_pdf',
                detail=f'기저유출 PDF 다운로드: {station_name}',
                related_object=analysis,
                request=request
            )

        return response

    except BaseflowAnalysis.DoesNotExist:
        return HttpResponse('Analysis not found', status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HttpResponse(f'Error generating PDF: {str(e)}', status=500)


# ============================================
# 측정 데이터 자동저장 및 히스토리
# ============================================

@require_http_methods(["POST"])
def api_measurement_autosave(request):
    """측정 데이터 자동저장 API"""
    from .models import MeasurementSession

    try:
        data = json.loads(request.body)

        session_id = data.get('session_id')  # 기존 세션 업데이트 시
        station_name = data.get('station_name', '')
        measurement_date = data.get('measurement_date')
        session_number = int(data.get('session_number', 1))
        rows_data = data.get('rows', [])
        calibration_data = data.get('calibration', {})
        setup_data = data.get('setup_data', {})  # 하천명, 기상, 측정자 등
        estimated_discharge = data.get('estimated_discharge')
        total_width = data.get('total_width')
        max_depth = data.get('max_depth')
        total_area = data.get('total_area')

        # 날짜 파싱
        parsed_date = None
        if measurement_date:
            try:
                parsed_date = datetime.strptime(measurement_date, '%Y-%m-%d').date()
            except:
                pass

        # 사용자 또는 세션키로 식별
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ''
        if not session_key and not user:
            request.session.create()
            session_key = request.session.session_key

        # 기존 세션 업데이트 또는 새로 생성
        session = None
        if session_id:
            try:
                if user:
                    session = MeasurementSession.objects.get(pk=session_id, user=user)
                else:
                    session = MeasurementSession.objects.get(pk=session_id, session_key=session_key)
            except MeasurementSession.DoesNotExist:
                session = None

        if session:
            # 기존 세션 업데이트
            session.station_name = station_name
            session.measurement_date = parsed_date
            session.session_number = session_number
            session.rows_data = rows_data
            session.calibration_data = calibration_data
            session.setup_data = setup_data
            session.estimated_discharge = estimated_discharge
            session.total_width = total_width
            session.max_depth = max_depth
            session.total_area = total_area
            session.save()
        else:
            # 새 세션 생성
            session = MeasurementSession.objects.create(
                user=user,
                session_key=session_key,
                station_name=station_name,
                measurement_date=parsed_date,
                session_number=session_number,
                rows_data=rows_data,
                calibration_data=calibration_data,
                setup_data=setup_data,
                estimated_discharge=estimated_discharge,
                total_width=total_width,
                max_depth=max_depth,
                total_area=total_area,
            )

        return JsonResponse({
            'success': True,
            'session_id': session.pk,
            'updated_at': session.updated_at.isoformat(),
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_POST
def api_result_save(request):
    """결과 페이지에서 최종 저장 API

    중복 저장 방지:
    - session_id가 있으면 해당 세션만 업데이트
    - session_id가 없으면 동일 데이터 중복 체크 후 저장
    """
    from .models import MeasurementSession

    try:
        data = json.loads(request.body)

        session_id = data.get('session_id')
        station_name = data.get('station_name', '')
        measurement_date = data.get('measurement_date')
        discharge = data.get('discharge')
        area = data.get('area')
        avg_velocity = data.get('avg_velocity')
        uncertainty = data.get('uncertainty')

        # 날짜 파싱
        parsed_date = None
        if measurement_date:
            try:
                parsed_date = datetime.strptime(measurement_date, '%Y-%m-%d').date()
            except:
                pass

        # session_id가 있으면 해당 세션만 업데이트 (중복 생성 방지)
        if session_id:
            try:
                session = MeasurementSession.objects.get(pk=session_id)
                # 기존 세션 업데이트 - 결과값 저장
                session.station_name = station_name or session.station_name
                if parsed_date:
                    session.measurement_date = parsed_date
                session.estimated_discharge = discharge
                session.total_area = area
                if not session.setup_data:
                    session.setup_data = {}
                session.setup_data['final_discharge'] = discharge
                session.setup_data['final_uncertainty'] = uncertainty
                session.setup_data['final_avg_velocity'] = avg_velocity
                session.save()

                return JsonResponse({
                    'success': True,
                    'session_id': session.pk,
                    'message': '결과가 저장되었습니다.',
                })
            except MeasurementSession.DoesNotExist:
                pass  # session_id가 유효하지 않으면 아래에서 중복 체크 후 처리

        # 사용자 또는 세션키로 식별
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key or ''
        if not session_key and not user:
            request.session.create()
            session_key = request.session.session_key

        # 중복 체크: 동일 관측소 + 날짜 + 유량값이 있으면 기존 세션 반환
        if station_name and parsed_date and discharge:
            existing = MeasurementSession.objects.filter(
                station_name=station_name,
                measurement_date=parsed_date,
                estimated_discharge=discharge
            ).first()

            if existing:
                return JsonResponse({
                    'success': True,
                    'session_id': existing.pk,
                    'message': '이미 저장된 데이터입니다.',
                    'duplicate': True,
                })

        # 새 세션 생성
        session = MeasurementSession.objects.create(
            user=user,
            session_key=session_key,
            station_name=station_name,
            measurement_date=parsed_date,
            estimated_discharge=discharge,
            total_area=area,
            setup_data={
                'final_discharge': discharge,
                'final_uncertainty': uncertainty,
                'final_avg_velocity': avg_velocity,
            }
        )

        return JsonResponse({
            'success': True,
            'session_id': session.pk,
            'message': '결과가 저장되었습니다.',
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_GET
def api_measurement_history(request):
    """측정 데이터 히스토리 목록 API"""
    from .models import MeasurementSession

    limit = int(request.GET.get('limit', 20))

    # 사용자 또는 세션키로 필터
    user = request.user if request.user.is_authenticated else None
    session_key = request.session.session_key or ''

    if user:
        sessions = MeasurementSession.objects.filter(user=user)
    elif session_key:
        sessions = MeasurementSession.objects.filter(session_key=session_key)
    else:
        # 비로그인이고 세션도 없으면 전체 최근 데이터 (개발용)
        sessions = MeasurementSession.objects.all()

    sessions = sessions.order_by('-updated_at')[:limit]

    history = []
    for s in sessions:
        history.append({
            'id': s.pk,
            'station_name': s.station_name or '미지정',
            'measurement_date': s.measurement_date.strftime('%Y-%m-%d') if s.measurement_date else None,
            'session_number': s.session_number,
            'estimated_discharge': s.estimated_discharge,
            'row_count': len(s.rows_data) if s.rows_data else 0,
            'updated_at': s.updated_at.strftime('%Y-%m-%d %H:%M'),
            'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
        })

    return JsonResponse({
        'history': history,
        'count': len(history),
    })


@require_GET
def api_measurement_load(request, session_id):
    """저장된 측정 데이터 불러오기 API"""
    from .models import MeasurementSession

    try:
        # 개발 모드에서는 모든 세션 접근 허용
        session = MeasurementSession.objects.get(pk=session_id)

        return JsonResponse({
            'success': True,
            'session_id': session.pk,
            'station_name': session.station_name,
            'measurement_date': session.measurement_date.strftime('%Y-%m-%d') if session.measurement_date else None,
            'session_number': session.session_number,
            'rows': session.rows_data,
            'calibration': session.calibration_data,
            'setup_data': session.setup_data,
            'estimated_discharge': session.estimated_discharge,
            'total_width': session.total_width,
            'max_depth': session.max_depth,
            'total_area': session.total_area,
            'updated_at': session.updated_at.isoformat(),
        })

    except MeasurementSession.DoesNotExist:
        return JsonResponse({'error': '세션을 찾을 수 없습니다.'}, status=404)


@require_http_methods(["DELETE"])
def api_measurement_delete(request, session_id):
    """측정 데이터 세션 삭제 API"""
    from .models import MeasurementSession

    try:
        # 개발 모드에서는 모든 세션 삭제 허용
        session = MeasurementSession.objects.get(pk=session_id)
        session.delete()

        return JsonResponse({
            'success': True,
            'message': '삭제되었습니다.',
        })

    except MeasurementSession.DoesNotExist:
        return JsonResponse({'error': '세션을 찾을 수 없습니다.'}, status=404)


def api_create_mock_data(request):
    """개발용: 모의 데이터 생성 API"""
    from django.core.management import call_command
    from io import StringIO

    try:
        out = StringIO()
        clean = request.GET.get('clean', '').lower() == 'true'
        call_command('create_mock_data', clean=clean, stdout=out)
        output = out.getvalue()

        return JsonResponse({
            'success': True,
            'message': '모의 데이터 생성 완료',
            'output': output,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
