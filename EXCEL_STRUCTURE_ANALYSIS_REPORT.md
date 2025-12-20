# Excel 파일 구조 분석 보고서

## 1. 개요

### 1.1 분석 대상 파일
| 파일명 | 형식 | 용도 |
|--------|------|------|
| 경주대종천하류보20250501_unlocked.xlsm | Excel 매크로 파일 | **주 분석 대상** (보호 해제 버전) |
| 경주대종천하류보20250501.xls | Excel 97-2003 | 원본 파일 |
| 경주_대종천_하류보.xls | Excel 97-2003 | 템플릿 또는 이전 버전 |

### 1.2 파일 목적
**수문(水文) 유량 측정 데이터 처리 및 불확실도 분석 시스템**
- 하천 유량 측정 데이터 입력
- 유속, 단면적, 유량 계산
- 측정 불확실도 분석 (ISO/KS 표준 준수)
- 결과 종합 리포트 생성

---

## 2. 시트 구조 분석

### 2.1 시트 목록 (총 17개)
```
xlsm 파일 시트 구조:
├── 입력시트      ← [INPUT] 원시 측정 데이터 입력
├── 종합          ← [OUTPUT] 측정 메타데이터 및 결과 종합
├── 평균          ← [OUTPUT] 측정 결과 평균 및 불확실도 요약
├── 계산1         ← [CALC] 1차 측정 계산
├── 계산2         ← [CALC] 2차 측정 계산
├── 비율          ← [CALC] 측정간 비율 분석
├── 불확실도1     ← [CALC] 1차 측정 불확실도 계산
├── 불확실도2     ← [CALC] 2차 측정 불확실도 계산
├── 공백          ← [UTIL] 빈 시트
├── 도움말        ← [REF] 측정 가이드라인
├── 도움말_개선사항 ← [REF] 개선사항 기록
├── 이름정의      ← [REF] 명명된 범위 정의
├── para          ← [PARAM] 유속계 보정 파라미터
├── Rantz         ← [PARAM] Rantz 공식 파라미터
├── 입력저장1     ← [DATA] 1차 측정 저장 데이터
├── 입력저장2     ← [DATA] 2차 측정 저장 데이터
└── 수위관측소일람표 ← [REF] 관측소 정보
```

---

## 3. 상세 시트 분석

### 3.1 입력시트 (INPUT - 핵심)
**범위**: A2:U21 (21행 x 21열)

#### 입력 필드 구조
| 열 | 필드명 | 단위 | 설명 |
|----|--------|------|------|
| C | 측선 | - | 측정 지점 번호 (1~10) |
| D | 거리 | m | 기준점으로부터 거리 |
| E | 수심 | m | 해당 측선의 수심 |
| F | 시각 | hh:mm | 측정 시각 |
| G | 목자판 | m | 수위표 읽음값 |
| H-K | 0.2D | - | 수심 20% 지점 측정값 (깊이, 각보정, N[V], T) |
| L-O | 0.6D | - | 수심 60% 지점 측정값 |
| P-S | 0.8D | - | 수심 80% 지점 측정값 |

#### 셀 병합 영역
- H6:K6 (0.2D 헤더)
- L6:O6 (0.6D 헤더)
- P6:S6 (0.8D 헤더)
- C6:C7 (측선 헤더)

---

### 3.2 계산1/계산2 시트 (CALCULATION)
**범위**: A3:AC114 (114행 x 29열)

#### 주요 계산 열
| 열 | 필드명 | 단위 | 계산 내용 |
|----|--------|------|----------|
| A | 측선방향 | - | LEW/REW |
| B | 번호 | - | 측선 번호 |
| C | 거리 | m | 측정 거리 |
| D | 측선폭 | m | 인접 측선간 폭 |
| E | 수심 | m | 측정 수심 |
| F-Q | 유속 회전수/보정 | - | 0.2D, 0.6D, 0.8D별 회전수, 보정값, N/T |
| R | Va0.2 | m/s | 0.2D 유속 |
| S | Va0.6 | m/s | 0.6D 유속 |
| T | Va0.8 | m/s | 0.8D 유속 |
| U-W | VΦ | m/s | 각도 보정 유속 |
| X | Vm | m/s | 평균 유속 |
| Y | 구간면적 | m² | 단면적 계산 |
| Z | 유량 | cms | 구간 유량 (Q = A × V) |
| AA | 윤변 | m | 습윤 둘레 |
| AC | 평균수위 | m | 평균 수위 |

#### 주요 수식 패턴
```
# 평균유속 계산 (2점법: 0.2D + 0.8D)
Vm = (V0.2 + V0.8) / 2

# 평균유속 계산 (3점법: 0.2D + 0.6D + 0.8D)
Vm = (V0.2 + 2*V0.6 + V0.8) / 4

# 구간면적
A = 측선폭 × 수심

# 유량
Q = A × Vm
```

---

### 3.3 비율 시트 (RATIO ANALYSIS)
**범위**: A3:AA114 (114행 x 27열)

#### 비교 분석 필드
| 열 | 필드명 | 설명 |
|----|--------|------|
| C-D | 수심차/비율 | 측정1 vs 측정2 수심 비교 |
| E-F | 유속차/비율 | 측정1 vs 측정2 유속 비교 |
| G-H | 면적차/비율 | 단면적 비교 |
| I-J | 유량차/비율 | 유량 비교 |
| K | 유량비 측정1 | 1차 측정 구간별 유량 비율(%) |
| L | 유량비 측정2 | 2차 측정 구간별 유량 비율(%) |
| M | 평균 | 평균 유량비 |

#### 핵심 수식
```excel
# 수심차 계산
=ABS(계산2!E9-계산1!E9)

# 비율 계산
=IF(계산1!E9=0,0,C9/계산1!E9*100)
```

---

### 3.4 불확실도1/불확실도2 시트 (UNCERTAINTY)
**범위**: A3:AF120 (120행 x 32열)

#### 불확실도 구성요소
| 기호 | 설명 | 유형 |
|------|------|------|
| X'b | 하폭측정 불확실도 | 무작위 |
| X'd | 수심측정 불확실도 | 무작위 |
| X'e | 측정시간 불확실도 | 무작위 |
| X'p | 측점수 불확실도 | 무작위 |
| X'c | 유속계보정 불확실도 | 무작위 |
| X'm | 무작위 불확실도 합 | 무작위 |
| X''b | 하폭측정 계통오차 | 계통 |
| X''d | 수심측정 계통오차 | 계통 |
| X''c | 유속계 계통오차 | 계통 |
| X''Q | 계통 불확실도 합 | 계통 |
| XQ | 전체 불확실도 | 합성 |

#### 불확실도 계산 공식
```
# 무작위 불확실도
X'Q = √(X'b² + X'd² + X'e² + X'p² + X'c²)

# 계통 불확실도
X''Q = √(X''b² + X''d² + X''c²)

# 전체 불확실도
XQ = √(X'Q² + X''Q²)
```

---

### 3.5 평균 시트 (SUMMARY)
**범위**: A2:AG41 (41행 x 33열)

#### 출력 필드 (측정 결과)
| 행 | 필드명 | 단위 | 설명 |
|----|--------|------|------|
| D9 | 수위 H | m | =계산1!$AC$114 |
| E9 | 수면폭 W | m | =계산1!$D$114 |
| F9 | 단면적 A | m² | =계산1!$Y$114 |
| G9 | 평균유속 V | m/s | =계산1!$Z$114/계산1!$Y$114 |
| H9 | 유량 Q | m³/s | =계산1!$Z$114 |
| J9 | 유속측선수 | 개 | =MAX(계산1!$B$9:$B$108) |

#### 불확실도 출력
| 셀 | 내용 | 참조 |
|----|------|------|
| D15 | X'm(%) 무작위요소 | =불확실도1!$N$114 |
| E15 | X''b(%) 계통요소 | =불확실도1!$P$114 |
| J15 | XQ(%) 전체 | =불확실도1!$T$114 |

---

### 3.6 종합 시트 (COMPREHENSIVE)
**범위**: A1:DM155 (155행 x 117열)

#### 메타데이터 입력
| 위치 | 필드 | 예시 |
|------|------|------|
| B4 | 측정일 | 2025-05-01 |
| F4 | 날씨 | 맑음 |
| I4 | 바람정도 | 강 |
| N2 | 하천명 | 대종천 |
| N3 | 지점명 | 대종천 |
| N4 | 측정위치 | 하류보 |

#### 계산 결과 출력 (BF~BI열)
| 행 | 항목 | 수식 |
|----|------|------|
| BH3 | 수면폭 | =평균!E11 |
| BH4 | 단면적 | =평균!F11 |
| BH5 | 윤변 | =AY140 |
| BH6 | 동수반경 | =AU140/AY140 |
| BH7 | 수위 | =평균!D11 |
| BH8 | 평균유속 | =평균!G11 |
| BH9 | 평균유량 | =평균!H11 |
| BH11 | 불확실도 | =평균!J15 |

---

## 4. 데이터 흐름 다이어그램

```
┌─────────────────┐
│    입력시트      │ ◄── 사용자 입력 (측정 원시 데이터)
│  (Raw Data)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│    입력저장1     │     │    입력저장2     │
│ (Data Storage)  │     │ (Data Storage)  │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌─────────────────┐
│     계산1       │     │     계산2       │
│  (Calculation)  │     │  (Calculation)  │
│  - 유속 계산    │     │  - 유속 계산    │
│  - 면적 계산    │     │  - 면적 계산    │
│  - 유량 계산    │     │  - 유량 계산    │
└────────┬────────┘     └────────┬────────┘
         │                       │
         ├───────────┬───────────┤
         │           │           │
         ▼           ▼           ▼
┌─────────────┐ ┌─────────┐ ┌─────────────┐
│  불확실도1   │ │  비율   │ │  불확실도2   │
│(Uncertainty)│ │ (Ratio) │ │(Uncertainty)│
└──────┬──────┘ └────┬────┘ └──────┬──────┘
       │             │             │
       └─────────────┼─────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │      평균       │
            │   (Summary)     │
            │ - 측정 평균     │
            │ - 불확실도 평균 │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │      종합       │ ──► 최종 보고서 출력
            │(Comprehensive)  │
            └─────────────────┘
```

---

## 5. Input/Output 필드 정리

### 5.1 입력 필드 (INPUT FIELDS)

#### 필수 입력 (입력시트)
| 필드 | 셀 범위 | 데이터 타입 | 필수 |
|------|---------|-------------|------|
| 측선번호 | C9:C18 | Integer | Y |
| 거리 | D9:D18 | Float (m) | Y |
| 수심 | E9:E18 | Float (m) | Y |
| 시각 | F9, F18 | Time (hh:mm) | Y |
| 목자판 읽음값 | G9, G18 | Float (m) | Y |
| 0.6D 깊이 | L9:L18 | Float (m) | Y |
| 0.6D 각보정 | M9:M18 | Float | N |
| 0.6D N[V] | N9:N18 | Float | Y |

#### 메타데이터 입력 (종합시트)
| 필드 | 셀 | 데이터 타입 |
|------|-----|-------------|
| 측정일 | B4 | Date |
| 날씨 | F4 | String |
| 바람정도 | I4 | String |
| 하천명 | N2 | String |
| 지점명 | N3 | String |
| 측정위치 | N4 | String |

### 5.2 출력 필드 (OUTPUT FIELDS)

#### 주요 계산 결과 (평균시트)
| 필드 | 셀 | 단위 | 수식 소스 |
|------|-----|------|----------|
| 수위 H | D11 | m | AVERAGE(D9:D10) |
| 수면폭 W | E11 | m | AVERAGE(E9:E10) |
| 단면적 A | F11 | m² | AVERAGE(F9:F10) |
| 평균유속 V | G11 | m/s | AVERAGE(G9:G10) |
| 유량 Q | H11 | m³/s | AVERAGE(H9:H10) |
| 측정장비 | I11 | - | 종합!K21 |
| 유속측선수 | J11 | 개 | AVERAGE(J9:J10) |
| 평균수심 | N11 | m | F11/E11 |

#### 불확실도 결과
| 필드 | 셀 | 단위 | 설명 |
|------|-----|------|------|
| X'm | D17 | % | 무작위 불확실도 평균 |
| X''b | E17 | % | 계통 불확실도(하폭) |
| X''d | F17 | % | 계통 불확실도(수심) |
| X''c | G17 | % | 계통 불확실도(유속계) |
| X'Q | H17 | % | 무작위 불확실도 합성 |
| X''Q | I17 | % | 계통 불확실도 합성 |
| XQ | J17 | % | **전체 불확실도** |

---

## 6. 수식 분석

### 6.1 유속 계산 (Velocity Calculation)
```python
# 유속계 보정 공식 (para 시트 참조 필요)
# V = a + b*N  (N: 회전수/시간)
# 또는 Rantz 공식 사용

# N/T 계산
N_per_T = N / T  # N: 회전수, T: 측정시간(초)

# 유속 (m/s)
Va = f(N_per_T, calibration_params)
```

### 6.2 유량 계산 (Discharge Calculation)
```python
# 구간 면적 (Mid-Section Method)
A_i = b_i * d_i  # b: 측선폭, d: 수심

# 구간 유량
Q_i = A_i * V_m_i  # V_m: 평균유속

# 총 유량
Q_total = sum(Q_i for all sections)
```

### 6.3 불확실도 계산 (Uncertainty Calculation)
```python
import math

# ISO 748 기반 불확실도 계산
# 무작위 불확실도 구성요소
X_prime_components = {
    'Xb': width_uncertainty,      # 하폭측정
    'Xd': depth_uncertainty,      # 수심측정
    'Xe': time_uncertainty,       # 측정시간
    'Xp': points_uncertainty,     # 측점수
    'Xc': meter_uncertainty       # 유속계보정
}

# 무작위 불확실도 합성
X_prime_Q = math.sqrt(sum(x**2 for x in X_prime_components.values()))

# 계통 불확실도 구성요소
X_double_prime = {
    'Xb': systematic_width,
    'Xd': systematic_depth,
    'Xc': systematic_meter
}

# 계통 불확실도 합성
X_double_prime_Q = math.sqrt(sum(x**2 for x in X_double_prime.values()))

# 전체 불확실도
XQ = math.sqrt(X_prime_Q**2 + X_double_prime_Q**2)
```

---

## 7. Python 재현을 위한 핵심 사항

### 7.1 필요한 Python 라이브러리
```python
# 필수
import pandas as pd
import numpy as np
import openpyxl
import xlrd

# 선택 (시각화/보고서)
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table
```

### 7.2 데이터 구조 설계
```python
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, time

@dataclass
class MeasurementPoint:
    """측선별 측정 데이터"""
    section_no: int           # 측선번호
    distance: float           # 거리 (m)
    depth: float              # 수심 (m)
    time: Optional[time]      # 측정시각
    gauge_reading: float      # 목자판 읽음값 (m)

    # 0.2D 측정값
    depth_02: Optional[float] = None
    angle_02: Optional[float] = None
    n_02: Optional[float] = None
    t_02: Optional[float] = None

    # 0.6D 측정값
    depth_06: Optional[float] = None
    angle_06: Optional[float] = None
    n_06: Optional[float] = None
    t_06: Optional[float] = None

    # 0.8D 측정값
    depth_08: Optional[float] = None
    angle_08: Optional[float] = None
    n_08: Optional[float] = None
    t_08: Optional[float] = None

@dataclass
class MeasurementSession:
    """측정 세션 (1회 측정)"""
    date: datetime
    river_name: str
    location_name: str
    weather: str
    wind: str
    points: List[MeasurementPoint]

@dataclass
class CalculationResult:
    """계산 결과"""
    water_level: float        # 수위 H (m)
    surface_width: float      # 수면폭 W (m)
    cross_section_area: float # 단면적 A (m²)
    mean_velocity: float      # 평균유속 V (m/s)
    discharge: float          # 유량 Q (m³/s)
    wetted_perimeter: float   # 윤변 (m)
    hydraulic_radius: float   # 동수반경 (m)

@dataclass
class UncertaintyResult:
    """불확실도 결과"""
    X_prime_m: float    # 무작위 불확실도 (%)
    X_prime_Q: float    # 무작위 합성 (%)
    X_double_Q: float   # 계통 합성 (%)
    XQ_total: float     # 전체 불확실도 (%)
```

### 7.3 구현 우선순위
1. **데이터 입력 파싱** - 입력시트 → Python 객체
2. **유속 계산 모듈** - para/Rantz 시트 기반 보정
3. **유량 계산 모듈** - Mid-Section Method 구현
4. **불확실도 계산 모듈** - ISO 748 기준
5. **결과 출력 모듈** - 평균/종합 시트 형식

---

## 8. 다음 단계 권장사항

### 8.1 추가 분석 필요 항목
1. **para 시트 상세 분석** - 유속계 보정 계수 추출
2. **Rantz 시트 분석** - Rantz 공식 파라미터 추출
3. **이름정의 시트 분석** - 명명된 범위 및 상수 확인
4. **VBA 매크로 분석** - xlsm 파일 내 자동화 로직 확인

### 8.2 Python 구현 단계
1. 데이터 모델 클래스 정의
2. Excel 파서 구현 (openpyxl/xlrd)
3. 계산 엔진 구현
4. 불확실도 분석 모듈 구현
5. 결과 출력/보고서 생성
6. 테스트 및 검증 (Excel 결과와 비교)

---

## 부록: 추출된 데이터 파일 위치
```
extracted_data/
├── xlsm_unlocked/
│   ├── 입력시트.json
│   ├── 평균.json
│   ├── 종합.json
│   ├── 계산1.json
│   ├── 계산2.json
│   ├── 비율.json
│   ├── 불확실도1.json
│   ├── 불확실도2.json
│   ├── 공백.json
│   └── 도움말.json
└── extraction_summary.json (미완료)
```

---

*보고서 작성일: 2025-12-19*
*분석 도구: Python 3.13.7, openpyxl 3.1.5, xlrd 2.0.2*
