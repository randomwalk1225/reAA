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

## 디버그 엔드포인트
- `/hydro/api/debug/env/` - Railway 환경변수 확인용 (프로덕션에서 제거 권장)
