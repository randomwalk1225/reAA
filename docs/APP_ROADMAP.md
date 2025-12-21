# HydroLink 앱 로드맵

## Parquet 도입 계획

### Parquet란?
Apache Parquet는 컬럼 기반의 효율적인 데이터 저장 포맷으로:
- **압축 효율**: CSV 대비 ~75% 용량 절감
- **빠른 읽기**: 필요한 컬럼만 로드 가능
- **스키마 보존**: 데이터 타입 자동 유지
- **대용량 처리**: 수백만 행도 빠르게 처리

### 도입 권장 상황

#### 1. 시계열 데이터 저장 (가장 적합)
```
/measurement/timeseries/
- 수위 시계열 (WaterLevelTimeSeries)
- 유량 시계열 (DischargeTimeSeries)
```
**이유**: 수십만~수백만 행의 시계열 데이터 → Parquet로 저장 시 빠른 조회, 압축 저장

#### 2. 대용량 측정 데이터 내보내기/가져오기
```
/measurement/export/
- Excel/CSV 대신 Parquet 옵션 추가
```
**이유**: 여러 측정 세션을 한 번에 내보낼 때 효율적

#### 3. 기저유출 분석 결과 저장
```
/measurement/baseflow/
- BaseflowDaily 일별 결과
```
**이유**: 일별 데이터가 365일 × 여러 분석 → 누적 시 대용량

#### 4. GEE 증발산량 데이터 캐싱
```
/hydro/evapotranspiration/
- 위성 기반 ET 데이터 (pixel-level)
```
**이유**: GEE 호출 비용 절감, 로컬 캐싱

---

### 구현 계획

#### Phase 1: 라이브러리 설치
```bash
uv add pyarrow pandas
```

#### Phase 2: 시계열 내보내기 기능
```python
# measurement/utils/parquet_export.py
import pandas as pd

def export_timeseries_parquet(station_id, start_date, end_date):
    """시계열 데이터를 Parquet로 내보내기"""
    from measurement.models import WaterLevelTimeSeries

    qs = WaterLevelTimeSeries.objects.filter(
        station_id=station_id,
        timestamp__range=(start_date, end_date)
    ).values('timestamp', 'stage', 'quality_flag')

    df = pd.DataFrame(list(qs))
    return df.to_parquet(compression='snappy')
```

#### Phase 3: 가져오기 기능
```python
def import_timeseries_parquet(file_path, station_id):
    """Parquet 파일에서 시계열 데이터 가져오기"""
    df = pd.read_parquet(file_path)

    for _, row in df.iterrows():
        WaterLevelTimeSeries.objects.update_or_create(
            station_id=station_id,
            timestamp=row['timestamp'],
            defaults={'stage': row['stage']}
        )
```

#### Phase 4: 분석 결과 캐싱
```python
# 기저유출 분석 결과를 Parquet로 캐싱
CACHE_DIR = Path('cache/baseflow/')

def cache_baseflow_result(analysis_id, df):
    path = CACHE_DIR / f'{analysis_id}.parquet'
    df.to_parquet(path, compression='snappy')

def load_cached_baseflow(analysis_id):
    path = CACHE_DIR / f'{analysis_id}.parquet'
    if path.exists():
        return pd.read_parquet(path)
    return None
```

---

### 적용 우선순위

| 순위 | 기능 | 효과 | 난이도 |
|------|------|------|--------|
| 1 | 시계열 데이터 내보내기 | 높음 | 낮음 |
| 2 | 기저유출 분석 캐싱 | 중간 | 낮음 |
| 3 | 측정 세션 일괄 내보내기 | 중간 | 중간 |
| 4 | GEE ET 데이터 캐싱 | 높음 | 중간 |

---

### CSV vs Parquet 비교 (예상)

| 항목 | CSV | Parquet |
|------|-----|---------|
| 10만 행 파일 크기 | ~15MB | ~3MB |
| 읽기 속도 | 2초 | 0.3초 |
| 특정 컬럼 조회 | 전체 로드 필요 | 해당 컬럼만 로드 |
| 스키마 정보 | 없음 (추론 필요) | 포함됨 |

---

### 메모

- **권장 시점**: 시계열 데이터가 10만 행 이상 쌓일 때
- **pyarrow**: Parquet 읽기/쓰기 라이브러리 (pandas 연동)
- **압축 옵션**: snappy(빠름), gzip(더 작음), zstd(균형)

---

작성일: 2025-12-21
