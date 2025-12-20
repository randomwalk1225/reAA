"""
기저유출 분석 PDF 리포트 생성 서비스
"""
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Line
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.widgets.markers import makeMarker


def get_bfi_interpretation(bfi):
    """BFI 값에 따른 해석 문구 반환"""
    if bfi is None:
        return "BFI 값을 계산할 수 없습니다."

    if bfi < 0.4:
        return (
            f"BFI = {bfi:.3f}로 직접유출이 우세한 유역입니다. "
            "강우 시 유출 반응이 빠르며, 지표수 의존도가 높습니다. "
            "가뭄 시 하천 유량이 급격히 감소할 수 있습니다."
        )
    elif bfi < 0.6:
        return (
            f"BFI = {bfi:.3f}로 지표수와 지하수의 기여가 균형을 이루는 유역입니다. "
            "적절한 지하수 함양이 이루어지고 있으며, "
            "계절적 유량 변동이 중간 수준입니다."
        )
    elif bfi < 0.8:
        return (
            f"BFI = {bfi:.3f}로 지하수 기여도가 높은 유역입니다. "
            "기저유출이 안정적으로 유지되며, 가뭄 시에도 "
            "일정 수준의 하천 유량이 유지됩니다."
        )
    else:
        return (
            f"BFI = {bfi:.3f}로 지하수가 우세한 유역입니다. "
            "대수층의 저류 능력이 우수하여 연중 안정적인 기저유출이 유지됩니다. "
            "수자원 관리 측면에서 매우 유리한 조건입니다."
        )


def get_method_description(method):
    """분석 방법 설명"""
    descriptions = {
        'lyne_hollick': (
            "Lyne-Hollick 디지털 필터는 단일 매개변수(α)를 사용하는 "
            "재귀 필터 방식으로, 호주 수문학에서 개발되어 널리 사용됩니다. "
            "필터 계수 α가 클수록 더 많은 고주파 성분이 제거됩니다."
        ),
        'eckhardt': (
            "Eckhardt 필터는 BFImax 제약 조건을 포함하는 개선된 디지털 필터입니다. "
            "유역의 수문지질 특성을 반영한 최대 기저유출지수(BFImax)를 "
            "설정하여 보다 물리적으로 타당한 결과를 제공합니다."
        ),
    }
    return descriptions.get(method, "디지털 필터 기반 기저유출 분리 방법")


def generate_baseflow_report(analysis, daily_data, output_buffer=None):
    """
    기저유출 분석 PDF 리포트 생성

    Args:
        analysis: BaseflowAnalysis 모델 인스턴스
        daily_data: 일별 데이터 QuerySet 또는 리스트
        output_buffer: 출력 버퍼 (None이면 새로 생성)

    Returns:
        BytesIO 버퍼 또는 None
    """
    if output_buffer is None:
        output_buffer = io.BytesIO()

    # 문서 설정
    doc = SimpleDocTemplate(
        output_buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm,
    )

    # 스타일 설정
    styles = getSampleStyleSheet()

    # 한글 폰트 스타일 (기본 폰트 사용, 한글은 깨질 수 있음)
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=12,
        alignment=1,  # 가운데 정렬
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceBefore=12,
        spaceAfter=6,
    )

    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
    )

    # 콘텐츠 빌드
    story = []

    # === 제목 ===
    story.append(Paragraph("Baseflow Analysis Report", title_style))
    story.append(Paragraph("기저유출 분석 리포트", styles['Heading2']))
    story.append(Spacer(1, 10*mm))

    # === 기본 정보 테이블 ===
    story.append(Paragraph("1. Basic Information (기본 정보)", heading_style))

    info_data = [
        ['Station (관측소)', analysis.station.name if analysis.station else '-'],
        ['Period (분석기간)', f"{analysis.start_date} ~ {analysis.end_date}"],
        ['Method (분석방법)', analysis.get_method_display()],
        ['Filter Coefficient (α)', f"{analysis.alpha:.3f}"],
        ['Generated (생성일시)', datetime.now().strftime('%Y-%m-%d %H:%M')],
    ]

    if analysis.method == 'eckhardt' and analysis.bfi_max:
        info_data.insert(4, ['BFImax', f"{analysis.bfi_max:.2f}"])

    info_table = Table(info_data, colWidths=[60*mm, 100*mm])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(0.9, 0.9, 0.9)),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 8*mm))

    # === 분석 결과 ===
    story.append(Paragraph("2. Analysis Results (분석 결과)", heading_style))

    results_data = [
        ['Metric', 'Value', 'Unit'],
        ['Total Runoff (총유출량)', f"{analysis.total_runoff:.1f}" if analysis.total_runoff else '-', 'mm'],
        ['Baseflow (기저유출량)', f"{analysis.baseflow:.1f}" if analysis.baseflow else '-', 'mm'],
        ['Direct Runoff (직접유출량)', f"{analysis.direct_runoff:.1f}" if analysis.direct_runoff else '-', 'mm'],
        ['BFI (기저유출지수)', f"{analysis.bfi:.4f}" if analysis.bfi else '-', '-'],
    ]

    results_table = Table(results_data, colWidths=[70*mm, 50*mm, 40*mm])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.6)),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('BACKGROUND', (0, 4), (-1, 4), colors.Color(0.9, 1.0, 0.9)),  # BFI 행 강조
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 8*mm))

    # === 해석 ===
    story.append(Paragraph("3. Interpretation (결과 해석)", heading_style))

    # BFI 해석
    bfi_interpretation = get_bfi_interpretation(analysis.bfi)
    story.append(Paragraph(f"<b>BFI Analysis:</b> {bfi_interpretation}", normal_style))
    story.append(Spacer(1, 4*mm))

    # 방법 설명
    method_desc = get_method_description(analysis.method)
    story.append(Paragraph(f"<b>Method Note:</b> {method_desc}", normal_style))
    story.append(Spacer(1, 8*mm))

    # === 월별 통계 (간략) ===
    if daily_data:
        story.append(Paragraph("4. Monthly Statistics (월별 통계)", heading_style))

        # 월별 집계
        monthly_stats = {}
        for d in daily_data:
            month_key = d.date.strftime('%Y-%m')
            if month_key not in monthly_stats:
                monthly_stats[month_key] = {'total': 0, 'baseflow': 0, 'count': 0}
            monthly_stats[month_key]['total'] += d.total_discharge
            monthly_stats[month_key]['baseflow'] += d.baseflow
            monthly_stats[month_key]['count'] += 1

        monthly_data = [['Month', 'Avg Q (m³/s)', 'Avg BF (m³/s)', 'BFI']]
        for month, stats in sorted(monthly_stats.items()):
            avg_total = stats['total'] / stats['count']
            avg_bf = stats['baseflow'] / stats['count']
            monthly_bfi = avg_bf / avg_total if avg_total > 0 else 0
            monthly_data.append([
                month,
                f"{avg_total:.3f}",
                f"{avg_bf:.3f}",
                f"{monthly_bfi:.3f}"
            ])

        monthly_table = Table(monthly_data, colWidths=[40*mm, 40*mm, 40*mm, 40*mm])
        monthly_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.3, 0.5, 0.3)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(monthly_table)
        story.append(Spacer(1, 8*mm))

    # === 데이터 요약 ===
    if daily_data:
        story.append(Paragraph("5. Data Summary (데이터 요약)", heading_style))

        total_discharges = [d.total_discharge for d in daily_data]
        baseflows = [d.baseflow for d in daily_data]

        import statistics
        summary_data = [
            ['Statistic', 'Total Q', 'Baseflow'],
            ['Count', str(len(total_discharges)), str(len(baseflows))],
            ['Mean', f"{statistics.mean(total_discharges):.3f}", f"{statistics.mean(baseflows):.3f}"],
            ['Std Dev', f"{statistics.stdev(total_discharges):.3f}" if len(total_discharges) > 1 else '-',
                       f"{statistics.stdev(baseflows):.3f}" if len(baseflows) > 1 else '-'],
            ['Min', f"{min(total_discharges):.3f}", f"{min(baseflows):.3f}"],
            ['Max', f"{max(total_discharges):.3f}", f"{max(baseflows):.3f}"],
        ]

        summary_table = Table(summary_data, colWidths=[50*mm, 55*mm, 55*mm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.4, 0.4, 0.6)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (0, -1), colors.Color(0.9, 0.9, 0.9)),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(summary_table)

    # === 푸터 ===
    story.append(Spacer(1, 15*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.grey))
    story.append(Spacer(1, 3*mm))

    footer_text = (
        "This report was automatically generated by HydroLink Baseflow Analysis System. "
        "For questions or feedback, please contact the system administrator."
    )
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.grey,
        alignment=1,
    )
    story.append(Paragraph(footer_text, footer_style))

    # PDF 빌드
    doc.build(story)

    output_buffer.seek(0)
    return output_buffer
