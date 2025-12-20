# Python 재현 구현 작업 계획서

## 1. 프로젝트 개요

### 1.1 목표
Excel 기반 수문 유량 측정 분석 시스템을 Python으로 완전히 재현

### 1.2 핵심 요구사항
- 동일한 입력 데이터에 대해 Excel과 동일한 결과 출력
- ISO 748 표준 준수 불확실도 계산
- 재사용 가능한 모듈형 설계
- 확장 가능한 아키텍처

---

## 2. 아키텍처 설계

### 2.1 모듈 구조
```
reAA/
├── src/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── measurement.py      # 측정 데이터 모델
│   │   ├── calculation.py      # 계산 결과 모델
│   │   └── uncertainty.py      # 불확실도 모델
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── excel_parser.py     # Excel 파일 파싱
│   │   └── input_validator.py  # 입력 검증
│   ├── calculators/
│   │   ├── __init__.py
│   │   ├── velocity.py         # 유속 계산
│   │   ├── discharge.py        # 유량 계산
│   │   ├── cross_section.py    # 단면적 계산
│   │   └── uncertainty.py      # 불확실도 계산
│   ├── calibration/
│   │   ├── __init__.py
│   │   ├── velocity_meter.py   # 유속계 보정
│   │   └── rantz.py            # Rantz 공식
│   ├── reporters/
│   │   ├── __init__.py
│   │   ├── excel_writer.py     # Excel 출력
│   │   ├── pdf_reporter.py     # PDF 보고서
│   │   └── summary.py          # 결과 요약
│   └── utils/
│       ├── __init__.py
│       ├── constants.py        # 상수 정의
│       └── helpers.py          # 유틸리티 함수
├── tests/
│   ├── __init__.py
│   ├── test_parsers.py
│   ├── test_calculators.py
│   └── test_integration.py
├── data/
│   ├── sample_input.xlsx       # 테스트용 샘플
│   └── calibration_params.json # 보정 파라미터
├── config/
│   └── settings.yaml           # 설정 파일
├── requirements.txt
├── setup.py
└── README.md
```

### 2.2 의존성 패키지
```
# requirements.txt
openpyxl>=3.1.0
xlrd>=2.0.0
pandas>=2.0.0
numpy>=1.24.0
pyyaml>=6.0
pydantic>=2.0.0
reportlab>=4.0.0    # PDF 생성
pytest>=7.0.0       # 테스트
```

---

## 3. 구현 작업 목록

### Phase 1: 기반 구축
| 작업 | 설명 | 우선순위 |
|------|------|----------|
| P1-1 | 프로젝트 구조 생성 | 높음 |
| P1-2 | 데이터 모델 클래스 정의 (Pydantic) | 높음 |
| P1-3 | 상수 및 설정 파일 구성 | 높음 |
| P1-4 | 유틸리티 함수 구현 | 중간 |

### Phase 2: 데이터 파싱
| 작업 | 설명 | 우선순위 |
|------|------|----------|
| P2-1 | 입력시트 파서 구현 | 높음 |
| P2-2 | 종합시트 메타데이터 파서 | 높음 |
| P2-3 | para/Rantz 시트 파라미터 추출 | 높음 |
| P2-4 | 입력 데이터 검증 로직 | 중간 |

### Phase 3: 계산 엔진
| 작업 | 설명 | 우선순위 |
|------|------|----------|
| P3-1 | 유속계 보정 공식 구현 | 높음 |
| P3-2 | 평균유속 계산 (1점/2점/3점법) | 높음 |
| P3-3 | 단면적 계산 (Mid-Section Method) | 높음 |
| P3-4 | 유량 계산 | 높음 |
| P3-5 | 윤변/동수반경 계산 | 중간 |

### Phase 4: 불확실도 분석
| 작업 | 설명 | 우선순위 |
|------|------|----------|
| P4-1 | 무작위 불확실도 구성요소 계산 | 높음 |
| P4-2 | 계통 불확실도 구성요소 계산 | 높음 |
| P4-3 | 불확실도 합성 (RSS) | 높음 |
| P4-4 | 요소별 기여도 분석 | 중간 |

### Phase 5: 출력 및 보고서
| 작업 | 설명 | 우선순위 |
|------|------|----------|
| P5-1 | 결과 데이터프레임 생성 | 높음 |
| P5-2 | Excel 출력 (평균/종합 시트 형식) | 높음 |
| P5-3 | PDF 보고서 생성 | 낮음 |
| P5-4 | CLI 인터페이스 | 낮음 |

### Phase 6: 테스트 및 검증
| 작업 | 설명 | 우선순위 |
|------|------|----------|
| P6-1 | 단위 테스트 작성 | 높음 |
| P6-2 | Excel 결과와 비교 검증 | 높음 |
| P6-3 | 통합 테스트 | 중간 |
| P6-4 | 엣지 케이스 테스트 | 중간 |

---

## 4. 상세 구현 명세

### 4.1 데이터 모델 (models/measurement.py)
```python
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time
from enum import Enum

class VelocityMethod(Enum):
    ONE_POINT = "1점법"    # 0.6D only
    TWO_POINT = "2점법"    # 0.2D + 0.8D
    THREE_POINT = "3점법"  # 0.2D + 0.6D + 0.8D

class VelocityPoint(BaseModel):
    """단일 깊이에서의 유속 측정값"""
    depth_ratio: float = Field(..., description="수심 비율 (0.2, 0.6, 0.8)")
    actual_depth: float = Field(..., description="실제 측정 깊이 (m)")
    angle_correction: float = Field(default=1.0, description="각도 보정 계수")
    revolution_count: float = Field(..., description="회전수 N")
    measurement_time: float = Field(..., description="측정 시간 T (초)")

    @property
    def n_per_t(self) -> float:
        """회전수/시간 계산"""
        return self.revolution_count / self.measurement_time if self.measurement_time > 0 else 0

class MeasurementPoint(BaseModel):
    """측선별 측정 데이터"""
    section_no: int = Field(..., ge=1, description="측선 번호")
    distance: float = Field(..., ge=0, description="기준점으로부터 거리 (m)")
    depth: float = Field(..., ge=0, description="수심 (m)")
    measurement_time: Optional[time] = Field(None, description="측정 시각")
    gauge_reading: Optional[float] = Field(None, description="목자판 읽음값 (m)")

    velocity_02d: Optional[VelocityPoint] = None
    velocity_06d: Optional[VelocityPoint] = None
    velocity_08d: Optional[VelocityPoint] = None

    @property
    def velocity_method(self) -> VelocityMethod:
        """사용된 유속 측정 방법 결정"""
        has_02 = self.velocity_02d is not None
        has_06 = self.velocity_06d is not None
        has_08 = self.velocity_08d is not None

        if has_02 and has_06 and has_08:
            return VelocityMethod.THREE_POINT
        elif has_02 and has_08:
            return VelocityMethod.TWO_POINT
        else:
            return VelocityMethod.ONE_POINT

class MeasurementSession(BaseModel):
    """측정 세션"""
    date: datetime
    river_name: str
    location_name: str
    measurement_position: str
    weather: Optional[str] = None
    wind_condition: Optional[str] = None
    points: List[MeasurementPoint] = Field(default_factory=list)

    @property
    def section_count(self) -> int:
        """유효 측선 수"""
        return len([p for p in self.points if p.depth > 0])
```

### 4.2 유속 계산기 (calculators/velocity.py)
```python
from typing import Tuple
from ..models.measurement import MeasurementPoint, VelocityMethod

class VelocityCalculator:
    """유속 계산기"""

    def __init__(self, calibration_a: float, calibration_b: float):
        """
        Args:
            calibration_a: 유속계 보정 계수 a
            calibration_b: 유속계 보정 계수 b
        """
        self.a = calibration_a
        self.b = calibration_b

    def n_to_velocity(self, n_per_t: float) -> float:
        """회전수/시간을 유속으로 변환

        V = a + b * (N/T)
        """
        return self.a + self.b * n_per_t

    def calculate_point_velocity(self, point: MeasurementPoint) -> Tuple[float, float, float]:
        """측선의 각 깊이별 유속 계산

        Returns:
            (v_02, v_06, v_08): 각 깊이별 유속 (m/s)
        """
        v_02 = self.n_to_velocity(point.velocity_02d.n_per_t) if point.velocity_02d else 0
        v_06 = self.n_to_velocity(point.velocity_06d.n_per_t) if point.velocity_06d else 0
        v_08 = self.n_to_velocity(point.velocity_08d.n_per_t) if point.velocity_08d else 0

        return v_02, v_06, v_08

    def calculate_mean_velocity(self, point: MeasurementPoint) -> float:
        """평균 유속 계산

        1점법: Vm = V_0.6
        2점법: Vm = (V_0.2 + V_0.8) / 2
        3점법: Vm = (V_0.2 + 2*V_0.6 + V_0.8) / 4
        """
        v_02, v_06, v_08 = self.calculate_point_velocity(point)
        method = point.velocity_method

        if method == VelocityMethod.ONE_POINT:
            return v_06
        elif method == VelocityMethod.TWO_POINT:
            return (v_02 + v_08) / 2
        else:  # THREE_POINT
            return (v_02 + 2 * v_06 + v_08) / 4
```

### 4.3 유량 계산기 (calculators/discharge.py)
```python
from typing import List, Tuple
from ..models.measurement import MeasurementPoint

class DischargeCalculator:
    """유량 계산기 (Mid-Section Method)"""

    def calculate_section_width(self, points: List[MeasurementPoint], index: int) -> float:
        """측선 폭 계산

        첫 번째 측선: (d[1] - d[0]) / 2
        중간 측선: (d[i+1] - d[i-1]) / 2
        마지막 측선: (d[n] - d[n-1]) / 2
        """
        n = len(points)
        if n == 0:
            return 0

        if index == 0:
            if n > 1:
                return (points[1].distance - points[0].distance) / 2
            return 0
        elif index == n - 1:
            return (points[n-1].distance - points[n-2].distance) / 2
        else:
            return (points[index+1].distance - points[index-1].distance) / 2

    def calculate_section_area(self, width: float, depth: float) -> float:
        """구간 단면적"""
        return width * depth

    def calculate_section_discharge(self, area: float, velocity: float) -> float:
        """구간 유량"""
        return area * velocity

    def calculate_wetted_perimeter(self, points: List[MeasurementPoint]) -> float:
        """윤변 계산"""
        if len(points) < 2:
            return 0

        perimeter = 0
        for i in range(len(points) - 1):
            dx = points[i+1].distance - points[i].distance
            dy = points[i+1].depth - points[i].depth
            perimeter += (dx**2 + dy**2) ** 0.5

        return perimeter

    def calculate_all(self, points: List[MeasurementPoint],
                      velocities: List[float]) -> dict:
        """전체 유량 계산

        Returns:
            {
                'sections': [...],  # 구간별 결과
                'total_area': float,
                'total_discharge': float,
                'wetted_perimeter': float,
                'hydraulic_radius': float,
                'surface_width': float,
                'mean_velocity': float
            }
        """
        sections = []
        total_area = 0
        total_discharge = 0

        for i, (point, velocity) in enumerate(zip(points, velocities)):
            width = self.calculate_section_width(points, i)
            area = self.calculate_section_area(width, point.depth)
            discharge = self.calculate_section_discharge(area, velocity)

            sections.append({
                'section_no': point.section_no,
                'distance': point.distance,
                'width': width,
                'depth': point.depth,
                'velocity': velocity,
                'area': area,
                'discharge': discharge
            })

            total_area += area
            total_discharge += discharge

        wetted_perimeter = self.calculate_wetted_perimeter(points)
        hydraulic_radius = total_area / wetted_perimeter if wetted_perimeter > 0 else 0
        surface_width = points[-1].distance - points[0].distance if points else 0
        mean_velocity = total_discharge / total_area if total_area > 0 else 0

        return {
            'sections': sections,
            'total_area': total_area,
            'total_discharge': total_discharge,
            'wetted_perimeter': wetted_perimeter,
            'hydraulic_radius': hydraulic_radius,
            'surface_width': surface_width,
            'mean_velocity': mean_velocity
        }
```

### 4.4 불확실도 계산기 (calculators/uncertainty.py)
```python
import math
from typing import Dict, List
from dataclasses import dataclass

@dataclass
class UncertaintyComponents:
    """불확실도 구성요소"""
    Xb: float = 0  # 하폭측정
    Xd: float = 0  # 수심측정
    Xe: float = 0  # 측정시간
    Xp: float = 0  # 측점수
    Xc: float = 0  # 유속계보정

class UncertaintyCalculator:
    """ISO 748 기반 불확실도 계산기"""

    def __init__(self, params: Dict):
        """
        Args:
            params: 불확실도 계산 파라미터
                - systematic_width: 하폭 계통 불확실도 (%)
                - systematic_depth: 수심 계통 불확실도 (%)
                - systematic_meter: 유속계 계통 불확실도 (%)
        """
        self.params = params

    def calculate_random_uncertainty(self,
                                     section_data: List[Dict]) -> UncertaintyComponents:
        """무작위 불확실도 계산

        각 구간의 유량 비중을 가중치로 사용
        """
        total_q = sum(s['discharge'] for s in section_data)
        if total_q == 0:
            return UncertaintyComponents()

        # 가중 평균 계산
        weighted_Xb = 0
        weighted_Xd = 0
        weighted_Xe = 0
        weighted_Xp = 0
        weighted_Xc = 0

        for section in section_data:
            weight = (section['discharge'] / total_q) ** 2

            # ISO 748 공식에 따른 개별 불확실도 계산
            # 실제 구현시 para 시트의 파라미터 사용
            weighted_Xb += weight * self.params.get('random_width', 1.0) ** 2
            weighted_Xd += weight * self.params.get('random_depth', 1.0) ** 2
            weighted_Xe += weight * self._time_uncertainty(section.get('measurement_time', 60)) ** 2
            weighted_Xp += weight * self._points_uncertainty(section.get('num_points', 1)) ** 2
            weighted_Xc += weight * self.params.get('random_meter', 1.0) ** 2

        return UncertaintyComponents(
            Xb=math.sqrt(weighted_Xb),
            Xd=math.sqrt(weighted_Xd),
            Xe=math.sqrt(weighted_Xe),
            Xp=math.sqrt(weighted_Xp),
            Xc=math.sqrt(weighted_Xc)
        )

    def _time_uncertainty(self, measurement_time: float) -> float:
        """측정시간에 따른 불확실도"""
        # ISO 748 Table 참조
        if measurement_time >= 60:
            return 1.0
        elif measurement_time >= 40:
            return 1.5
        else:
            return 2.5

    def _points_uncertainty(self, num_points: int) -> float:
        """측점수에 따른 불확실도"""
        # ISO 748 Table 참조
        if num_points >= 3:
            return 2.5
        elif num_points >= 2:
            return 3.5
        else:
            return 7.5

    def calculate_systematic_uncertainty(self) -> UncertaintyComponents:
        """계통 불확실도 계산"""
        return UncertaintyComponents(
            Xb=self.params.get('systematic_width', 0.5),
            Xd=self.params.get('systematic_depth', 0.5),
            Xc=self.params.get('systematic_meter', 1.0)
        )

    def combine_uncertainties(self,
                              random: UncertaintyComponents,
                              systematic: UncertaintyComponents) -> Dict:
        """불확실도 합성 (RSS - Root Sum of Squares)"""
        # 무작위 불확실도 합성
        X_prime_Q = math.sqrt(
            random.Xb**2 + random.Xd**2 + random.Xe**2 +
            random.Xp**2 + random.Xc**2
        )

        # 계통 불확실도 합성
        X_double_Q = math.sqrt(
            systematic.Xb**2 + systematic.Xd**2 + systematic.Xc**2
        )

        # 전체 불확실도
        XQ_total = math.sqrt(X_prime_Q**2 + X_double_Q**2)

        return {
            'random_components': {
                'Xb': random.Xb,
                'Xd': random.Xd,
                'Xe': random.Xe,
                'Xp': random.Xp,
                'Xc': random.Xc,
                'combined': X_prime_Q
            },
            'systematic_components': {
                'Xb': systematic.Xb,
                'Xd': systematic.Xd,
                'Xc': systematic.Xc,
                'combined': X_double_Q
            },
            'total_uncertainty': XQ_total
        }
```

---

## 5. 테스트 전략

### 5.1 단위 테스트
```python
# tests/test_calculators.py
import pytest
from src.calculators.velocity import VelocityCalculator
from src.calculators.discharge import DischargeCalculator

class TestVelocityCalculator:
    def test_n_to_velocity(self):
        calc = VelocityCalculator(a=0.0, b=0.0545)
        result = calc.n_to_velocity(10.0)
        assert abs(result - 0.545) < 0.001

    def test_mean_velocity_two_point(self):
        # 2점법 테스트
        pass

class TestDischargeCalculator:
    def test_section_width_first(self):
        # 첫 번째 측선 폭 계산 테스트
        pass

    def test_total_discharge(self):
        # 총 유량 계산 테스트
        pass
```

### 5.2 통합 테스트
```python
# tests/test_integration.py
import pytest
from src.parsers.excel_parser import ExcelParser
from src.calculators.velocity import VelocityCalculator
from src.calculators.discharge import DischargeCalculator

class TestExcelComparison:
    """Excel 결과와 Python 결과 비교"""

    @pytest.fixture
    def excel_data(self):
        parser = ExcelParser("data/경주대종천하류보20250501_unlocked.xlsm")
        return parser.parse()

    def test_discharge_matches_excel(self, excel_data):
        # Excel의 유량 결과와 Python 계산 결과 비교
        expected_discharge = 0.024  # Excel 평균!H11 값
        calculated = calculate_discharge(excel_data)
        assert abs(calculated - expected_discharge) < 0.001

    def test_uncertainty_matches_excel(self, excel_data):
        # Excel의 불확실도와 Python 계산 결과 비교
        expected_uncertainty = 5.5  # Excel 평균!J17 값 (%)
        calculated = calculate_uncertainty(excel_data)
        assert abs(calculated - expected_uncertainty) < 0.1
```

---

## 6. 마일스톤

| 단계 | 목표 | 산출물 |
|------|------|--------|
| M1 | 프로젝트 설정 완료 | 프로젝트 구조, 의존성 설치 |
| M2 | 데이터 파싱 완료 | Excel → Python 객체 변환 |
| M3 | 기본 계산 구현 | 유속, 유량 계산 검증 |
| M4 | 불확실도 구현 | 불확실도 계산 검증 |
| M5 | 출력 구현 | Excel/PDF 보고서 생성 |
| M6 | 검증 완료 | 전체 테스트 통과 |

---

## 7. 리스크 및 대응

| 리스크 | 영향 | 대응 방안 |
|--------|------|----------|
| para/Rantz 시트 파라미터 미파악 | 높음 | 추가 분석 수행 |
| 복잡한 수식 오류 | 중간 | 단계별 검증 |
| 매크로 의존 로직 | 중간 | VBA 코드 분석 |
| 엣지 케이스 미대응 | 낮음 | 도움말 시트 참조 |

---

## 8. 시작 명령어

```bash
# 프로젝트 초기화
mkdir -p src/{models,parsers,calculators,calibration,reporters,utils}
mkdir -p tests data config

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install openpyxl xlrd pandas numpy pyyaml pydantic pytest

# 테스트 실행
pytest tests/ -v
```

---

*작성일: 2025-12-19*
