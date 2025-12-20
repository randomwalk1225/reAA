# VBA Function Reference Guide

수문 유량 측정 시스템 VBA 코드 레퍼런스
ISO 748 표준 기반 불확실도 분석 시스템

---

## 목차

1. [시스템 개요](#시스템-개요)
2. [파일 구조](#파일-구조)
3. [Module1.bas - 핵심 계산 엔진](#module1bas---핵심-계산-엔진)
4. [Module2.bas - 거리 및 유속계 처리](#module2bas---거리-및-유속계-처리)
5. [기본입력.frm - 메타데이터 입력 폼](#기본입력frm---메타데이터-입력-폼)
6. [사전불확실도.frm - 사전 불확실도 계산](#사전불확실도frm---사전-불확실도-계산)
7. [데이터 흐름](#데이터-흐름)
8. [핵심 공식](#핵심-공식)
9. [Python 구현 참고사항](#python-구현-참고사항)

---

## 시스템 개요

이 시스템은 **하천 유량 측정** 및 **ISO 748 기반 불확실도 분석**을 수행하는 Excel VBA 애플리케이션입니다.

### 주요 기능
- **유량 계산**: Mid-Section Method (중앙단면법)
- **불확실도 분석**: ISO 748 표준 준수
- **유속 측정**: 1점법, 2점법, 3점법 지원
- **다중 유속계**: 최대 4개 유속계 동시 사용

### 측정 방법
| 수심 조건 | 측정법 | 측정 깊이 |
|-----------|--------|-----------|
| 수심 < 0.6m | 1점법 | 0.6D |
| 수심 0.6-1.0m | 2점법 | 0.2D, 0.8D |
| 수심 >= 1.0m | 3점법 | 0.2D, 0.6D, 0.8D |

---

## 파일 구조

```
extracted_vba/
├── Module1.bas.vb      # 핵심 계산 로직 (2518줄)
├── Module2.bas.vb      # 거리/유속계 처리 (386줄)
├── 기본입력.frm.vb     # 기본 입력 폼 (503줄)
├── 사전불확실도.frm.vb # 사전 불확실도 폼 (496줄)
├── ufSelCal.frm.vb     # 계산 선택 다이얼로그 (33줄)
├── 중복정보.frm.vb     # 중복 관측소 선택 (41줄)
├── Sheet1.cls.vb       # 입력시트 이벤트 (69줄)
└── Sheet*.cls.vb       # 기타 시트 (빈 파일들)
```

---

## Module1.bas - 핵심 계산 엔진

### 전역 변수

```vb
Public sh                  ' 현재 시트명
Option Base 1              ' 배열 인덱스 1부터 시작
Public Matrix As Variant   ' 데이터 행렬
Public i                   ' 카운터
```

---

### calFlow(num As Integer)

**목적**: 메인 유량 및 불확실도 계산 함수

**파라미터**:
- `num`: 측정 번호 (1 또는 2)

**기능**:
1. 측선별 유속 계산
2. 단면적 계산 (Mid-Section Method)
3. 유량 계산 (Q = A × V)
4. 불확실도 분석 (ISO 748)

**계산 흐름**:
```
입력저장 시트 → 유속계산 → 단면적계산 → 유량계산 → 불확실도계산 → 결과출력
```

**핵심 로직** (Line 48-600):
```vb
' 측선별 반복
Do
    n = n + 1

    ' 1. 수심별 측정법 결정
    If depth < 0.6 Then
        method = 1  ' 1점법 (0.6D)
    ElseIf depth < 1.0 Then
        method = 2  ' 2점법 (0.2D, 0.8D)
    Else
        method = 3  ' 3점법 (0.2D, 0.6D, 0.8D)
    End If

    ' 2. 평균유속 계산
    avgVel = fmVel(...)

    ' 3. 단면적 계산 (Mid-Section)
    area = (dist(n) - dist(n-1)) * depth(n)

    ' 4. 부분유량
    partQ = area * avgVel

Loop Until 마지막 측선
```

**Python 구현 예시**:
```python
def cal_flow(measurement_num: int, data: pd.DataFrame) -> dict:
    results = []
    total_q = 0

    for i, row in data.iterrows():
        depth = row['depth']

        # 측정법 결정
        if depth < 0.6:
            method = 1
        elif depth < 1.0:
            method = 2
        else:
            method = 3

        # 평균유속
        avg_vel = calculate_mean_velocity(row, method)

        # 단면적 (Mid-Section)
        width = row['distance'] - prev_distance
        area = width * depth

        # 부분유량
        partial_q = area * avg_vel
        total_q += partial_q

    return {'total_discharge': total_q, 'details': results}
```

---

### calDepth(depth, cal)

**목적**: 수심에 따른 측정 깊이 배율 계산

**파라미터**:
- `depth`: 총 수심 (m)
- `cal`: 측정법 선택 (1=0.2D, 2=0.6D, 3=0.8D)

**반환값**: 측정 깊이 (m)

**로직** (Line 630-680):
```vb
Function calDepth(depth, cal) As Variant
    Select Case cal
        Case 1  ' 0.2D
            calDepth = depth * 0.2
        Case 2  ' 0.6D
            calDepth = depth * 0.6
        Case 3  ' 0.8D
            calDepth = depth * 0.8
    End Select
End Function
```

**Python 구현**:
```python
def cal_depth(depth: float, cal: int) -> float:
    ratios = {1: 0.2, 2: 0.6, 3: 0.8}
    return depth * ratios.get(cal, 0.6)
```

---

### fnaveVel(N, T, Meter)

**목적**: 유속계 회전수와 시간으로 실제 유속 계산

**파라미터**:
- `N`: 회전수 (revolutions)
- `T`: 측정 시간 (초)
- `Meter`: 유속계 유형 (문자열)

**반환값**: 유속 (m/s)

**공식**: `V = a + b × (N/T)`
- `a`: 시동유속 (starting velocity)
- `b`: 검정상수 (calibration constant)

**로직** (Line 700-800):
```vb
Function fnaveVel(N, T, Meter) As Variant
    ' para 시트에서 유속계 검정계수 조회
    ' 검정계수: a (시동유속), b (비례상수)

    rps = N / T  ' 초당 회전수

    ' 검정식 적용
    fnaveVel = a + b * rps
End Function
```

**Python 구현**:
```python
def calculate_velocity(n: int, t: float, meter_type: str,
                       calibration: dict) -> float:
    """
    유속 = a + b × (N/T)
    """
    a = calibration[meter_type]['a']  # 시동유속
    b = calibration[meter_type]['b']  # 검정상수
    rps = n / t  # revolutions per second
    return a + b * rps
```

---

### fmVel(method, v1, v2, v3)

**목적**: 측정법에 따른 평균유속 계산

**파라미터**:
- `method`: 측정법 (1, 2, 3)
- `v1`: 0.2D 유속
- `v2`: 0.6D 유속
- `v3`: 0.8D 유속

**반환값**: 평균유속 (m/s)

**공식**:
| 측정법 | 공식 |
|--------|------|
| 1점법 | V = V₀.₆ |
| 2점법 | V = (V₀.₂ + V₀.₈) / 2 |
| 3점법 | V = (V₀.₂ + 2×V₀.₆ + V₀.₈) / 4 |

**로직** (Line 820-870):
```vb
Function fmVel(method, v1, v2, v3) As Variant
    Select Case method
        Case 1  ' 1점법
            fmVel = v2  ' 0.6D만 사용
        Case 2  ' 2점법
            fmVel = (v1 + v3) / 2
        Case 3  ' 3점법
            fmVel = (v1 + 2 * v2 + v3) / 4
    End Select
End Function
```

**Python 구현**:
```python
def mean_velocity(method: int, v_02d: float, v_06d: float, v_08d: float) -> float:
    if method == 1:
        return v_06d
    elif method == 2:
        return (v_02d + v_08d) / 2
    else:  # 3점법
        return (v_02d + 2 * v_06d + v_08d) / 4
```

---

### mainCalFlow()

**목적**: 유량 계산 진입점 (버튼 클릭 이벤트)

**기능** (Line 1-45):
1. 입력 데이터 유효성 검사
2. 측정 횟수 확인 (1회 or 2회)
3. `calFlow()` 호출

```vb
Public Sub mainCalFlow()
    ' 유속계 설정 확인
    Call 유속계입력

    ' 계산 선택 폼 표시
    ufSelCal.Show
End Sub
```

---

### Xe_Error(), Xp_Error(), Xc_Error(), Xm_Error()

**목적**: ISO 748 불확실도 구성요소 계산

#### Xe_Error() - 측점 관련 불확실도
**파라미터**: 측선 수 (m)
**공식**: `Xe = k / sqrt(m)` (k는 유속분포에 따른 상수)

#### Xp_Error() - 깊이측정 불확실도
**파라미터**: 수심 (d), 표면상태
**로직**: para 시트의 조견표에서 조회

#### Xc_Error() - 유속계 검정 불확실도
**파라미터**: 유속계 유형
**로직**: para 시트에서 유속계별 검정 불확실도 조회

#### Xm_Error() - 측정 불확실도
**파라미터**: 측정시간, 측정방법, 유속
**공식**: 복합 불확실도 계산

**로직** (Line 900-1200):
```vb
Function Xe_Error(m) As Variant
    ' 측점 수에 따른 불확실도
    Xe_Error = para_lookup(m)
End Function

Function Xp_Error(depth, surface) As Variant
    ' 수심 및 표면상태별 불확실도
    Xp_Error = para_lookup(depth, surface)
End Function
```

**Python 구현**:
```python
def xe_error(num_verticals: int, lookup_table: pd.DataFrame) -> float:
    """측점 관련 불확실도"""
    return lookup_table.loc[num_verticals, 'xe']

def xp_error(depth: float, surface_condition: str,
             lookup_table: pd.DataFrame) -> float:
    """깊이측정 불확실도"""
    return lookup_table.loc[(depth, surface_condition), 'xp']

def xc_error(meter_type: str, calibration_data: dict) -> float:
    """유속계 검정 불확실도"""
    return calibration_data[meter_type]['uncertainty']

def xm_error(measurement_time: float, method: int, velocity: float) -> float:
    """측정 불확실도"""
    # ISO 748 공식 적용
    pass
```

---

### fnaveVelE(N, T)

**목적**: 가장자리 유속 추정 (Rantz 공식, USGS)

**파라미터**:
- `N`: 회전수
- `T`: 측정 시간

**공식**: Rantz 공식을 사용한 가장자리 유속 추정

**로직** (Line 1300-1400):
```vb
Function fnaveVelE(N, T) As Variant
    ' Rantz 공식 (USGS)
    ' 가장자리 측선의 유속 추정
End Function
```

---

## Module2.bas - 거리 및 유속계 처리

### 전역 변수

```vb
Public sh                  ' 시트명
Option Base 1              ' 배열 인덱스 1부터
Public Matrix As Variant   ' 관측소 정보 행렬
Public i                   ' 카운터
```

---

### 거리계산()

**목적**: 누가거리/구간거리 판별 및 변환

**기능** (Line 11-61):
1. 입력된 거리 데이터가 누가거리인지 구간거리인지 판별
2. 구간거리인 경우 누가거리로 변환
3. `CountIf`로 중복값 확인하여 판별

**로직**:
```vb
Public Sub 거리계산()
    ' 거리 배열 읽기
    Dis = Range(.Cells(9, 4), .Cells(8, 4).Offset(n + 1, 0))

    ' 중복값 확인으로 구간거리 여부 판별
    If Application.CountIf(...) > 1 Then
        i = i + 1  ' 구간거리임
    End If

    ' 구간거리인 경우 누가거리로 변환
    If i > 0 Then
        Dis1(1, 1) = 0
        For n = 2 To count
            Dis1(n, 1) = Dis1(n - 1, 1) + Dis(n, 1)
        Next
    End If
End Sub
```

**Python 구현**:
```python
def convert_distance(distances: List[float]) -> List[float]:
    """
    구간거리를 누가거리로 변환
    중복값이 있으면 구간거리로 판단
    """
    # 중복값 확인
    if len(distances) != len(set(distances)):
        # 구간거리 -> 누가거리 변환
        cumulative = [0]
        for d in distances[1:]:
            cumulative.append(cumulative[-1] + d)
        return cumulative
    return distances
```

---

### 지점입력()

**목적**: 관측소 정보 검색 및 입력

**기능** (Line 63-105):
1. 수위관측소일람표에서 지점명 검색
2. 중복된 지점명이 있으면 선택 다이얼로그 표시
3. 하천명, DM 번호 자동 입력

**로직**:
```vb
Public Sub 지점입력()
    ' 지점명으로 관측소 검색
    Do
        n = n + 1
        If Sheets("수위관측소일람표").Cells(n, 2) = 기본입력.T지점명.Text Then
            i = i + 1
            Matrix(i, 1) = DM_No
            Matrix(i, 2) = 하천명
        End If
    Loop Until Empty

    ' 중복 처리
    If i > 1 Then
        중복정보.Show  ' 선택 다이얼로그
    ElseIf i = 1 Then
        ' 자동 입력
        기본입력.T하천명 = Matrix(i, 2)
        기본입력.TDM = Matrix(i, 1)
    Else
        MsgBox "관측소를 찾을 수 없습니다"
    End If
End Sub
```

---

### 유속계입력()

**목적**: 다중 유속계의 측선 배정 처리

**기능** (Line 106-389):
1. 최대 4개 유속계 지원
2. 측선 범위 파싱 (예: "1-5,7,9-12")
3. 중복 배정 검사
4. 측선별 유속계 색상 표시

**입력 형식**:
- 단일: `"3"`
- 범위: `"1-5"`
- 혼합: `"1-5,7,9-12"`

**로직**:
```vb
Public Sub 유속계입력()
    ' 각 유속계별 측선 설정 파싱
    For P_i = 1 To Count_Text
        tex = Pri(P_i, 1)  ' "1-5,7,9-12" 형식

        ' 쉼표로 분리
        Do
            If InStr(tex, ",") <> 0 Then
                P_j = Left(tex, InStr(tex, ",") - 1)

                ' 범위 처리 (예: "1-5")
                If InStr(P_j, "-") <> 0 Then
                    For P_k = start To end
                        유속계(P_k, 1) = meter_name
                    Next
                Else
                    유속계(P_j, 1) = meter_name
                End If
            End If
        Loop Until InStr(tex, ",") = 0
    Next P_i

    ' 시트에 색상 표시
    For Each cell In 측선범위
        cell.Interior.ColorIndex = meter_color
    Next
End Sub
```

**Python 구현**:
```python
def parse_measurement_lines(spec: str) -> List[int]:
    """
    측선 범위 문자열 파싱
    "1-5,7,9-12" -> [1,2,3,4,5,7,9,10,11,12]
    """
    result = []
    parts = spec.split(',')

    for part in parts:
        if '-' in part:
            start, end = map(int, part.split('-'))
            step = 1 if start < end else -1
            result.extend(range(start, end + step, step))
        else:
            result.append(int(part))

    return result

def assign_velocity_meters(meter_specs: Dict[str, str],
                           total_lines: int) -> Dict[int, str]:
    """
    각 측선에 유속계 배정
    """
    assignments = {}

    for meter_name, spec in meter_specs.items():
        lines = parse_measurement_lines(spec)
        for line in lines:
            if line in assignments:
                raise ValueError(f"측선 {line}에 중복 배정")
            assignments[line] = meter_name

    return assignments
```

---

## 기본입력.frm - 메타데이터 입력 폼

### 폼 컨트롤

| 컨트롤명 | 유형 | 설명 |
|----------|------|------|
| T하천명 | TextBox | 하천명 |
| T지점명 | TextBox | 관측 지점명 |
| TDM | TextBox | DM 번호 |
| T날짜 | TextBox | 측정 날짜 |
| T기상 | ComboBox | 기상 상태 |
| T바람 | ComboBox | 바람 상태 |
| TextBox1-4 | TextBox | 유속계별 측선 설정 |

---

### CB_find_Click()

**목적**: 지점명 검색 버튼

**기능**: 입력된 지점명으로 관측소 검색

```vb
Private Sub CB_find_Click()
    Call 지점입력
End Sub
```

---

### CBsave_Click()

**목적**: 입력 데이터 저장

**기능**:
1. 메타데이터 유효성 검사
2. 거리 데이터 변환 (`거리계산` 호출)
3. 유속계 배정 (`유속계입력` 호출)
4. 데이터를 입력저장 시트에 저장

---

### 유속계 관련 이벤트

```vb
Private Sub CheckBox_2_Click()
    ' 2번 유속계 활성화/비활성화
    If CheckBox_2.Value = True Then
        TextBox2.Visible = True
    Else
        TextBox2.Visible = False
    End If
End Sub
```

---

## 사전불확실도.frm - 사전 불확실도 계산

### 목적

측정 전 예상 불확실도를 계산하여 측정 계획 수립에 활용

### 주요 컨트롤

| 컨트롤명 | 설명 |
|----------|------|
| T측선수 | 예상 측선 수 |
| T평균수심 | 예상 평균 수심 |
| T표면상태 | 수면 상태 선택 |
| T측정시간 | 측정 시간 |
| LB결과 | 결과 표시 라벨 |

### CBcalc_Click()

**목적**: 사전 불확실도 계산 실행

**로직**:
```vb
Private Sub CBcalc_Click()
    ' 불확실도 구성요소 계산
    Xe = Xe_Error(측선수)
    Xp = Xp_Error(수심, 표면상태)
    Xc = Xc_Error(유속계)
    Xm = Xm_Error(측정시간, 방법, 유속)

    ' 합성 불확실도 (RSS)
    U = Sqrt(Xe^2 + Xp^2 + Xc^2 + Xm^2)

    ' 확장 불확실도 (95% 신뢰수준, k=2)
    U_expanded = 2 * U

    LB결과.Caption = Format(U_expanded, "0.00") & "%"
End Sub
```

---

## 데이터 흐름

```
┌─────────────┐
│  기본입력   │ ← 사용자 입력 (메타데이터, 유속계 설정)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  입력시트   │ ← 측정 데이터 입력 (거리, 수심, 회전수, 시간)
└──────┬──────┘
       │ 저장
       ▼
┌─────────────┐
│ 입력저장1/2 │ ← 측정 세션별 원시 데이터 보관
└──────┬──────┘
       │ calFlow()
       ▼
┌─────────────┐
│  계산1/2    │ ← 유속, 단면적, 부분유량 계산
└──────┬──────┘
       │ 불확실도 계산
       ▼
┌─────────────┐
│ 불확실도1/2 │ ← ISO 748 불확실도 분석
└──────┬──────┘
       │ 집계
       ▼
┌─────────────┐
│   평균      │ ← 2회 측정 평균값
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   종합      │ ← 최종 보고서 출력
└─────────────┘
```

---

## 핵심 공식

### 1. 유속 계산

```
V = a + b × (N/T)

여기서:
  V = 유속 (m/s)
  a = 시동유속 (starting velocity, m/s)
  b = 검정상수 (calibration constant)
  N = 회전수 (revolutions)
  T = 측정시간 (seconds)
```

### 2. 평균유속 (측정법별)

```
1점법: V̄ = V₀.₆
2점법: V̄ = (V₀.₂ + V₀.₈) / 2
3점법: V̄ = (V₀.₂ + 2×V₀.₆ + V₀.₈) / 4
```

### 3. 유량 계산 (Mid-Section Method)

```
Q = Σ qᵢ

qᵢ = Aᵢ × V̄ᵢ

Aᵢ = [(bᵢ - bᵢ₋₁)/2 + (bᵢ₊₁ - bᵢ)/2] × dᵢ
   = (bᵢ₊₁ - bᵢ₋₁)/2 × dᵢ

여기서:
  Q = 총 유량 (m³/s)
  qᵢ = i번째 측선의 부분유량
  Aᵢ = i번째 측선의 단면적
  V̄ᵢ = i번째 측선의 평균유속
  bᵢ = i번째 측선의 거리
  dᵢ = i번째 측선의 수심
```

### 4. 불확실도 계산 (ISO 748)

```
u(Q) = √[u²(Xe) + u²(Xp) + u²(Xc) + u²(Xm)]

여기서:
  u(Q) = 유량의 합성표준불확실도
  u(Xe) = 측점 관련 불확실도
  u(Xp) = 깊이측정 불확실도
  u(Xc) = 유속계 검정 불확실도
  u(Xm) = 측정 불확실도

확장불확실도 (95% 신뢰수준):
U = k × u(Q), k = 2
```

---

## Python 구현 참고사항

### 1. 데이터 모델

```python
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

class MeasurementMethod(Enum):
    ONE_POINT = 1   # 0.6D
    TWO_POINT = 2   # 0.2D, 0.8D
    THREE_POINT = 3 # 0.2D, 0.6D, 0.8D

@dataclass
class VelocityMeter:
    name: str
    type: str
    a: float  # 시동유속
    b: float  # 검정상수
    uncertainty: float  # 검정 불확실도

@dataclass
class MeasurementPoint:
    line_number: int
    distance: float      # 누가거리 (m)
    depth: float         # 수심 (m)
    revolutions: List[int]  # 회전수 [0.2D, 0.6D, 0.8D]
    times: List[float]      # 측정시간 [0.2D, 0.6D, 0.8D]
    meter: VelocityMeter

@dataclass
class DischargeResult:
    total_discharge: float  # 총 유량 (m³/s)
    total_area: float       # 총 단면적 (m²)
    mean_velocity: float    # 평균유속 (m/s)
    uncertainty: float      # 확장불확실도 (%)
    details: List[dict]     # 측선별 상세 결과
```

### 2. 주요 모듈 구조

```python
# core/
#   velocity.py      - 유속 계산
#   discharge.py     - 유량 계산 (Mid-Section)
#   uncertainty.py   - ISO 748 불확실도
#   calibration.py   - 유속계 검정 데이터
#
# services/
#   calculation.py   - 계산 서비스 (calFlow 대응)
#   validation.py    - 입력 검증
#
# models/
#   measurement.py   - 측정 데이터 모델
#   station.py       - 관측소 정보
```

### 3. Django 통합

```python
# views.py
from django.views.generic import FormView
from .forms import MeasurementForm
from .services import DischargeCalculationService

class CalculateDischargeView(FormView):
    template_name = 'measurement/input.html'
    form_class = MeasurementForm

    def form_valid(self, form):
        service = DischargeCalculationService()
        result = service.calculate(form.cleaned_data)
        return self.render_to_response({
            'result': result,
            'form': form,
        })
```

---

## 부록: VBA-Python 대응표

| VBA 함수 | Python 함수 | 파일 |
|----------|-------------|------|
| `calFlow()` | `DischargeCalculationService.calculate()` | services/calculation.py |
| `calDepth()` | `cal_depth()` | core/velocity.py |
| `fnaveVel()` | `calculate_velocity()` | core/velocity.py |
| `fmVel()` | `mean_velocity()` | core/velocity.py |
| `Xe_Error()` | `xe_error()` | core/uncertainty.py |
| `Xp_Error()` | `xp_error()` | core/uncertainty.py |
| `Xc_Error()` | `xc_error()` | core/uncertainty.py |
| `Xm_Error()` | `xm_error()` | core/uncertainty.py |
| `거리계산()` | `convert_distance()` | core/distance.py |
| `유속계입력()` | `assign_velocity_meters()` | core/meter.py |

---

*문서 생성일: 2025-12-19*
*VBA 소스: 경주대종천하류보20250501.xls*
