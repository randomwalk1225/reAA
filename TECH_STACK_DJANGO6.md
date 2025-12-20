# Django 6.0 기반 기술 스택

## 1. Django 6.0 신규 기능 활용

### 1.1 주요 신규 기능 (2025.12.03 릴리즈)

| 기능 | 설명 | 본 프로젝트 활용 |
|------|------|-----------------|
| **Template Partials** | 템플릿 내 재사용 가능한 조각 정의 | UI 컴포넌트 모듈화 |
| **Background Tasks** | 내장 비동기 작업 프레임워크 (`@task`) | Excel 파싱, 계산 백그라운드 처리 |
| **CSP 지원** | Content Security Policy 내장 | 보안 강화 |
| **BigAutoField 기본** | 64-bit ID 기본 적용 | 대용량 데이터 대비 |

### 1.2 Background Tasks 활용 예시
```python
# Django 6.0 내장 @task 데코레이터
from django.tasks import task

@task
def process_excel_file(session_id: int):
    """백그라운드에서 Excel 파일 처리"""
    session = MeasurementSession.objects.get(id=session_id)
    parser = ExcelParser(session.source_file)
    result = parser.parse_and_calculate()
    session.calculation_result = result
    session.save()
```

### 1.3 Template Partials 활용
```html
<!-- templates/calculator/result.html -->
{% load partials %}

{% partial measurement_row %}
    <tr class="hover:bg-gray-50">
        <td>{{ point.section_no }}</td>
        <td>{{ point.distance|floatformat:2 }}</td>
        <td>{{ point.depth|floatformat:3 }}</td>
        <td>{{ point.velocity|floatformat:3 }}</td>
    </tr>
{% endpartial %}

<!-- 재사용 -->
{% for point in points %}
    {% include_partial "measurement_row" %}
{% endfor %}
```

---

## 2. 프로젝트 아키텍처

### 2.1 전체 구조
```
reAA/
├── manage.py
├── requirements.txt
├── pyproject.toml
│
├── config/                     # Django 설정
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py            # 공통 설정
│   │   ├── development.py     # 개발 환경
│   │   └── production.py      # 운영 환경
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py                # 비동기 지원
│
├── apps/
│   ├── __init__.py
│   │
│   ├── core/                  # 핵심 모델 및 공통 기능
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── templatetags/
│   │       └── core_tags.py
│   │
│   ├── measurement/           # 측정 데이터 관리
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── forms.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── excel_parser.py
│   │
│   ├── calculator/            # 계산 엔진
│   │   ├── __init__.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── tasks.py           # Django 6.0 Background Tasks
│   │   └── services/
│   │       ├── __init__.py
│   │       ├── velocity.py
│   │       ├── discharge.py
│   │       └── uncertainty.py
│   │
│   └── reports/               # 보고서 생성
│       ├── __init__.py
│       ├── views.py
│       ├── urls.py
│       └── services/
│           ├── __init__.py
│           ├── excel_export.py
│           └── pdf_generator.py
│
├── templates/
│   ├── base.html
│   ├── partials/              # Django 6.0 Template Partials
│   │   ├── _navbar.html
│   │   ├── _sidebar.html
│   │   └── _data_table.html
│   ├── core/
│   ├── measurement/
│   ├── calculator/
│   └── reports/
│
├── static/
│   ├── css/
│   │   └── output.css         # Tailwind 빌드 결과
│   ├── js/
│   │   └── htmx.min.js
│   └── images/
│
├── media/
│   ├── uploads/
│   └── exports/
│
└── tests/
    ├── __init__.py
    ├── test_parser.py
    ├── test_calculator.py
    └── test_views.py
```

---

## 3. 기술 스택 상세

### 3.1 핵심 패키지
```
# requirements.txt

# Django 6.0
Django>=6.0,<6.1
django-htmx>=1.18

# Excel 처리
openpyxl>=3.1.5
xlrd>=2.0.1
pandas>=2.2

# 수치 계산
numpy>=2.0

# PDF 생성
reportlab>=4.2
# weasyprint>=62.0  # 대안

# 환경 설정
python-dotenv>=1.0
django-environ>=0.11

# 개발 도구
django-debug-toolbar>=4.4
django-extensions>=3.2

# 테스트
pytest>=8.0
pytest-django>=4.8

# 배포
gunicorn>=22.0
whitenoise>=6.7

# 데스크톱 앱 (선택)
pywebview>=5.0
```

### 3.2 Python 버전
- **권장**: Python 3.12 또는 3.13
- Django 6.0은 Python 3.10, 3.11 지원 종료

### 3.3 프론트엔드 스택
| 구성요소 | 기술 | 버전 |
|----------|------|------|
| 템플릿 엔진 | Django Templates + Partials | 6.0 내장 |
| 동적 UI | HTMX | 2.0+ |
| CSS 프레임워크 | Tailwind CSS | 3.4+ |
| 차트 | Chart.js | 4.4+ |
| 아이콘 | Lucide Icons | 최신 |

---

## 4. 데이터베이스 모델

### 4.1 models.py
```python
# apps/measurement/models.py
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class River(models.Model):
    """하천 정보"""
    name = models.CharField("하천명", max_length=100)
    code = models.CharField("하천코드", max_length=20, unique=True, blank=True)
    location = models.CharField("위치", max_length=200, blank=True)
    description = models.TextField("설명", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "하천"
        verbose_name_plural = "하천 목록"
        ordering = ["name"]

    def __str__(self):
        return self.name


class MeasurementStation(models.Model):
    """측정 지점"""
    river = models.ForeignKey(
        River,
        on_delete=models.CASCADE,
        related_name="stations",
        verbose_name="하천"
    )
    name = models.CharField("지점명", max_length=100)
    code = models.CharField("지점코드", max_length=20, blank=True)

    class Meta:
        verbose_name = "측정지점"
        verbose_name_plural = "측정지점 목록"

    def __str__(self):
        return f"{self.river.name} - {self.name}"


class MeasurementSession(models.Model):
    """측정 세션 (1회 측정)"""

    class WeatherChoices(models.TextChoices):
        SUNNY = "sunny", "맑음"
        CLOUDY = "cloudy", "흐림"
        RAINY = "rainy", "비"
        SNOWY = "snowy", "눈"

    class WindChoices(models.TextChoices):
        NONE = "none", "없음"
        WEAK = "weak", "약"
        MODERATE = "moderate", "중"
        STRONG = "strong", "강"

    station = models.ForeignKey(
        MeasurementStation,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="측정지점"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="측정자"
    )

    measurement_date = models.DateField("측정일")
    start_time = models.TimeField("시작시각", null=True, blank=True)
    end_time = models.TimeField("종료시각", null=True, blank=True)

    weather = models.CharField(
        "날씨",
        max_length=20,
        choices=WeatherChoices.choices,
        default=WeatherChoices.SUNNY
    )
    wind = models.CharField(
        "바람",
        max_length=20,
        choices=WindChoices.choices,
        default=WindChoices.NONE
    )

    # 파일
    source_file = models.FileField(
        "원본파일",
        upload_to="uploads/%Y/%m/",
        null=True,
        blank=True
    )

    # 계산 결과 (JSON)
    calculation_result = models.JSONField("계산결과", null=True, blank=True)
    uncertainty_result = models.JSONField("불확실도결과", null=True, blank=True)

    # 처리 상태
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "대기"
        PROCESSING = "processing", "처리중"
        COMPLETED = "completed", "완료"
        FAILED = "failed", "실패"

    status = models.CharField(
        "상태",
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    error_message = models.TextField("오류메시지", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "측정세션"
        verbose_name_plural = "측정세션 목록"
        ordering = ["-measurement_date", "-created_at"]

    def __str__(self):
        return f"{self.station} - {self.measurement_date}"


class MeasurementPoint(models.Model):
    """측선별 측정 데이터"""
    session = models.ForeignKey(
        MeasurementSession,
        on_delete=models.CASCADE,
        related_name="points",
        verbose_name="세션"
    )

    section_no = models.PositiveIntegerField("측선번호")
    distance = models.FloatField("거리(m)")
    depth = models.FloatField("수심(m)")
    measurement_time = models.TimeField("측정시각", null=True, blank=True)
    gauge_reading = models.FloatField("목자판(m)", null=True, blank=True)

    # 0.2D 측정값
    v02_depth = models.FloatField("0.2D깊이", null=True, blank=True)
    v02_angle = models.FloatField("0.2D각보정", default=1.0)
    v02_n = models.FloatField("0.2D회전수", null=True, blank=True)
    v02_t = models.FloatField("0.2D시간(초)", null=True, blank=True)

    # 0.6D 측정값 (기본)
    v06_depth = models.FloatField("0.6D깊이", null=True, blank=True)
    v06_angle = models.FloatField("0.6D각보정", default=1.0)
    v06_n = models.FloatField("0.6D회전수", null=True, blank=True)
    v06_t = models.FloatField("0.6D시간(초)", null=True, blank=True)

    # 0.8D 측정값
    v08_depth = models.FloatField("0.8D깊이", null=True, blank=True)
    v08_angle = models.FloatField("0.8D각보정", default=1.0)
    v08_n = models.FloatField("0.8D회전수", null=True, blank=True)
    v08_t = models.FloatField("0.8D시간(초)", null=True, blank=True)

    # 계산된 값 (캐시)
    calculated_velocity = models.FloatField("계산유속(m/s)", null=True, blank=True)
    calculated_area = models.FloatField("계산면적(m²)", null=True, blank=True)
    calculated_discharge = models.FloatField("계산유량(m³/s)", null=True, blank=True)

    class Meta:
        verbose_name = "측정점"
        verbose_name_plural = "측정점 목록"
        ordering = ["section_no"]
        unique_together = ["session", "section_no"]

    def __str__(self):
        return f"측선 {self.section_no} ({self.distance}m)"
```

---

## 5. 계산 서비스 (Background Task 활용)

### 5.1 tasks.py
```python
# apps/calculator/tasks.py
from django.tasks import task
from apps.measurement.models import MeasurementSession
from .services.discharge import DischargeCalculator
from .services.uncertainty import UncertaintyCalculator


@task
def calculate_discharge(session_id: int) -> dict:
    """
    Django 6.0 Background Task로 유량 계산
    """
    session = MeasurementSession.objects.get(id=session_id)
    session.status = MeasurementSession.StatusChoices.PROCESSING
    session.save(update_fields=["status"])

    try:
        points = session.points.all()

        # 유량 계산
        discharge_calc = DischargeCalculator()
        result = discharge_calc.calculate(points)

        # 불확실도 계산
        uncertainty_calc = UncertaintyCalculator()
        uncertainty = uncertainty_calc.calculate(points, result)

        # 결과 저장
        session.calculation_result = result
        session.uncertainty_result = uncertainty
        session.status = MeasurementSession.StatusChoices.COMPLETED
        session.save()

        return {"status": "success", "session_id": session_id}

    except Exception as e:
        session.status = MeasurementSession.StatusChoices.FAILED
        session.error_message = str(e)
        session.save()
        return {"status": "error", "message": str(e)}


@task
def generate_report(session_id: int, format: str = "pdf") -> str:
    """보고서 생성 백그라운드 작업"""
    from apps.reports.services.pdf_generator import PDFGenerator

    session = MeasurementSession.objects.get(id=session_id)
    generator = PDFGenerator(session)
    file_path = generator.generate()

    return file_path
```

### 5.2 views.py (HTMX 통합)
```python
# apps/calculator/views.py
from django.views import View
from django.views.generic import DetailView
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django_htmx.http import trigger_client_event

from apps.measurement.models import MeasurementSession
from .tasks import calculate_discharge


class CalculateView(View):
    """계산 시작 뷰 (HTMX)"""

    def post(self, request, session_id):
        session = get_object_or_404(MeasurementSession, id=session_id)

        # Django 6.0 Background Task 실행
        calculate_discharge.defer(session_id)

        # HTMX로 상태 업데이트 UI 반환
        return render(request, "calculator/partials/_processing.html", {
            "session": session,
        })


class CalculationStatusView(View):
    """계산 상태 확인 (HTMX Polling)"""

    def get(self, request, session_id):
        session = get_object_or_404(MeasurementSession, id=session_id)

        if session.status == MeasurementSession.StatusChoices.COMPLETED:
            # 완료되면 결과 페이지로
            response = render(request, "calculator/partials/_result.html", {
                "session": session,
                "result": session.calculation_result,
            })
            trigger_client_event(response, "calculation-complete")
            return response

        elif session.status == MeasurementSession.StatusChoices.FAILED:
            return render(request, "calculator/partials/_error.html", {
                "session": session,
            })

        # 아직 처리중이면 계속 폴링
        return render(request, "calculator/partials/_processing.html", {
            "session": session,
        })


class ResultDetailView(DetailView):
    """결과 상세 페이지"""
    model = MeasurementSession
    template_name = "calculator/result_detail.html"
    context_object_name = "session"
```

---

## 6. 템플릿 예시

### 6.1 base.html
```html
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}수문 유량 분석{% endblock %}</title>

    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>

    <!-- HTMX -->
    <script src="https://unpkg.com/htmx.org@2.0.0"></script>

    <!-- Django CSP (6.0 신기능) -->
    {% load csp %}
    {% csp_nonce %}

    {% block extra_head %}{% endblock %}
</head>
<body class="bg-gray-50 min-h-screen">
    {% include "partials/_navbar.html" %}

    <main class="container mx-auto px-4 py-8">
        {% block content %}{% endblock %}
    </main>

    {% include "partials/_footer.html" %}

    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 6.2 계산 결과 (HTMX + Partials)
```html
<!-- templates/calculator/partials/_result.html -->
{% load humanize %}

<div id="result-section" class="bg-white rounded-lg shadow p-6">
    <h2 class="text-xl font-bold mb-4">계산 결과</h2>

    <!-- 요약 카드 -->
    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        {% partial result_card %}
        <div class="bg-blue-50 p-4 rounded-lg">
            <div class="text-sm text-blue-600">{{ label }}</div>
            <div class="text-2xl font-bold">{{ value }}</div>
            <div class="text-xs text-gray-500">{{ unit }}</div>
        </div>
        {% endpartial %}

        {% include_partial "result_card" label="유량" value=result.total_discharge|floatformat:4 unit="m³/s" %}
        {% include_partial "result_card" label="단면적" value=result.total_area|floatformat:3 unit="m²" %}
        {% include_partial "result_card" label="평균유속" value=result.mean_velocity|floatformat:3 unit="m/s" %}
        {% include_partial "result_card" label="불확실도" value=session.uncertainty_result.total|floatformat:1 unit="%" %}
    </div>

    <!-- 측선별 상세 테이블 -->
    <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
                <tr>
                    <th class="px-4 py-2 text-left text-xs font-medium text-gray-500">측선</th>
                    <th class="px-4 py-2 text-right">거리(m)</th>
                    <th class="px-4 py-2 text-right">수심(m)</th>
                    <th class="px-4 py-2 text-right">유속(m/s)</th>
                    <th class="px-4 py-2 text-right">면적(m²)</th>
                    <th class="px-4 py-2 text-right">유량(m³/s)</th>
                </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
                {% for section in result.sections %}
                <tr class="hover:bg-gray-50">
                    <td class="px-4 py-2">{{ section.section_no }}</td>
                    <td class="px-4 py-2 text-right">{{ section.distance|floatformat:2 }}</td>
                    <td class="px-4 py-2 text-right">{{ section.depth|floatformat:3 }}</td>
                    <td class="px-4 py-2 text-right">{{ section.velocity|floatformat:3 }}</td>
                    <td class="px-4 py-2 text-right">{{ section.area|floatformat:4 }}</td>
                    <td class="px-4 py-2 text-right">{{ section.discharge|floatformat:5 }}</td>
                </tr>
                {% endfor %}
            </tbody>
            <tfoot class="bg-gray-100 font-bold">
                <tr>
                    <td colspan="4" class="px-4 py-2">합계</td>
                    <td class="px-4 py-2 text-right">{{ result.total_area|floatformat:3 }}</td>
                    <td class="px-4 py-2 text-right">{{ result.total_discharge|floatformat:4 }}</td>
                </tr>
            </tfoot>
        </table>
    </div>

    <!-- 내보내기 버튼 -->
    <div class="mt-6 flex gap-4">
        <button hx-get="{% url 'reports:export_excel' session.id %}"
                hx-swap="none"
                class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">
            Excel 다운로드
        </button>
        <button hx-get="{% url 'reports:export_pdf' session.id %}"
                hx-swap="none"
                class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">
            PDF 다운로드
        </button>
    </div>
</div>
```

---

## 7. 개발 환경 설정

### 7.1 초기화 스크립트
```bash
# Windows PowerShell

# 1. 프로젝트 디렉토리 생성
mkdir reAA
cd reAA

# 2. Python 가상환경
python -m venv venv
.\venv\Scripts\Activate.ps1

# 3. Django 6.0 설치
pip install Django>=6.0

# 4. 프로젝트 생성
django-admin startproject config .

# 5. 앱 디렉토리 구조
mkdir apps
mkdir apps\core apps\measurement apps\calculator apps\reports

# 6. 각 앱 생성
python manage.py startapp core apps/core
python manage.py startapp measurement apps/measurement
python manage.py startapp calculator apps/calculator
python manage.py startapp reports apps/reports

# 7. 나머지 의존성 설치
pip install django-htmx openpyxl xlrd pandas numpy reportlab python-dotenv

# 8. 마이그레이션
python manage.py migrate

# 9. 슈퍼유저 생성
python manage.py createsuperuser

# 10. 개발 서버 실행
python manage.py runserver
```

### 7.2 settings.py 주요 설정
```python
# config/settings/base.py

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "django_htmx",

    # Local apps
    "apps.core",
    "apps.measurement",
    "apps.calculator",
    "apps.reports",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # 정적 파일
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",  # HTMX
    "csp.middleware.CSPMiddleware",  # Django 6.0 CSP
]

# Django 6.0 Background Tasks
TASKS = {
    "default": {
        "BACKEND": "django.tasks.backends.database.DatabaseBackend",
    }
}

# Django 6.0 CSP 설정
CONTENT_SECURITY_POLICY = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "https://unpkg.com", "https://cdn.tailwindcss.com"],
    "style-src": ["'self'", "'unsafe-inline'", "https://cdn.tailwindcss.com"],
}
```

---

## 8. 개발 로드맵

| Phase | 작업 | 설명 |
|-------|------|------|
| **1** | 프로젝트 초기화 | Django 6.0 설정, 앱 구조 |
| **2** | 모델 정의 | River, Station, Session, Point |
| **3** | Excel 파서 | openpyxl + xlrd 파싱 서비스 |
| **4** | 계산 엔진 | 유속, 유량, 불확실도 |
| **5** | UI 개발 | HTMX + Tailwind 템플릿 |
| **6** | Background Tasks | 대용량 파일 비동기 처리 |
| **7** | 보고서 | Excel/PDF 내보내기 |
| **8** | 테스트 | Excel 결과와 비교 검증 |
| **9** | 배포 | 웹 서버 또는 데스크톱 |

---

## 9. 참고 자료

- [Django 6.0 Release Notes](https://docs.djangoproject.com/en/dev/releases/6.0/)
- [Django 6.0 Released - Official Blog](https://www.djangoproject.com/weblog/2025/dec/03/django-60-released/)
- [Django 6.0 New Features - Adam Johnson](https://adamj.eu/tech/2025/12/03/django-whats-new-6.0/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/)

---

*작성일: 2025-12-19*
*Django 버전: 6.0*
