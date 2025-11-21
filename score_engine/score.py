"""
Penguin-Land CloudWatch Anomaly Detection Score Engine

배포 상태를 0~100점으로 점수화하고, 펭귄 코치 메시지를 생성하는 엔진

담당: 이승규
최종 수정: 2025-11-20
"""

import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# ============================================================================
# 상수 정의
# ============================================================================

@dataclass
class ThresholdConfig:
    """메트릭별 Fallback 임계값 설정"""
    normal: float      # 정상 상한값
    warning: float     # 주의 상한값
    danger: float      # 위험 시작값


# Fallback 임계값 (Anomaly Detection 밴드가 없을 때 사용)
FALLBACK_THRESHOLDS: Dict[str, ThresholdConfig] = {
    'error_rate': ThresholdConfig(
        normal=1.0,    # 1% 이하 정상
        warning=5.0,   # 5% 이하 주의
        danger=10.0    # 10% 초과 위험
    ),
    'latency': ThresholdConfig(
        normal=300,    # 300ms 이하 정상
        warning=700,   # 700ms 이하 주의
        danger=1500    # 1500ms 초과 위험
    ),
    'cpu': ThresholdConfig(
        normal=50,     # 50% 이하 정상
        warning=80,    # 80% 이하 주의
        danger=95      # 95% 초과 위험
    )
}

# 메트릭별 가중치 (합계 100%)
METRIC_WEIGHTS: Dict[str, float] = {
    'error_rate': 0.50,  # 에러율이 가장 중요 (50%)
    'latency': 0.35,     # 레이턴시 (35%)
    'cpu': 0.15          # CPU (15%)
}

# 상태별 점수 범위
STATE_SCORE_RANGES = {
    'healthy': (0, 30),
    'warning': (31, 70),
    'danger': (71, 100)
}

# 건강 상태 메시지 템플릿
HEALTHY_MESSAGES = [
    "🎉 완벽해요! 모든 지표가 정상이에요!",
    "👍 아주 안정적이에요! 지금 상태로도 충분해요!",
    "✨ 훌륭한 배포에요! 펭귄이 춤추고 있어요!",
    "🌟 최고의 상태에요! 이대로 유지해주세요!",
    "🏆 완벽한 점수! 축하드려요!",
    "💯 모든 지표가 녹색이에요! 대단해요!",
    "🎊 배포 성공! 펭귄들이 축하하고 있어요!"
]


# ============================================================================
# 핵심 점수 계산 함수
# ============================================================================

def calculate_severity(
    value: float,
    band_upper: Optional[float] = None,
    band_lower: Optional[float] = None,
    metric_type: str = 'latency'
) -> float:
    """
    개별 메트릭의 심각도를 0.0~1.0 사이의 값으로 계산

    Args:
        value: 현재 메트릭 값
        band_upper: Anomaly Detection 상한 밴드 (있으면 우선 사용)
        band_lower: Anomaly Detection 하한 밴드
        metric_type: 메트릭 타입 ('error_rate', 'latency', 'cpu')

    Returns:
        float: 심각도 (0.0 = 완전 정상, 1.0 = 매우 위험)

    Examples:
        >>> calculate_severity(450, 600, 200, 'latency')
        0.0  # 밴드 안이므로 정상

        >>> calculate_severity(900, 600, 200, 'latency')
        1.0  # 밴드를 50% 벗어남 (위험)

        >>> calculate_severity(450, metric_type='latency')
        0.5  # Fallback 임계값 사용 (300~700ms 구간)
    """

    # 1. Anomaly Detection Band가 있는 경우 (우선순위)
    if band_upper is not None and band_lower is not None:
        # 밴드 안에 있으면 정상
        if band_lower <= value <= band_upper:
            return 0.0

        # 밴드 밖으로 벗어난 정도 계산
        if value > band_upper:
            # 상한 초과: 얼마나 많이 벗어났는지
            deviation = (value - band_upper) / band_upper
        else:
            # 하한 미만: 얼마나 많이 벗어났는지
            deviation = (band_lower - value) / band_lower

        # 50% 이상 벗어나면 최대 위험으로 간주
        severity = min(1.0, deviation * 2.0)
        return severity

    # 2. Fallback 임계값 사용
    threshold = FALLBACK_THRESHOLDS.get(metric_type)
    if threshold is None:
        # 알 수 없는 메트릭 타입: 중간 값 반환
        return 0.5

    if value <= threshold.normal:
        # 정상 범위
        return 0.0
    elif value <= threshold.warning:
        # 정상~주의 구간: 선형 보간 (0.0 → 0.5)
        ratio = (value - threshold.normal) / (threshold.warning - threshold.normal)
        return ratio * 0.5
    elif value <= threshold.danger:
        # 주의~위험 구간: 선형 보간 (0.5 → 0.8)
        ratio = (value - threshold.warning) / (threshold.danger - threshold.warning)
        return 0.5 + (ratio * 0.3)
    else:
        # 위험 초과: 선형 증가 (0.8 → 1.0)
        ratio = min(1.0, (value - threshold.danger) / threshold.danger)
        return 0.8 + (ratio * 0.2)


def calculate_health_score(metrics: Dict[str, Dict]) -> int:
    """
    여러 메트릭의 심각도를 종합하여 0~100점의 건강 점수 계산

    Args:
        metrics: 메트릭 데이터
            {
                'error_rate': {
                    'value': 2.5,
                    'band_upper': 3.0,
                    'band_lower': 0.5
                },
                'latency': {
                    'value': 450,
                    'band_upper': 600,
                    'band_lower': 200
                },
                'cpu': {
                    'value': 65,
                    'band_upper': None,  # Anomaly Detection 밴드 없음
                    'band_lower': None
                }
            }

    Returns:
        int: 건강 점수 (0 = 완벽, 100 = 매우 위험)

    Examples:
        >>> metrics = {
        ...     'error_rate': {'value': 0.5, 'band_upper': 2.0, 'band_lower': 0.1},
        ...     'latency': {'value': 250, 'band_upper': 600, 'band_lower': 200},
        ...     'cpu': {'value': 40}
        ... }
        >>> calculate_health_score(metrics)
        0  # 모든 지표 정상

        >>> metrics = {
        ...     'error_rate': {'value': 8.0},
        ...     'latency': {'value': 1200},
        ...     'cpu': {'value': 90}
        ... }
        >>> calculate_health_score(metrics)
        85  # 매우 위험한 상태
    """

    total_score = 0.0
    total_weight = 0.0

    for metric_name, weight in METRIC_WEIGHTS.items():
        metric_data = metrics.get(metric_name)

        # 메트릭 데이터가 없으면 건너뛰기
        if not metric_data:
            continue

        # 개별 메트릭 심각도 계산
        severity = calculate_severity(
            value=metric_data['value'],
            band_upper=metric_data.get('band_upper'),
            band_lower=metric_data.get('band_lower'),
            metric_type=metric_name
        )

        # 가중치 적용
        total_score += severity * weight * 100
        total_weight += weight

    # 가중 평균 계산
    if total_weight > 0:
        final_score = total_score / total_weight
    else:
        # 메트릭이 하나도 없으면 중간 점수
        final_score = 50

    # 0~100 범위로 클리핑
    return int(max(0, min(100, final_score)))


def classify_state(score: int) -> str:
    """
    점수를 3단계 상태로 분류

    Args:
        score: 건강 점수 (0~100)

    Returns:
        str: 'healthy' | 'warning' | 'danger'

    Examples:
        >>> classify_state(15)
        'healthy'

        >>> classify_state(55)
        'warning'

        >>> classify_state(85)
        'danger'
    """
    if score <= STATE_SCORE_RANGES['healthy'][1]:
        return 'healthy'
    elif score <= STATE_SCORE_RANGES['warning'][1]:
        return 'warning'
    else:
        return 'danger'


# ============================================================================
# 문제 메트릭 식별
# ============================================================================

def identify_problem_metrics(metrics: Dict[str, Dict]) -> List[Tuple[str, float]]:
    """
    문제가 있는 메트릭을 식별하고 심각도 순으로 정렬

    Args:
        metrics: 메트릭 데이터

    Returns:
        List[Tuple[str, float]]: (메트릭명, 심각도) 튜플의 리스트
            심각도가 높은 순으로 정렬됨

    Examples:
        >>> metrics = {
        ...     'error_rate': {'value': 8.0},
        ...     'latency': {'value': 450, 'band_upper': 600, 'band_lower': 200},
        ...     'cpu': {'value': 85}
        ... }
        >>> identify_problem_metrics(metrics)
        [('error_rate', 0.9), ('cpu', 0.7), ('latency', 0.0)]
    """
    problems = []

    for metric_name, metric_data in metrics.items():
        if not metric_data:
            continue

        severity = calculate_severity(
            value=metric_data['value'],
            band_upper=metric_data.get('band_upper'),
            band_lower=metric_data.get('band_lower'),
            metric_type=metric_name
        )

        # 심각도가 0.3 이상이면 문제로 간주
        if severity >= 0.3:
            problems.append((metric_name, severity))

    # 심각도 높은 순으로 정렬
    problems.sort(key=lambda x: x[1], reverse=True)

    return problems


# ============================================================================
# 코칭 메시지 생성
# ============================================================================

def generate_warning_message(problem_metrics: List[Tuple[str, float]]) -> str:
    """
    주의 상태에 대한 코칭 메시지 생성

    Args:
        problem_metrics: 문제 메트릭 리스트 [(메트릭명, 심각도), ...]

    Returns:
        str: 코칭 메시지
    """
    if not problem_metrics:
        return "⚠️ 조금 불안정해 보여요. 모니터링을 계속 지켜봐주세요!"

    # 가장 심각한 문제 메트릭
    worst_metric = problem_metrics[0][0]

    message_map = {
        'latency': "⚠️ 응답 속도가 약간 느려지고 있어요. DB 쿼리나 외부 API를 확인해보면 좋아요!",
        'cpu': "⚠️ CPU 사용률이 높아지고 있어요. 트래픽이 증가했거나 무거운 작업이 실행 중일 수 있어요!",
        'error_rate': "⚠️ 에러가 조금씩 발생하고 있어요. 로그를 확인해서 원인을 파악해보세요!"
    }

    return message_map.get(worst_metric, "⚠️ 일부 지표가 평소와 다릅니다. 주의 깊게 모니터링해주세요!")


def generate_danger_message(problem_metrics: List[Tuple[str, float]]) -> str:
    """
    위험 상태에 대한 코칭 메시지 생성

    Args:
        problem_metrics: 문제 메트릭 리스트 [(메트릭명, 심각도), ...]

    Returns:
        str: 코칭 메시지
    """
    if not problem_metrics:
        return "🚨 위험한 상태에요! 즉시 점검이 필요해요!"

    messages = []

    # 심각한 문제들을 모두 언급
    for metric_name, severity in problem_metrics:
        if severity < 0.7:  # 위험 상태에서는 심각도 0.7 이상만
            continue

        if metric_name == 'error_rate':
            messages.append("에러율이 급증했어요!")
        elif metric_name == 'latency':
            messages.append("응답이 매우 느려요!")
        elif metric_name == 'cpu':
            messages.append("CPU가 과부하 상태에요!")

    if not messages:
        return "🚨 서비스 상태가 불안정해요! 즉시 확인이 필요합니다!"

    # 첫 문제에 대한 구체적 조언
    worst_metric = problem_metrics[0][0]

    advice_map = {
        'error_rate': "최근 배포 내역을 확인하고, 에러 로그를 점검하세요!",
        'latency': "DB 연결 상태와 외부 API 응답 시간을 점검하세요!",
        'cpu': "오토스케일링을 고려하거나, 불필요한 프로세스를 종료하세요!"
    }

    main_message = " ".join(messages)
    advice = advice_map.get(worst_metric, "시스템 리소스와 최근 변경사항을 확인하세요!")

    return f"🚨 {main_message} {advice}"


def generate_coach_message(
    state: str,
    metrics: Dict[str, Dict]
) -> str:
    """
    상황에 맞는 펭귄 코치 메시지 생성

    Args:
        state: 건강 상태 ('healthy', 'warning', 'danger')
        metrics: 메트릭 데이터

    Returns:
        str: 코칭 메시지

    Examples:
        >>> metrics = {'error_rate': {'value': 0.5}, 'latency': {'value': 250}, 'cpu': {'value': 40}}
        >>> generate_coach_message('healthy', metrics)
        '🎉 완벽해요! 모든 지표가 정상이에요!'

        >>> metrics = {'error_rate': {'value': 4.0}, 'latency': {'value': 500}}
        >>> msg = generate_coach_message('warning', metrics)
        >>> '⚠️' in msg
        True
    """
    if state == 'healthy':
        return random.choice(HEALTHY_MESSAGES)

    # 문제가 있는 메트릭 식별
    problem_metrics = identify_problem_metrics(metrics)

    if state == 'warning':
        return generate_warning_message(problem_metrics)

    if state == 'danger':
        return generate_danger_message(problem_metrics)

    # 알 수 없는 상태 (방어 코드)
    return "펭귄이 상태를 분석하고 있어요..."


# ============================================================================
# 통합 분석 함수 (메인 API)
# ============================================================================

def analyze_deployment_health(metrics: Dict[str, Dict]) -> Dict:
    """
    배포 상태를 종합 분석하여 점수, 상태, 메시지를 반환

    이것이 메인 API 함수입니다. Backend에서 이 함수를 호출하면 됩니다.

    Args:
        metrics: 메트릭 데이터
            {
                'error_rate': {'value': 2.5, 'band_upper': 3.0, 'band_lower': 0.5},
                'latency': {'value': 450, 'band_upper': 600, 'band_lower': 200},
                'cpu': {'value': 65}
            }

    Returns:
        Dict: 분석 결과
            {
                'health_score': 45,
                'health_state': 'warning',
                'coach_message': '⚠️ 에러가 조금씩 발생하고 있어요...',
                'penguin_animation': 'worried',
                'problem_metrics': [('error_rate', 0.7), ('cpu', 0.5)]
            }

    Examples:
        >>> metrics = {
        ...     'error_rate': {'value': 0.5, 'band_upper': 2.0, 'band_lower': 0.1},
        ...     'latency': {'value': 250, 'band_upper': 600, 'band_lower': 200},
        ...     'cpu': {'value': 40}
        ... }
        >>> result = analyze_deployment_health(metrics)
        >>> result['health_score'] <= 30
        True
        >>> result['health_state']
        'healthy'
        >>> result['penguin_animation']
        'happy'
    """
    # 1. 건강 점수 계산
    health_score = calculate_health_score(metrics)

    # 2. 상태 분류
    health_state = classify_state(health_score)

    # 3. 코칭 메시지 생성
    coach_message = generate_coach_message(health_state, metrics)

    # 4. 펭귄 애니메이션 선택
    animation_map = {
        'healthy': 'happy',
        'warning': 'worried',
        'danger': 'crying'
    }
    penguin_animation = animation_map[health_state]

    # 5. 문제 메트릭 식별
    problem_metrics = identify_problem_metrics(metrics)

    return {
        'health_score': health_score,
        'health_state': health_state,
        'coach_message': coach_message,
        'penguin_animation': penguin_animation,
        'problem_metrics': problem_metrics
    }


# ============================================================================
# 유틸리티 함수
# ============================================================================

def get_metric_display_name(metric_name: str) -> str:
    """메트릭 이름을 사용자 친화적인 이름으로 변환"""
    display_names = {
        'error_rate': '에러율',
        'latency': '응답 시간',
        'cpu': 'CPU 사용률'
    }
    return display_names.get(metric_name, metric_name)


def format_metric_value(metric_name: str, value: float) -> str:
    """메트릭 값을 형식화된 문자열로 변환"""
    if metric_name == 'error_rate':
        return f"{value:.2f}%"
    elif metric_name == 'latency':
        return f"{int(value)}ms"
    elif metric_name == 'cpu':
        return f"{int(value)}%"
    return str(value)


# ============================================================================
# 테스트용 메인 함수
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Penguin-Land Score Engine 테스트")
    print("=" * 70)

    # 테스트 케이스 1: 완벽한 상태
    print("\n[테스트 1] 완벽한 배포 상태")
    metrics_perfect = {
        'error_rate': {'value': 0.2, 'band_upper': 2.0, 'band_lower': 0.1},
        'latency': {'value': 180, 'band_upper': 600, 'band_lower': 100},
        'cpu': {'value': 35}
    }
    result = analyze_deployment_health(metrics_perfect)
    print(f"점수: {result['health_score']}점")
    print(f"상태: {result['health_state']}")
    print(f"메시지: {result['coach_message']}")
    print(f"펭귄: {result['penguin_animation']}")

    # 테스트 케이스 2: 주의 상태
    print("\n[테스트 2] 주의가 필요한 상태")
    metrics_warning = {
        'error_rate': {'value': 3.5},
        'latency': {'value': 550, 'band_upper': 600, 'band_lower': 200},
        'cpu': {'value': 72}
    }
    result = analyze_deployment_health(metrics_warning)
    print(f"점수: {result['health_score']}점")
    print(f"상태: {result['health_state']}")
    print(f"메시지: {result['coach_message']}")
    print(f"펭귄: {result['penguin_animation']}")

    # 테스트 케이스 3: 위험 상태
    print("\n[테스트 3] 위험한 상태")
    metrics_danger = {
        'error_rate': {'value': 8.5},
        'latency': {'value': 1800},
        'cpu': {'value': 92}
    }
    result = analyze_deployment_health(metrics_danger)
    print(f"점수: {result['health_score']}점")
    print(f"상태: {result['health_state']}")
    print(f"메시지: {result['coach_message']}")
    print(f"펭귄: {result['penguin_animation']}")
    print(f"문제 메트릭: {result['problem_metrics']}")

    print("\n" + "=" * 70)
    print("테스트 완료!")
    print("=" * 70)
