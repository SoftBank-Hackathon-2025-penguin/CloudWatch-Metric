"""
Penguin-Land Score Engine 테스트 코드

pytest로 점수 계산 로직을 검증합니다.

실행 방법:
    cd score_engine
    pytest test_score.py -v
"""

import pytest
from score import (
    calculate_severity,
    calculate_health_score,
    classify_state,
    identify_problem_metrics,
    generate_coach_message,
    analyze_deployment_health
)


class TestCalculateSeverity:
    """calculate_severity() 함수 테스트"""

    def test_with_band_inside(self):
        """밴드 안에 있을 때 - 정상"""
        severity = calculate_severity(
            value=450,
            band_upper=600,
            band_lower=200,
            metric_type='latency'
        )
        assert severity == 0.0, "밴드 안에 있으면 심각도 0.0이어야 함"

    def test_with_band_above_upper(self):
        """밴드 상한을 초과했을 때"""
        severity = calculate_severity(
            value=900,  # 600의 50% 초과
            band_upper=600,
            band_lower=200,
            metric_type='latency'
        )
        assert severity == 1.0, "밴드를 50% 이상 벗어나면 최대 위험"

    def test_with_band_below_lower(self):
        """밴드 하한 미만일 때"""
        severity = calculate_severity(
            value=100,  # 200의 50% 미만
            band_upper=600,
            band_lower=200,
            metric_type='latency'
        )
        assert severity == 1.0, "밴드를 50% 이상 벗어나면 최대 위험"

    def test_fallback_normal(self):
        """Fallback: 정상 범위"""
        severity = calculate_severity(
            value=250,  # 300ms 이하
            metric_type='latency'
        )
        assert severity == 0.0, "Fallback 정상 범위는 심각도 0.0"

    def test_fallback_warning(self):
        """Fallback: 주의 범위"""
        severity = calculate_severity(
            value=500,  # 300~700ms
            metric_type='latency'
        )
        assert 0.0 < severity < 0.8, "Fallback 주의 범위는 0~0.8 사이"

    def test_fallback_danger(self):
        """Fallback: 위험 범위"""
        severity = calculate_severity(
            value=1500,  # 1500ms 이상
            metric_type='latency'
        )
        assert severity >= 0.8, "Fallback 위험 범위는 0.8 이상"

    def test_error_rate_threshold(self):
        """에러율 Fallback 임계값"""
        # 정상
        assert calculate_severity(0.5, metric_type='error_rate') == 0.0
        # 주의
        severity_warning = calculate_severity(3.0, metric_type='error_rate')
        assert 0.0 < severity_warning < 0.8
        # 위험
        severity_danger = calculate_severity(12.0, metric_type='error_rate')
        assert severity_danger >= 0.8

    def test_cpu_threshold(self):
        """CPU Fallback 임계값"""
        # 정상
        assert calculate_severity(40, metric_type='cpu') == 0.0
        # 주의
        severity_warning = calculate_severity(70, metric_type='cpu')
        assert 0.0 < severity_warning < 0.8
        # 위험
        severity_danger = calculate_severity(96, metric_type='cpu')
        assert severity_danger >= 0.8


class TestCalculateHealthScore:
    """calculate_health_score() 함수 테스트"""

    def test_perfect_score(self):
        """모든 메트릭이 정상일 때"""
        metrics = {
            'error_rate': {'value': 0.2, 'band_upper': 2.0, 'band_lower': 0.1},
            'latency': {'value': 250, 'band_upper': 600, 'band_lower': 200},
            'cpu': {'value': 40}
        }
        score = calculate_health_score(metrics)
        assert 0 <= score <= 30, f"완벽한 상태는 0~30점이어야 함, 실제: {score}"

    def test_warning_score(self):
        """주의 상태"""
        metrics = {
            'error_rate': {'value': 3.5},  # 주의
            'latency': {'value': 550, 'band_upper': 600, 'band_lower': 200},  # 정상
            'cpu': {'value': 72}  # 주의
        }
        score = calculate_health_score(metrics)
        assert 31 <= score <= 70, f"주의 상태는 31~70점이어야 함, 실제: {score}"

    def test_danger_score(self):
        """위험 상태"""
        metrics = {
            'error_rate': {'value': 8.5},  # 위험
            'latency': {'value': 1800},  # 위험
            'cpu': {'value': 92}  # 위험
        }
        score = calculate_health_score(metrics)
        assert 71 <= score <= 100, f"위험 상태는 71~100점이어야 함, 실제: {score}"

    def test_empty_metrics(self):
        """메트릭이 없을 때"""
        metrics = {}
        score = calculate_health_score(metrics)
        assert 0 <= score <= 100, "점수는 항상 0~100 사이여야 함"

    def test_partial_metrics(self):
        """일부 메트릭만 있을 때"""
        metrics = {
            'error_rate': {'value': 2.0}
        }
        score = calculate_health_score(metrics)
        assert 0 <= score <= 100, "부분 메트릭도 점수 계산 가능해야 함"

    def test_metric_weights(self):
        """에러율 가중치가 가장 높은지 확인"""
        # 에러율만 위험
        metrics_error = {
            'error_rate': {'value': 10.0},
            'latency': {'value': 250},
            'cpu': {'value': 40}
        }
        score_error = calculate_health_score(metrics_error)

        # CPU만 위험
        metrics_cpu = {
            'error_rate': {'value': 0.5},
            'latency': {'value': 250},
            'cpu': {'value': 95}
        }
        score_cpu = calculate_health_score(metrics_cpu)

        # 에러율이 위험할 때 점수가 더 높아야 함 (가중치 50% vs 15%)
        assert score_error > score_cpu, "에러율의 가중치가 CPU보다 높아야 함"


class TestClassifyState:
    """classify_state() 함수 테스트"""

    def test_healthy_state(self):
        """건강 상태 분류"""
        assert classify_state(0) == 'healthy'
        assert classify_state(15) == 'healthy'
        assert classify_state(30) == 'healthy'

    def test_warning_state(self):
        """주의 상태 분류"""
        assert classify_state(31) == 'warning'
        assert classify_state(50) == 'warning'
        assert classify_state(70) == 'warning'

    def test_danger_state(self):
        """위험 상태 분류"""
        assert classify_state(71) == 'danger'
        assert classify_state(85) == 'danger'
        assert classify_state(100) == 'danger'

    def test_boundary_values(self):
        """경계값 테스트"""
        assert classify_state(30) == 'healthy'
        assert classify_state(31) == 'warning'
        assert classify_state(70) == 'warning'
        assert classify_state(71) == 'danger'


class TestIdentifyProblemMetrics:
    """identify_problem_metrics() 함수 테스트"""

    def test_no_problems(self):
        """문제 없는 경우"""
        metrics = {
            'error_rate': {'value': 0.5},
            'latency': {'value': 250},
            'cpu': {'value': 40}
        }
        problems = identify_problem_metrics(metrics)
        assert len(problems) == 0, "정상 상태는 문제 메트릭이 없어야 함"

    def test_single_problem(self):
        """하나의 문제"""
        metrics = {
            'error_rate': {'value': 6.0},  # 문제!
            'latency': {'value': 250},
            'cpu': {'value': 40}
        }
        problems = identify_problem_metrics(metrics)
        assert len(problems) == 1, "하나의 문제만 있어야 함"
        assert problems[0][0] == 'error_rate', "에러율이 문제로 식별되어야 함"

    def test_multiple_problems(self):
        """여러 문제"""
        metrics = {
            'error_rate': {'value': 8.0},  # 문제!
            'latency': {'value': 1200},  # 문제!
            'cpu': {'value': 90}  # 문제!
        }
        problems = identify_problem_metrics(metrics)
        assert len(problems) == 3, "3개의 문제가 있어야 함"

    def test_sorted_by_severity(self):
        """심각도 순으로 정렬되는지 확인"""
        metrics = {
            'error_rate': {'value': 8.0},  # 매우 심각
            'latency': {'value': 500},  # 약간 문제
            'cpu': {'value': 90}  # 심각
        }
        problems = identify_problem_metrics(metrics)
        # 첫 번째가 가장 심각해야 함
        assert problems[0][1] >= problems[1][1], "심각도 순으로 정렬되어야 함"
        assert problems[1][1] >= problems[2][1], "심각도 순으로 정렬되어야 함"


class TestGenerateCoachMessage:
    """generate_coach_message() 함수 테스트"""

    def test_healthy_message(self):
        """건강 상태 메시지"""
        metrics = {
            'error_rate': {'value': 0.5},
            'latency': {'value': 250},
            'cpu': {'value': 40}
        }
        message = generate_coach_message('healthy', metrics)
        assert len(message) > 0, "메시지가 생성되어야 함"
        assert any(emoji in message for emoji in ['🎉', '👍', '✨', '🌟', '🏆', '💯', '🎊']), \
            "건강 상태는 긍정적인 이모지가 있어야 함"

    def test_warning_message(self):
        """주의 상태 메시지"""
        metrics = {
            'error_rate': {'value': 4.0},
            'latency': {'value': 550},
            'cpu': {'value': 70}
        }
        message = generate_coach_message('warning', metrics)
        assert '⚠️' in message, "주의 상태는 경고 이모지가 있어야 함"
        assert len(message) > 0, "메시지가 생성되어야 함"

    def test_danger_message(self):
        """위험 상태 메시지"""
        metrics = {
            'error_rate': {'value': 10.0},
            'latency': {'value': 2000},
            'cpu': {'value': 95}
        }
        message = generate_coach_message('danger', metrics)
        assert '🚨' in message, "위험 상태는 긴급 이모지가 있어야 함"
        assert len(message) > 0, "메시지가 생성되어야 함"

    def test_message_relevance(self):
        """메시지가 문제와 관련 있는지 확인"""
        # 에러율 문제
        metrics_error = {
            'error_rate': {'value': 8.0},
            'latency': {'value': 250},
            'cpu': {'value': 40}
        }
        message = generate_coach_message('warning', metrics_error)
        assert '에러' in message, "에러율 문제일 때는 '에러'가 언급되어야 함"

        # 레이턴시 문제
        metrics_latency = {
            'error_rate': {'value': 0.5},
            'latency': {'value': 1000},
            'cpu': {'value': 40}
        }
        message = generate_coach_message('warning', metrics_latency)
        assert any(word in message for word in ['응답', '느려', '속도']), \
            "레이턴시 문제일 때는 관련 단어가 언급되어야 함"

        # CPU 문제
        metrics_cpu = {
            'error_rate': {'value': 0.5},
            'latency': {'value': 250},
            'cpu': {'value': 85}
        }
        message = generate_coach_message('warning', metrics_cpu)
        assert 'CPU' in message, "CPU 문제일 때는 'CPU'가 언급되어야 함"


class TestAnalyzeDeploymentHealth:
    """analyze_deployment_health() 통합 테스트"""

    def test_complete_analysis_healthy(self):
        """완전한 분석 - 건강 상태"""
        metrics = {
            'error_rate': {'value': 0.3, 'band_upper': 2.0, 'band_lower': 0.1},
            'latency': {'value': 220, 'band_upper': 600, 'band_lower': 150},
            'cpu': {'value': 35}
        }
        result = analyze_deployment_health(metrics)

        assert 'health_score' in result
        assert 'health_state' in result
        assert 'coach_message' in result
        assert 'penguin_animation' in result
        assert 'problem_metrics' in result

        assert result['health_state'] == 'healthy'
        assert result['penguin_animation'] == 'happy'
        assert 0 <= result['health_score'] <= 30

    def test_complete_analysis_warning(self):
        """완전한 분석 - 주의 상태"""
        metrics = {
            'error_rate': {'value': 3.5},
            'latency': {'value': 600},
            'cpu': {'value': 75}
        }
        result = analyze_deployment_health(metrics)

        assert result['health_state'] == 'warning'
        assert result['penguin_animation'] == 'worried'
        assert 31 <= result['health_score'] <= 70
        assert '⚠️' in result['coach_message']

    def test_complete_analysis_danger(self):
        """완전한 분석 - 위험 상태"""
        metrics = {
            'error_rate': {'value': 12.0},
            'latency': {'value': 2500},
            'cpu': {'value': 95}
        }
        result = analyze_deployment_health(metrics)

        assert result['health_state'] == 'danger'
        assert result['penguin_animation'] == 'crying'
        assert 71 <= result['health_score'] <= 100
        assert '🚨' in result['coach_message']
        assert len(result['problem_metrics']) > 0

    def test_api_response_structure(self):
        """API 응답 구조가 올바른지 확인"""
        metrics = {
            'error_rate': {'value': 2.0},
            'latency': {'value': 400}
        }
        result = analyze_deployment_health(metrics)

        # 필수 필드 확인
        required_fields = [
            'health_score',
            'health_state',
            'coach_message',
            'penguin_animation',
            'problem_metrics'
        ]
        for field in required_fields:
            assert field in result, f"필수 필드 '{field}'가 없음"

        # 타입 확인
        assert isinstance(result['health_score'], int)
        assert isinstance(result['health_state'], str)
        assert isinstance(result['coach_message'], str)
        assert isinstance(result['penguin_animation'], str)
        assert isinstance(result['problem_metrics'], list)


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_zero_values(self):
        """0 값 처리"""
        metrics = {
            'error_rate': {'value': 0.0},
            'latency': {'value': 0.0},
            'cpu': {'value': 0.0}
        }
        result = analyze_deployment_health(metrics)
        assert 0 <= result['health_score'] <= 100

    def test_extreme_values(self):
        """극단적인 값 처리"""
        metrics = {
            'error_rate': {'value': 100.0},
            'latency': {'value': 99999},
            'cpu': {'value': 100.0}
        }
        result = analyze_deployment_health(metrics)
        assert result['health_score'] <= 100
        assert result['health_state'] == 'danger'

    def test_negative_values(self):
        """음수 값 처리 (방어 코드)"""
        metrics = {
            'error_rate': {'value': -1.0}
        }
        # 음수도 처리 가능해야 함 (에러 발생하지 않아야 함)
        result = analyze_deployment_health(metrics)
        assert isinstance(result['health_score'], int)

    def test_missing_band_values(self):
        """밴드 값이 None일 때"""
        metrics = {
            'error_rate': {'value': 2.0, 'band_upper': None, 'band_lower': None}
        }
        # Fallback으로 처리되어야 함
        result = analyze_deployment_health(metrics)
        assert isinstance(result['health_score'], int)

    def test_only_one_metric(self):
        """메트릭이 하나만 있을 때"""
        metrics = {
            'latency': {'value': 500}
        }
        result = analyze_deployment_health(metrics)
        assert 0 <= result['health_score'] <= 100
        assert result['health_state'] in ['healthy', 'warning', 'danger']


# ============================================================================
# Pytest 설정 및 실행
# ============================================================================

if __name__ == "__main__":
    # 터미널에서 직접 실행할 때
    pytest.main([__file__, '-v', '--tb=short'])
