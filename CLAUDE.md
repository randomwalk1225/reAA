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

## 업무 방식 주의사항

### 백그라운드 로컬 서버 금지 (2025-12-22)

**문제**: 로컬 테스트를 위해 백그라운드로 Django 서버를 여러 개 실행하면 리소스 낭비 및 포트 충돌 발생

**규칙**:
1. 로컬 테스트 최소화 - 바로 Railway에 배포 후 테스트
2. 백그라운드 서버 실행 금지
3. Playwright 테스트는 프로덕션 서버 대상으로만 실행
4. 코드 수정 → 즉시 커밋 → 배포 → 프로덕션 테스트

---

# 사용자 피드백 및 향후 기능 요청

## 박승혁 (2025-12-21)

### 1. 댐 수문 영향 표기 기능

**현재 상태**: 강수량 시자료와 수위 시자료만 고려

**개선 요청**:
- 댐 수문이 열고 닫히는 시간을 파악
- 현재 측정 시각에서 댐 수문 영향 유무를 유량값에 표기

**데이터 소스 확보 완료 (2025-12-22)**:
- **한국수자원공사_수문 방류정보 조회 서비스** API 발견
- 엔드포인트: `https://apis.data.go.kr/B500001/DamDisChargeInfo/flugdschginfo`
- 제공 필드: STARTDATE(방류시작), ENDDATE(방류종료), DAMNM(댐명), AFFECTAREA(영향범위)
- 갱신주기: 15분
- 상세 정보: [홍수통제소 정보 제공 현황 > 5. 수문 방류정보 조회 API](#5-수문-방류정보-조회-api-댐-수문-개폐-시간) 참조

**구현 방향**:
1. **환경변수**: `DAM_DISCHARGE_API_KEY` - 공공데이터포털 인증키
2. **서비스 레이어**: `hydro/services/dam_discharge.py`
   - `fetch_dam_discharge_info(date)`: 해당일 방류 정보 조회
   - `is_dam_discharging(dam_code, datetime)`: 특정 시각 방류 여부 확인
   - `get_upstream_dams(station_code)`: 관측소 상류 댐 목록 (매핑 테이블 필요)
3. **도달시간 고려**:
   - 댐-관측소 간 거리/하천 특성에 따른 도달시간 테이블 구축
   - `측정시각 - 도달시간` 범위 내 방류 여부 판단
4. **유량 데이터 연동**:
   - `dam_influenced: true/false` 플래그 추가
   - `influencing_dams: ["팔당댐", "충주댐"]` 영향 댐 목록
5. **UI 표시**:
   - 유량 측정 화면에 댐 영향 배지/아이콘 표시
   - 툴팁으로 상세 정보 (어떤 댐, 방류 시작/종료 시간)

---

### 2. 유속계 관리 기능 (2:40 PM)

**현재 상태**: 유속계를 새로 입력 후 적용 불가

**개선 요청**:
- 유속계 종류
- 명칭
- 상관식 (회전수 → 유속 변환식)
- 유효범위
- 검정 유효기간

**구현 방향**:
1. `Meter` 모델 생성 (type, name, equation, valid_range, calibration_expiry)
2. 유속계 관리 페이지 CRUD 구현 (`/measurement/meters/`)
3. 유량 측정 시 유속계 선택 및 상관식 자동 적용

---

### 3. 금강/낙동강 관측소 추가 (2:41 PM)

**현재 상태**: 한강홍수통제소(HRFCO) API만 연동 → 한강 권역만 선택 가능

**개선 요청**:
- 금강, 낙동강 지역 관측소 선택 가능하도록
- 측정 지점 직접 추가 기능

**구현 방향**:
1. 금강홍수통제소, 낙동강홍수통제소 API 연동 추가
2. 또는 WAMIS 전국 통합 API 연동
3. 사용자 정의 관측소 추가 기능 (위경도, 하천명 입력)

---

### 4. 로컬 앱 + 유역유출고 평가 (4:12 PM)

**요청 내용**:
- 유량측정을 앱으로 해서 결과값이 바로 나오고
- 유역유출고에 맞는지 평가만 되면 로컬앱에서 가능할 듯

**의미**: 현장에서 측정 → 즉시 결과 확인 → 유역유출고 기준 적합성 평가

---

### 5. 사전 유출량 한계 산정 기능 (4:14 PM)

**요청 내용**:
- 출발 전에 미리 강수량 관측지점 입력
- 해당 지점의 유역면적에서 최대 하천유출량 값 한계를 산정
- 정량적은 아니더라도 가늠 가능
- 나중에 정량적으로 보고서에 넣으면 좋겠음

**구현 방향 (검토 필요)**:
1. 유역면적 입력 (또는 GIS 기반 자동 산정)
2. 강수량 데이터 연동 (기상청 API 또는 HRFCO)
3. 단위유량도법 또는 합리식으로 예상 최대 유출량 산정
4. 측정 전 "예상 유량 범위" 제공 → 현장 측정값과 비교

---

### 6. Excel 분석결과표 항목 조정 (9:00 PM)

**요청 내용**:
- 평균폭~평균불확실도까지, 유량등급까지요
- 중간에 다른것은 없어도돼요

**수정 항목**:
- 수면폭, 단면적, 윤변, 동수반경, 수위, 평균유속, 평균유량, 유속측선수, 불확실도①, 평균불확실도, 수위고도, 유량조사 등급
- 제거 항목: 불확실도②, 보상단고, 물넘이바닥고도

---

### 7. 유속계 방향 보정 기능 (9:00 PM)

**요청 내용**:
- 입력창에 유속계방향관련 index 각각도로 넣으면 탄젠트로 환산되게 부탁드려요
- 엑셀시트가 이것에 맞게 20년전에 만들어진 것인데 index넣어 유속각보정하는게 빠져있는듯요

**참고 문서**:
- [2016년 수문조사보고서_이론및방법총괄.pdf](file:///C:/Users/rando/repos/reAA/resource/공부용자료/2016년%20수문조사보고서_이론및방법총괄.pdf)
- 그림 1.50: 이용을 위한 보정계수 θ 결정

**구현 방향**:
1. 데이터 입력창에 유속계 방향 각도(θ) 입력 필드 추가
2. 입력된 각도를 탄젠트로 환산하여 유속 보정
3. 보정 공식: `V_corrected = V_measured * cos(θ)` 또는 보고서 기준 적용

---

# 참고 사이트

## K-water MyWater 원클릭 수자원 정보

**URL**: https://www.water.or.kr/kor/realtime/oneClick/index.do?menuId=13_91_295

**평가**: 매우 잘 만든 수자원 통합 데이터 센터

### 주요 기능

| 기능 | 설명 |
|------|------|
| 실시간 수위/저수율 | 현재수위, 저수율, 유입량/방류량 (m³/s) |
| 수질 모니터링 | pH, 수온, 탁도(NTU), 전기전도도, 알칼리도, 2-MIB, Geosmin, 조류 |
| 다중 댐 선택 | 팔당, 운문, 달방, 대암, 대청, 사연, 수어 등 7개 시설 |
| 데이터 시각화 | 8개 파라미터 동시 차트, 최대 7일 범위 |
| 데이터 내보내기 | Excel 내보내기 지원 |

### UI/UX 특징

- 21개 언어 지원 (Google Translate 연동)
- AI 챗봇 기능
- 날씨/대기질 위젯
- 반응형 모바일 디자인
- 사용자 만족도 조사 (별점)

### 벤치마킹 포인트

1. **원클릭 대시보드**: 여러 데이터를 한 화면에 통합 표시
2. **다중 파라미터 차트**: 8개 지표 동시 시각화
3. **시설별 지도 연동**: 선택한 댐/시설의 위치 지도 표시
4. **날짜 범위 선택**: 유연한 기간 설정 (최대 7일)
5. **데이터 테이블**: 시계열 데이터 표 형식 제공

---

# 홍수통제소 정보 제공 현황 (2025-12-22)

## 개요

국내 홍수통제소 Open API 현황. **인증키 필수** - URL만으로 바로 데이터 조회 불가.

## 1. 한강홍수통제소 Open API (핵심 - 전국 4대강 통합)

**공식 사이트**: https://www.hrfco.go.kr/web/openapiPage/openApi.do
**API 레퍼런스**: https://www.hrfco.go.kr/web/openapiPage/reference.do
**공공데이터포털**: https://www.data.go.kr/data/3040409/openapi.do

### 특징
- **전국 4대강 데이터 통합 제공** (한강, 낙동강, 금강, 영산강)
- 금강/낙동강/영산강 홍수통제소는 별도 API 없음 → 이 API 사용
- JSON, XML 형식 지원
- 1분당 1,000건 제한

### URL 구조
```
https://api.hrfco.go.kr/{ServiceKey}/{HydroType}/{DataType}/{TimeUnit}/{StationCode}/{StartTime}/{EndTime}.{Format}
```

### 제공 데이터 종류

| HydroType | 설명 | 응답 필드 |
|-----------|------|----------|
| waterlevel | 수위 | 현재수위 (El.m), 유량 |
| rainfall | 강수량 | 시간별 강수량 |
| dam | 댐 | 현재수위, 총 방류량 (m³/s) |
| bo | 보 | 수위, 유량 |
| radar | 강우레이더 | 영상 정보 |
| fldfct | 홍수예보 | 발표일시, 지점 |

### 시간 단위

| 코드 | 의미 | 최대 조회 기간 |
|------|------|---------------|
| 10M | 10분 | 1개월 |
| 1H | 1시간 | 1년 |
| 1D | 1일 | 1년 |

### URL 예시

**수위(Waterlevel)**
```
# 전체 10분 자료
https://api.hrfco.go.kr/{ServiceKey}/waterlevel/list/10M.xml

# 한강대교(1018683) 10분 자료
https://api.hrfco.go.kr/{ServiceKey}/waterlevel/list/10M/1018683.xml

# 기간별 조회 (yyyyMMddHHmm 형식)
https://api.hrfco.go.kr/{ServiceKey}/waterlevel/list/10M/1018683/202503230710/202503240710.json
```

**강수량(Rainfall)**
```
https://api.hrfco.go.kr/{ServiceKey}/rainfall/list/10M/10184100.xml
```

**댐(Dam)**
```
https://api.hrfco.go.kr/{ServiceKey}/dam/list/10M.xml
```

**홍수예보(Flood Forecast)**
```
https://api.hrfco.go.kr/{ServiceKey}/fldfct/list.xml
```

### 주의사항
- 관측소코드 미지정 시 최종 시간 자료만 반환
- 기간 조회 시 관측소코드 필수
- 낙동강/금강/영산강 데이터는 한강보다 수집 지연 (11분 이상)

---

## 2. WAMIS 국가수자원관리종합정보시스템

**공식 사이트**: https://www.wamis.go.kr/
**인증키 신청**: http://www.wamis.go.kr:8080/wamisweb/mn/w54.do
**GitHub 튜토리얼**: https://github.com/hyunholee26/Tutorial-Hydrology-data-collection-using-WAMIS-OpenAPI

### 특징
- 환경부 한강홍수통제소 관리
- 강수량, 수위, 기상 등 다양한 수문 데이터
- Python 연동 용이

### 주요 API 엔드포인트

| 데이터 | 엔드포인트 |
|--------|-----------|
| 수위 시간자료 | `http://www.wamis.go.kr:8080/wamis/openapi/wkw/wl_hrdata` |
| 기상 시간자료 | `http://www.wamis.go.kr:8080/wamis/openapi/wkw/we_hrdata` |
| 관측소 정보 | `http://www.wamis.go.kr:8080/wamis/openapi/wkd/mn_obsinfo` |

### 파라미터

| 파라미터 | 설명 | 예시 |
|---------|------|------|
| ServiceKey | 인증키 | (발급받은 키) |
| ResultType | 응답 형식 | json |
| obscd | 관측소 코드 | 1012650 |
| startdt | 시작일 (YYYYMMDD) | 20241201 |
| enddt | 종료일 (YYYYMMDD) | 20241222 |

### Python 코드 예시

```python
import requests

url = "http://www.wamis.go.kr:8080/wamis/openapi/wkw/wl_hrdata"
params = {
    "ServiceKey": "YOUR_API_KEY",
    "ResultType": "json",
    "obscd": "1012650",
    "startdt": "20241201",
    "enddt": "20241222"
}
response = requests.get(url, params=params)
data = response.json()["result"]["data"]
```

### 기상 데이터 응답 필드
- ymdh: 시간
- ta: 기온
- hm: 습도
- ws: 풍속
- wd: 풍향
- sihr1, catot, sdtot: 기타 기상 요소

---

## 3. 개별 홍수통제소 (별도 API 없음)

| 홍수통제소 | 공식 사이트 | API 상태 |
|-----------|-----------|---------|
| 금강 | https://www.geumriver.go.kr/ | 별도 API 없음 → HRFCO API 사용 |
| 낙동강 | https://www.nakdongriver.go.kr/ | 별도 API 없음 → HRFCO API 사용 |
| 영산강 | https://www.yeongsanriver.go.kr/ | 별도 API 없음 → HRFCO API 사용 |

---

## 4. 공공데이터포털 관련 API

**공식 사이트**: https://www.data.go.kr/

| API명 | 링크 | 활용신청 |
|-------|------|---------|
| 한강홍수통제소_표준수문DB | https://www.data.go.kr/data/3040409/openapi.do | 1,825건 |
| 낙동강홍수통제소_홍수예보정보 | https://www.data.go.kr/data/3039647/fileData.do | - |
| 한강홍수통제소_강우레이더영상 | https://www.data.go.kr/data/15021451/openapi.do | - |
| **한국수자원공사_수문 방류정보 조회** | https://www.data.go.kr/data/15140222/openapi.do | - |

---

## 5. 수문 방류정보 조회 API (댐 수문 개폐 시간)

**공공데이터포털**: https://www.data.go.kr/data/15140222/openapi.do

### API 정보

| 항목 | 내용 |
|------|------|
| 엔드포인트 | `https://apis.data.go.kr/B500001/DamDisChargeInfo/flugdschginfo` |
| 갱신주기 | 15분 |
| 형식 | XML |
| 비용 | 무료 |
| 제공기관 | 한국수자원공사 (K-water) |

### 요청 파라미터

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| serviceKey | string | O | 공공데이터포털 인증키 |
| pageNo | string | O | 페이지 번호 |
| numOfRows | string | O | 페이지당 결과 수 |
| stDt | string | X | 시작일 (YYYYMMDD) |
| edDt | string | X | 종료일 (YYYYMMDD) |
| damCd | string | X | 댐 코드 |

### 응답 필드 (핵심)

| 필드 | 설명 | 용도 |
|------|------|------|
| **STARTDATE** | 방류 시작 시간 | 수문 개방 시간 |
| **ENDDATE** | 방류 종료 시간 | 수문 폐쇄 시간 |
| DAMCD | 댐 코드 | 댐 식별 |
| DAMNM | 댐 이름 | 표시용 |
| DAMCOORD | 댐 좌표 | 지도 표시 |
| AFFECTAREA | 영향 범위 | 하류 영향 지역 |
| UPDATEDDATE | 업데이트 시간 | 데이터 최신성 확인 |

### 요청 예시
```
GET https://apis.data.go.kr/B500001/DamDisChargeInfo/flugdschginfo
?serviceKey={인증키}
&pageNo=1
&numOfRows=100
&stDt=20241222
&edDt=20241222
```

### Python 코드 예시
```python
import requests
import xml.etree.ElementTree as ET

url = "https://apis.data.go.kr/B500001/DamDisChargeInfo/flugdschginfo"
params = {
    "serviceKey": "YOUR_API_KEY",
    "pageNo": "1",
    "numOfRows": "100",
    "stDt": "20241222",
    "edDt": "20241222"
}
response = requests.get(url, params=params)
root = ET.fromstring(response.content)

for item in root.findall('.//item'):
    dam_name = item.find('DAMNM').text
    start_time = item.find('STARTDATE').text
    end_time = item.find('ENDDATE').text
    affect_area = item.find('AFFECTAREA').text
    print(f"{dam_name}: {start_time} ~ {end_time}, 영향범위: {affect_area}")
```

---

## 인증키 발급 절차

### 한강홍수통제소 API
1. https://www.hrfco.go.kr/web/openapiPage/openApi.do 접속
2. "오픈API 사용 신청" 메뉴 클릭
3. 회원가입/로그인
4. 인증키 발급 신청
5. 발급된 ServiceKey로 API 호출

### WAMIS API
1. http://www.wamis.go.kr/ 접속
2. OpenAPI 메뉴 클릭
3. 로그인
4. OpenAPI 활용 신청 및 키 확인

### 공공데이터포털 API
1. https://www.data.go.kr/ 접속
2. 회원가입/로그인
3. 원하는 API 검색 후 "활용신청"
4. 개발계정: 1일 1,000건 / 운영계정: 1일 10만건

---

## 교육용 요약

**Q: 금강/낙동강 데이터는 어디서 가져오나요?**
A: 한강홍수통제소 Open API가 **전국 4대강을 통합 제공**합니다. 별도 금강/낙동강 API는 없습니다.

**Q: URL만 입력하면 바로 데이터 받을 수 있나요?**
A: 아니요. 모든 API는 **인증키(ServiceKey) 필수**입니다. 사전에 발급받아야 합니다.

**Q: 가장 쉬운 방법은?**
A: 한강홍수통제소 API 인증키 발급 → REST API로 JSON 데이터 조회

**Q: Python으로 연동하려면?**
A: `requests` 라이브러리로 GET 요청. WAMIS GitHub 튜토리얼 참고.

---

# 수질/위치 데이터 자동 입력 기능 개발 계획 (2025-12-31)

## 개요

유량 측정 시 수질 데이터(PH, ORP, 수온, EC, TDS)와 위치 정보(위도, 경도)를 입력할 수 있도록 하며, 수동 입력을 기본으로 하되 자동 입력 옵션을 제공한다.

## 구현 단계

### Phase 1: 수동 입력 UI 추가 ✅ 완료 (2025-12-31)

**목표**: 데이터 입력 화면에 수질/위치 필드 추가

**작업 내용**:
1. `templates/measurement/data_input.html` 수정
   - PC/모바일 레이아웃에 접이식 "추가 정보" 섹션 추가
   - 위치 정보 섹션: 위도, 경도
   - 수질 정보 섹션: PH, ORP, 수온(℃), EC(μS/cm), TDS(mg/L)
2. JavaScript `extraData` 객체 추가
   - `calculate()` 함수에서 서버로 전송

**검증 방법**:
- [x] 데이터 입력 화면에서 수질/위치 필드 표시 확인
- [ ] 값 입력 후 저장 확인 (백엔드 연동 필요)
- [ ] 상세 페이지에서 저장된 값 표시 확인 (추후 구현)

---

### Phase 2: 위도/경도 자동 입력 ⬜

**목표**: 관측소 선택 시 해당 관측소의 좌표 자동 입력

**데이터 소스**:
- 한강홍수통제소 표준수문DB API
- 엔드포인트: `https://api.hrfco.go.kr/{ServiceKey}/waterlevel/info/{StationCode}.json`

**작업 내용**:
1. HRFCO API에서 관측소 정보 조회 시 좌표 포함하여 반환
2. 프론트엔드에서 관측소 선택 시 위도/경도 필드 자동 채우기
3. "자동 입력" 버튼 또는 체크박스 UI 추가
4. 수동 수정 가능하도록 필드 편집 허용

**API 응답 예시** (확인 필요):
```json
{
  "stationCode": "1018683",
  "stationName": "한강대교",
  "latitude": 37.5172,
  "longitude": 126.9784,
  "riverName": "한강"
}
```

**검증 방법**:
- [ ] 관측소 선택 시 좌표 자동 입력 확인
- [ ] 좌표 없는 관측소 선택 시 빈 값 유지 확인
- [ ] 수동으로 좌표 수정 가능 확인

---

### Phase 3: 인근 수질측정소 데이터 참조 (선택적) ⬜

**목표**: 버튼 클릭 시 가장 가까운 수질측정소의 최신 데이터 가져오기

**데이터 소스**:
- 물환경정보시스템 자동측정망 API
- 엔드포인트: `https://www.data.go.kr/data/15081073/openapi.do`

**제공 항목**: 수온, pH, EC, DO, 탁도, TOC, TN, TP

**주의사항**:
- ORP, TDS는 API에서 제공하지 않음 → 수동 입력 필요
- 측정소 위치가 유량 측정 지점과 다를 수 있음 → 참고용으로만 사용

**작업 내용**:
1. 물환경정보시스템 API 인증키 발급 및 환경변수 등록
2. `hydro/services/water_quality.py` 서비스 레이어 생성
3. 위도/경도 기반 가장 가까운 측정소 찾기 로직
4. "인근 측정소 데이터 가져오기" 버튼 UI 추가
5. 가져온 값 표시 + 수동 수정 가능

**검증 방법**:
- [ ] 버튼 클릭 시 인근 측정소 데이터 표시 확인
- [ ] 측정소 없을 경우 안내 메시지 확인
- [ ] 가져온 값 수동 수정 가능 확인

---

### Phase 4: CSV Import 수질 데이터 파싱 ⬜

**목표**: CSV 파일에 수질 데이터 포함 시 자동 파싱

**CSV 형식 확장**:
```
# 기존 CSV 헤더에 추가
위도,경도,PH,ORP,수온,EC,TDS
```

**작업 내용**:
1. `api_batch_import_csv` 함수 수정
2. CSV 헤더에서 수질/위치 컬럼 인식
3. 값 파싱 후 MeasurementSession에 저장

**검증 방법**:
- [ ] 수질 데이터 포함 CSV 업로드 시 값 저장 확인
- [ ] 수질 데이터 없는 CSV도 정상 처리 확인

---

### Phase 5: Excel Export 수질/위치 테이블 추가 ⬜

**목표**: Excel 분석결과표에 수질/위치 정보 테이블 추가

**추가할 테이블 형식**:
```
| 공번 | 위도 | 경도 | 유량(m³/d) | PH | ORP | 수온 | EC | TDS |
|------|------|------|-----------|-----|-----|------|-----|-----|
| GJSW-1 | 35.76562 | 129.454039 | 292,693.80 | 7.31 | 85.6 | 25.14 | 184 | 92 |
```

**작업 내용**:
1. `export_analysis_excel` 함수 수정
2. 데이터 테이블 아래에 수질/위치 정보 테이블 추가
3. 스타일 적용 (테두리, 헤더 색상)

**검증 방법**:
- [ ] Excel 다운로드 시 수질/위치 테이블 포함 확인
- [ ] 데이터 없을 경우 빈 테이블 또는 "-" 표시 확인

---

## API 인증키 필요 목록

| API | 환경변수명 | 발급처 | 상태 |
|-----|-----------|--------|------|
| 한강홍수통제소 | `HRFCO_API_KEY` | hrfco.go.kr | ✅ 발급완료 |
| 물환경정보시스템 | `WATER_QUALITY_API_KEY` | data.go.kr | ⬜ 미발급 |

---

## 모델 필드 현황

**MeasurementSession 모델** (measurement/models.py):

| 필드명 | 타입 | 설명 | 상태 |
|--------|------|------|------|
| latitude | FloatField | 위도 | ✅ 추가완료 |
| longitude | FloatField | 경도 | ✅ 추가완료 |
| ph | FloatField | PH | ✅ 추가완료 |
| orp | FloatField | ORP | ✅ 추가완료 |
| water_temp | FloatField | 수온(℃) | ✅ 추가완료 |
| ec | FloatField | EC(μS/cm) | ✅ 추가완료 |
| tds | FloatField | TDS(mg/L) | ✅ 추가완료 |

---

## 진행 상황

| 단계 | 상태 | 완료일 |
|------|------|--------|
| Phase 1: 수동 입력 UI | ✅ 완료 | 2025-12-31 |
| Phase 2: 위도/경도 자동 입력 | ⬜ 대기 | - |
| Phase 3: 수질 데이터 참조 | ⬜ 대기 | - |
| Phase 4: CSV Import 확장 | ⬜ 대기 | - |
| Phase 5: Excel Export 확장 | ⬜ 대기 | - |
