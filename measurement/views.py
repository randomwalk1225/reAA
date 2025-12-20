from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from io import BytesIO
from datetime import datetime, timedelta
import json
import math


def measurement_list(request):
    """측정 목록"""
    # 샘플 데이터 (추후 DB 연동)
    measurements = [
        {
            'id': 1,
            'station_name': '경주 대종천 하류보',
            'river_name': '대종천',
            'measurement_date': '2025-05-01',
            'discharge': 1.234,
            'uncertainty': 4.2,
            'status': 'completed',
        },
        {
            'id': 2,
            'station_name': '신태인 수위관측소',
            'river_name': '동진강',
            'measurement_date': '2025-04-28',
            'discharge': 15.67,
            'uncertainty': 3.8,
            'status': 'completed',
        },
        {
            'id': 3,
            'station_name': '평림천 관측소',
            'river_name': '평림천',
            'measurement_date': '2025-04-25',
            'discharge': 0.856,
            'uncertainty': 5.1,
            'status': 'draft',
        },
    ]
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
    """측정 상세 (결과 보기)"""
    # 샘플 데이터 (추후 DB 연동)
    sample_data = {
        1: {
            'id': 1,
            'station_name': '경주 대종천 하류보',
            'date': '2025-05-01',
            'discharge': 1.234,
            'uncertainty': 4.2,
            'uncertainty_abs': 0.052,
            'area': 5.67,
            'width': 10.5,
            'avg_depth': 0.54,
            'avg_velocity': 0.218,
            'max_velocity': 0.312,
            'min_velocity': 0.156,
        },
        2: {
            'id': 2,
            'station_name': '신태인 수위관측소',
            'date': '2025-04-28',
            'discharge': 15.67,
            'uncertainty': 3.8,
            'uncertainty_abs': 0.596,
            'area': 42.5,
            'width': 25.0,
            'avg_depth': 1.70,
            'avg_velocity': 0.369,
            'max_velocity': 0.512,
            'min_velocity': 0.234,
        },
        3: {
            'id': 3,
            'station_name': '평림천 관측소',
            'date': '2025-04-25',
            'discharge': 0.856,
            'uncertainty': 5.1,
            'uncertainty_abs': 0.044,
            'area': 3.21,
            'width': 8.0,
            'avg_depth': 0.40,
            'avg_velocity': 0.267,
            'max_velocity': 0.345,
            'min_velocity': 0.189,
        },
    }
    measurement = sample_data.get(pk, sample_data[1])
    return render(request, 'measurement/result.html', {
        'measurement': measurement,
        'discharge': measurement['discharge'],
        'uncertainty': measurement['uncertainty'],
        'uncertainty_abs': measurement['uncertainty_abs'],
        'area': measurement['area'],
        'width': measurement['width'],
        'avg_depth': measurement['avg_depth'],
        'avg_velocity': measurement['avg_velocity'],
        'max_velocity': measurement['max_velocity'],
        'min_velocity': measurement['min_velocity'],
    })


def measurement_edit(request, pk):
    """측정 수정"""
    return redirect('measurement:data_input')


def measurement_delete(request, pk):
    """측정 삭제"""
    if request.method == 'DELETE':
        # 삭제 처리 (추후 구현)
        return HttpResponse(status=200)
    return HttpResponse(status=405)


def data_input(request):
    """데이터 입력 그리드"""
    return render(request, 'measurement/data_input.html')


def result(request):
    """계산 결과"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            rows = data.get('rows', [])
            calibration = data.get('calibration', {'a': 0.0012, 'b': 0.2534})

            # 계산 수행
            result_data = calculate_discharge(rows, calibration)

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
    """Excel 다운로드"""
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, Border, Side, PatternFill

    # 샘플 데이터 (추후 DB에서 조회)
    data = {
        'station_name': '경주 대종천 하류보',
        'date': '2025-05-01',
        'discharge': 1.234,
        'uncertainty': 4.2,
        'area': 5.67,
        'avg_velocity': 0.218,
        'rows': [
            {'no': 1, 'distance': 0.0, 'depth': 0.00, 'velocity': 0.000, 'area': 0.000, 'discharge': 0.000, 'ratio': 0.0},
            {'no': 2, 'distance': 1.5, 'depth': 0.45, 'velocity': 0.156, 'area': 0.338, 'discharge': 0.053, 'ratio': 4.3},
            {'no': 3, 'distance': 3.0, 'depth': 0.72, 'velocity': 0.198, 'area': 0.540, 'discharge': 0.107, 'ratio': 8.7},
            {'no': 4, 'distance': 4.5, 'depth': 1.20, 'velocity': 0.285, 'area': 0.900, 'discharge': 0.257, 'ratio': 20.8},
            {'no': 5, 'distance': 6.0, 'depth': 1.35, 'velocity': 0.312, 'area': 1.013, 'discharge': 0.316, 'ratio': 25.6},
            {'no': 6, 'distance': 7.5, 'depth': 0.85, 'velocity': 0.245, 'area': 0.638, 'discharge': 0.156, 'ratio': 12.7},
            {'no': 7, 'distance': 9.0, 'depth': 0.50, 'velocity': 0.168, 'area': 0.375, 'discharge': 0.063, 'ratio': 5.1},
            {'no': 8, 'distance': 10.5, 'depth': 0.00, 'velocity': 0.000, 'area': 0.000, 'discharge': 0.000, 'ratio': 0.0},
        ]
    }

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
    """PDF 출력"""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    import os

    # 샘플 데이터 (추후 DB에서 조회)
    data = {
        'station_name': '경주 대종천 하류보',
        'date': '2025-05-01',
        'discharge': 1.234,
        'uncertainty': 4.2,
        'area': 5.67,
        'avg_velocity': 0.218,
        'rows': [
            [1, 0.0, 0.00, 0.000, 0.000, 0.000, '0.0%'],
            [2, 1.5, 0.45, 0.156, 0.338, 0.053, '4.3%'],
            [3, 3.0, 0.72, 0.198, 0.540, 0.107, '8.7%'],
            [4, 4.5, 1.20, 0.285, 0.900, 0.257, '20.8%'],
            [5, 6.0, 1.35, 0.312, 1.013, 0.316, '25.6%'],
            [6, 7.5, 0.85, 0.245, 0.638, 0.156, '12.7%'],
            [7, 9.0, 0.50, 0.168, 0.375, 0.063, '5.1%'],
            [8, 10.5, 0.00, 0.000, 0.000, 0.000, '0.0%'],
        ]
    }

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
    # 샘플 데이터 (추후 DB 연동)
    sample_curves = [
        {
            'id': 1,
            'station_name': '신태인',
            'year': 2003,
            'curve_type': '방류',
            'h_range': '0.26 ≤ h ≤ 4.45',
            'equation': 'Q = 24.5898(h - 0.034264)^1.6663',
            'r_squared': 0.977,
        },
        {
            'id': 2,
            'station_name': '신태인',
            'year': 2003,
            'curve_type': '저류',
            'h_range': '0.32 ≤ h ≤ 2.03',
            'equation': 'Q = 2.31208(h + 0.262311)^4.14495',
            'r_squared': 0.934,
        },
        {
            'id': 3,
            'station_name': '경주 대종천',
            'year': 2025,
            'curve_type': '방류',
            'h_range': '0.24 < h ≤ 0.5',
            'equation': 'Q = 3.22(h - 0.001)^1.941',
            'r_squared': 0.985,
        },
    ]
    return render(request, 'measurement/rating_curve_list.html', {
        'curves': sample_curves,
    })


def rating_curve_detail(request, pk):
    """수위-유량곡선 상세"""
    # 샘플 데이터
    curve_data = {
        'id': pk,
        'station_name': '경주 대종천',
        'year': 2025,
        'curve_type': 'open',
        'curve_type_display': '방류',
        'h_min': 0.24,
        'h_max': 0.5,
        'coef_a': 3.22,
        'coef_b': 1.941,
        'coef_h0': 0.001,
        'r_squared': 0.985,
        'equation': 'Q = 3.22×(h - 0.001)^1.941',
        'data_points': [
            {'date': '2025-03-15', 'stage': 0.24, 'discharge': 0.12},
            {'date': '2025-04-20', 'stage': 0.32, 'discharge': 0.28},
            {'date': '2025-05-10', 'stage': 0.48, 'discharge': 0.95},
            {'date': '2025-06-05', 'stage': 0.65, 'discharge': 1.65},
        ],
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


def timeseries_list(request):
    """시계열 데이터 관리"""
    # 샘플 관측소 목록
    stations = [
        {
            'id': 1,
            'name': '경주 대종천 하류보',
            'has_rating_curve': True,
            'data_count': 8760,  # 1년치 시간 데이터
            'last_update': '2025-05-01 12:00',
            'period': '2024-05-01 ~ 2025-05-01',
        },
        {
            'id': 2,
            'name': '신태인 수위관측소',
            'has_rating_curve': True,
            'data_count': 17520,  # 2년치
            'last_update': '2025-04-30 18:00',
            'period': '2023-05-01 ~ 2025-04-30',
        },
    ]
    return render(request, 'measurement/timeseries_list.html', {
        'stations': stations,
    })


def timeseries_upload(request):
    """수위 데이터 업로드"""
    if request.method == 'POST':
        # CSV 파싱 및 저장 로직 (추후 구현)
        return JsonResponse({'success': True, 'message': '업로드 완료'})
    return render(request, 'measurement/timeseries_upload.html')


def timeseries_detail(request, station_id):
    """관측소별 시계열 상세"""
    import random
    from datetime import timedelta

    # 샘플 데이터 생성 (최근 30일)
    base_date = datetime(2025, 5, 1)
    sample_data = []
    for i in range(30 * 24):  # 30일 x 24시간
        dt = base_date - timedelta(hours=i)
        h = 0.3 + 0.2 * (1 + 0.5 * (i % 24) / 24) + random.uniform(-0.05, 0.05)
        q = 3.22 * ((h - 0.001) ** 1.941)
        sample_data.append({
            'timestamp': dt.strftime('%Y-%m-%d %H:%M'),
            'stage': round(h, 3),
            'discharge': round(q, 4),
        })

    station = {
        'id': station_id,
        'name': '경주 대종천 하류보' if station_id == 1 else '신태인 수위관측소',
        'rating_curve': 'Q = 3.22(h - 0.001)^1.941',
    }

    return render(request, 'measurement/timeseries_detail.html', {
        'station': station,
        'data': sample_data[:100],  # 최근 100개만
        'total_count': len(sample_data),
    })


@require_http_methods(["POST"])
def generate_discharge_series(request):
    """Rating Curve 적용하여 유량 시계열 생성 (AJAX)"""
    try:
        data = json.loads(request.body)
        station_id = data.get('station_id')
        rating_curve_id = data.get('rating_curve_id')

        # 실제로는 DB에서 수위 데이터를 가져와 Rating Curve 적용
        # 여기서는 샘플 응답
        return JsonResponse({
            'success': True,
            'message': '유량 시계열 생성 완료',
            'count': 8760,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def baseflow_list(request):
    """기저유출 분석 목록"""
    analyses = [
        {
            'id': 1,
            'station_name': '경주 대종천 하류보',
            'period': '2024-05-01 ~ 2025-04-30',
            'method': 'Lyne-Hollick 필터',
            'bfi': 0.42,
            'total_runoff': 856.3,
            'baseflow': 359.6,
            'created_at': '2025-05-01',
        },
        {
            'id': 2,
            'station_name': '신태인 수위관측소',
            'period': '2024-01-01 ~ 2024-12-31',
            'method': 'Eckhardt 필터',
            'bfi': 0.38,
            'total_runoff': 1245.8,
            'baseflow': 473.4,
            'created_at': '2025-01-15',
        },
    ]
    return render(request, 'measurement/baseflow_list.html', {
        'analyses': analyses,
    })


def baseflow_new(request):
    """새 기저유출 분석"""
    return render(request, 'measurement/baseflow_new.html')


def baseflow_detail(request, pk):
    """기저유출 분석 상세"""
    import random

    # 샘플 일별 데이터 생성 (1년)
    daily_data = []
    base_date = datetime(2024, 5, 1)
    for i in range(365):
        dt = base_date + timedelta(days=i)
        # 계절 변동 + 강우 이벤트 시뮬레이션
        seasonal = 0.5 + 0.3 * abs((i % 365) - 182) / 182
        event = random.uniform(0, 2) if random.random() < 0.1 else 0
        total_q = seasonal + event + random.uniform(-0.1, 0.1)
        baseflow_q = seasonal * 0.4 + random.uniform(-0.02, 0.02)

        daily_data.append({
            'date': dt.strftime('%Y-%m-%d'),
            'total': round(max(0.1, total_q), 3),
            'baseflow': round(max(0.05, baseflow_q), 3),
            'direct': round(max(0, total_q - baseflow_q), 3),
        })

    analysis = {
        'id': pk,
        'station_name': '경주 대종천 하류보',
        'start_date': '2024-05-01',
        'end_date': '2025-04-30',
        'method': 'lyne_hollick',
        'method_display': 'Lyne-Hollick 필터',
        'alpha': 0.925,
        'total_runoff': 856.3,
        'baseflow': 359.6,
        'direct_runoff': 496.7,
        'bfi': 0.42,
    }

    return render(request, 'measurement/baseflow_detail.html', {
        'analysis': analysis,
        'daily_data': daily_data,
    })


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
