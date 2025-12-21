# HydroLink 프로젝트 가이드

## 프로젝트 개요
Django 기반 수문 데이터 분석 웹 애플리케이션

## 기술 스택
- Django 6.0
- Python 3.12
- uv (패키지 관리)
- Chart.js, Alpine.js (프론트엔드)
- Railway (배포)
- Google Earth Engine (위성 데이터)

## 주요 앱
- `core`: 기본 페이지
- `measurement`: 유량 측정, 기저유출 분석
- `satellite`: 위성 영상
- `hydro`: 실시간 수문 데이터, GEE 증발산량

---

# 에러 로그 및 해결 방법

## 2025-12-21

### 1. 기저유출 분석 - Maximum call stack size exceeded

**원인**: Alpine.js 반응성 + 함수 무한 루프

**해결**:
- 디바운스 함수 `debouncedRunAnalysis()` 추가
- `loading` 가드 추가

---

### 2. Chart.js - Cannot set properties of undefined (setting 'fullSize')

**원인**: DOM 준비 전 차트 초기화

**해결**:
- `initChart()`에 null 체크, try-catch 추가
- `$nextTick()` + `setTimeout` 사용

---

### 3. 모바일에서 차트 미표시

**원인**: 컨테이너 너비 미지정, sticky 레이아웃 충돌

**해결**:
```html
<div class="relative w-full" style="height: 300px; min-height: 250px;">
    <canvas id="baseflowChart" class="w-full h-full"></canvas>
</div>
```
- sticky → `lg:sticky lg:top-24`
- 그리드 → `grid-cols-2 sm:grid-cols-4`
- resize 이벤트 리스너 추가

---

### 4. Railway GEE 초기화 실패

**원인**: JSON 환경변수 특수문자 처리 문제

**해결**:
1. Base64 인코딩 방식:
```
GEE_CLIENT_EMAIL=gee-hydrolink@hydrolink-481811.iam.gserviceaccount.com
GEE_PRIVATE_KEY=<base64_encoded_private_key>
```

2. 임시 파일 + `key_file` 파라미터 사용

3. 필수 필드 포함:
- `token_uri`: 'https://oauth2.googleapis.com/token'
- `auth_uri`, `auth_provider_x509_cert_url`, `client_x509_cert_url`, `universe_domain`

**Base64 인코딩 (PowerShell)**:
```powershell
$json = Get-Content -Raw "resource/googlekey/hydrolink-481811-3c7f2f9745eb.json" | ConvertFrom-Json
[Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($json.private_key))
```

---

### 5. 기저유출 분석 - 분석 실행 후 차트 미표시 (리사이즈 시에만 표시)

**원인**: `chart.update('none')` 사용 시 렌더링 스킵 문제

**해결**:
- `update('none')` → `update()` 로 변경 (기본 애니메이션 사용)
```javascript
// 잘못된 방식
this.chart.update('none');  // 애니메이션 비활성화 → 렌더링 문제 발생

// 올바른 방식
this.chart.update();  // 기본 애니메이션으로 즉시 렌더링
```

---

### 6. 기저유출 분석 - 자동 데이터 로드 시 차트 에러

**에러 메시지**: `Cannot set properties of undefined (setting 'fullSize')`

**원인**: URL 파라미터로 관측소가 자동 선택되어 데이터 로드가 시작되지만, 차트 초기화(50ms)보다 데이터 로드 완료가 먼저 일어나는 경우

**발생 시나리오**:
1. `/measurement/baseflow/new/?station=1` 접속
2. `init()`에서 `initChart()`가 50ms 후 실행 예약
3. `init()`에서 `loadStationData()`가 100ms 후 실행 예약
4. 데이터 로드가 빠르게 완료되어 `updateChartData()` 호출
5. 차트가 아직 초기화되지 않아 에러 발생

**해결**:
- `updateChartData()`에서 차트 초기화 재시도 시 try-catch 추가
- 차트 객체 유효성 검사 강화
```javascript
updateChartData() {
    if (!this.chart) {
        this.initChart();
        if (!this.chart) return;  // 초기화 실패 시 리턴
    }
    try {
        this.chart.data.labels = this.dateLabels;
        // ...
        this.chart.update();
    } catch (e) {
        console.error('Chart update error:', e);
        // 차트 재초기화 시도
        this.chart = null;
        this.initChart();
    }
}
```

---

### 7. 데이터 불안정 (저장 후 사라짐)

**원인**: `DATABASE_URL` 환경변수 미설정 → SQLite 폴백 → 컨테이너 재시작 시 데이터 손실

**해결**: Railway에서 PostgreSQL 서비스 추가 후 `DATABASE_URL` 환경변수 연결
- Railway Dashboard → 앱 서비스 → Variables → `DATABASE_URL` 추가
- PostgreSQL 서비스와 Reference Variable로 연결

**진단 방법**: `/hydro/api/debug/env/` 엔드포인트에서 `DATABASE_URL` 확인

---

### 8. 저장 버튼 중복 클릭 시 다중 저장

**원인**: 빠른 연속 클릭 시 race condition 발생

**해결**:
- 프론트엔드: `_saveLock` 동기적 잠금 추가
- 백엔드: `transaction.atomic()` + `select_for_update()` 적용

---

### 9. 기저유출 분석 - 관측소 변경 시 차트 미갱신

**원인**:
1. 관측소 변경 시 새 데이터 자동 로드 미구현
2. 차트 업데이트 시 기존 차트 인스턴스 재사용으로 인한 렌더링 문제

**해결**:
1. `selectInternalStation()`에서 관측소 변경 시 자동 데이터 로드
2. `updateChartData()`에서 기존 차트 파괴 후 재생성

```javascript
selectInternalStation() {
    if (this.selectedInternalStationId) {
        this.selectedInternalStation = this.internalStations[this.selectedInternalStationId];
        // 관측소 변경 시 기존 데이터 초기화 및 새 데이터 자동 로드
        this.dischargeData = [];
        this.baseflowData = [];
        this.results = null;
        this.loadStationData();  // 자동 로드
    }
},

updateChartData() {
    // 기존 차트 파괴
    if (this.chart) {
        this.chart.destroy();
        this.chart = null;
    }
    // 새 차트 생성
    this.$nextTick(() => {
        this.initChart();
        if (this.chart) {
            this.chart.data.labels = this.dateLabels;
            this.chart.data.datasets[0].data = this.dischargeData;
            this.chart.data.datasets[1].data = this.baseflowData;
            this.chart.update();
        }
    });
}
```

---

## 디버그 엔드포인트
- `/hydro/api/debug/env/` - Railway 환경변수 확인용 (프로덕션에서 제거 권장)

---

# 사용자 피드백 및 향후 기능 요청

## 박승혁 (2025-12-21)

### 댐 수문 영향 표기 기능

**현재 상태**: 강수량 시자료와 수위 시자료만 고려

**개선 요청**:
- 댐 수문이 열고 닫히는 시간을 파악
- 현재 측정 시각에서 댐 수문 영향 유무를 유량값에 표기

**구현 방향 (검토 필요)**:
1. 댐 수문 개폐 시간 데이터 소스 확보
2. 측정 시각 기준 상류 댐까지의 도달시간 고려
3. 유량 데이터에 `dam_influenced: true/false` 플래그 추가
4. UI에서 댐 영향 여부 시각적 표시 (아이콘 또는 색상)
