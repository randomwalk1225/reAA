# 데이터 구조 문제 보고서

## 발견된 문제

### 핵심 이슈: `/measurement/new/` → `/measurement/data-input/` 데이터 연결 끊김

**현상**: 사용자가 `/measurement/new/`에서 "한강관측소"를 선택해도, `/measurement/data-input/`에서 저장 시 "경주 대종천"으로 저장됨

---

## 데이터 흐름 분석

### 현재 구조 (문제)

```
[/measurement/new/]
    ↓ formData 수집
    ↓ station_name, station_code, river_name, dm_number 등
    ↓
    ↓ submitForm() 호출
    ↓ window.location.href = '/measurement/data-input/?new=1'  ← 데이터 전달 안됨!
    ↓
[/measurement/data-input/]
    ↓ 빈 상태로 시작 (stationName = '')
    ↓
    ↓ loadTestCSV() 호출 시
    ↓ stationName = '경주 대종천 (테스트)'  ← 하드코딩으로 덮어씀!
    ↓
[저장 시 DB]
    ↓ MeasurementSession.station_name = '경주 대종천 (테스트)'
```

### 문제 위치

#### 1. `templates/measurement/new.html` - Line 569-573
```javascript
submitForm() {
    console.log('Submitting:', this.formData);
    window.location.href = '{% url "measurement:data_input" %}?new=1';  // ← 데이터 전달 없음
}
```
- formData를 수집만 하고 실제로 전달하지 않음
- URL 파라미터, 세션 스토리지, 서버 저장 등 아무것도 없음

#### 2. `templates/measurement/data_input.html` - Line 1171-1201
```javascript
loadTestCSV() {
    // ...
    this.stationName = '경주 대종천 (테스트)';  // ← 하드코딩
    this.measurementDate = new Date().toISOString().split('T')[0];
    // ...
}
```
- 테스트 데이터 로드 시 관측소명을 무조건 덮어씀

#### 3. CSV 파일에는 관측소 정보 없음
`static/sample_measurement_data.csv`:
```csv
거리(m),수심(m),N_0.2D,T_0.2D,N_0.6D,T_0.6D,N_0.8D,T_0.8D
0.00,0.00,,,,,,
1.50,0.32,,,85,60,,
...
```
- CSV에는 측선 데이터만 있고 관측소 정보 없음
- JS에서 하드코딩으로 관측소명 설정

---

## 영향 받는 데이터 필드

### `/measurement/new/`에서 입력하지만 전달되지 않는 필드들:

| 필드 | 설명 | 상태 |
|------|------|------|
| `station_name` | 지점명 | ❌ 미전달 |
| `station_code` | 관측소 코드 | ❌ 미전달 |
| `river_name` | 하천명 | ❌ 미전달 |
| `dm_number` | DM 번호 | ❌ 미전달 |
| `location_desc` | 위치 설명 | ❌ 미전달 |
| `measurement_date` | 측정일 | ❌ 미전달 (data_input에서 오늘 날짜로 재설정) |
| `weather` | 기상 상태 | ❌ 미전달 |
| `wind` | 바람 | ❌ 미전달 |
| `measurer` | 측정자 | ❌ 미전달 |
| `direction` | 측정 방향 | ❌ 미전달 |
| `meter_type` | 유속계 종류 | ❌ 미전달 |
| `meter_id` | 유속계 번호 | ❌ 미전달 |
| `calibration` | 검정계수 | ❌ 미전달 (data_input에서 기본값 사용) |

---

## 해결 방안

### Option A: URL 파라미터로 전달 (간단)
```javascript
// new.html
submitForm() {
    const params = new URLSearchParams({
        station_name: this.formData.station_name,
        station_code: this.formData.station_code,
        river_name: this.formData.river_name,
        measurement_date: this.formData.measurement_date,
        // ...
    });
    window.location.href = `/measurement/data-input/?${params}`;
}

// data_input.html
init() {
    const params = new URLSearchParams(window.location.search);
    this.stationName = params.get('station_name') || '';
    this.measurementDate = params.get('measurement_date') || new Date().toISOString().split('T')[0];
    // ...
}
```

### Option B: 세션 스토리지 사용 (프라이버시)
```javascript
// new.html
submitForm() {
    sessionStorage.setItem('measurementSetup', JSON.stringify(this.formData));
    window.location.href = '/measurement/data-input/?new=1';
}

// data_input.html
init() {
    const setup = JSON.parse(sessionStorage.getItem('measurementSetup') || '{}');
    this.stationName = setup.station_name || '';
    // ...
    sessionStorage.removeItem('measurementSetup');
}
```

### Option C: 서버 세션 저장 (권장)
```python
# views.py - measurement_new
def measurement_new(request):
    if request.method == 'POST':
        # 세션에 설정 저장
        request.session['measurement_setup'] = {
            'station_name': request.POST.get('station_name'),
            'station_code': request.POST.get('station_code'),
            # ...
        }
        return redirect('measurement:data_input')
    return render(request, 'measurement/new.html')

# views.py - data_input
def data_input(request):
    setup = request.session.pop('measurement_setup', {})
    return render(request, 'measurement/data_input.html', {
        'setup': setup,
        'debug': settings.DEBUG,
    })
```

### 테스트 CSV 수정
```javascript
loadTestCSV() {
    // 기존 관측소명이 있으면 유지
    if (!this.stationName) {
        this.stationName = '경주 대종천 (테스트)';
    }
    // ...
}
```

---

## 권장 조치

1. **Option B (세션 스토리지)** 채택 - 빠른 구현, 새로고침 시 데이터 유지
2. `loadTestCSV()`에서 기존 관측소명 유지하도록 수정
3. MeasurementSession 모델에 추가 필드 고려:
   - `station_code` (관측소 코드)
   - `river_name` (하천명)
   - `weather`, `wind`, `measurer` 등

---

## 추가 발견 사항

### MeasurementSession 모델 현재 필드:
```python
class MeasurementSession(models.Model):
    user = ForeignKey(...)  # nullable
    session_key = CharField(...)  # 비로그인용
    station_name = CharField(...)  # 관측소명만 있음
    measurement_date = DateField(...)
    session_number = PositiveSmallIntegerField(...)
    rows_data = JSONField(...)  # 측선 데이터
    calibration_data = JSONField(...)  # 검정계수
    estimated_discharge = FloatField(...)
    # ... 기타 계산 결과
```

**누락된 필드:**
- `station_code` (Station 모델과 연결 가능)
- `river_name`
- `weather`, `wind`, `measurer`, `note`
- `direction` (LEW→REW / REW→LEW)

---

작성일: 2025-12-21
작성자: Claude Code
