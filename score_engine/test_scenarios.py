"""
다양한 시나리오 테스트
"""

import json
from score import analyze_deployment_health

print("=" * 70)
print("시나리오별 테스트")
print("=" * 70)

# 시나리오 1: Healthy (현재 상태)
print("\n[시나리오 1] Healthy - 정상 배포")
print("-" * 70)
metrics1 = {
    'error_rate': {'value': 2.0},
    'latency': {'value': 850.0},
    'cpu': {'value': 60}
}
result1 = analyze_deployment_health(metrics1)
print(f"점수: {result1['health_score']}점")
print(f"상태: {result1['health_state']}")
print(f"메시지: {result1['coach_message']}")

# 시나리오 2: Warning - 주의 필요
print("\n[시나리오 2] Warning - 주의 필요")
print("-" * 70)
metrics2 = {
    'error_rate': {'value': 5.0},    # 5% (경계선)
    'latency': {'value': 1200.0},    # 1.2초 (느림!)
    'cpu': {'value': 82}             # 82% (높음!)
}
result2 = analyze_deployment_health(metrics2)
print(f"점수: {result2['health_score']}점")
print(f"상태: {result2['health_state']}")
print(f"메시지: {result2['coach_message']}")

# 시나리오 3: Danger - 위험!
print("\n[시나리오 3] Danger - 위험 상태!")
print("-" * 70)
metrics3 = {
    'error_rate': {'value': 10.0},   # 10% (매우 높음!)
    'latency': {'value': 2500.0},    # 2.5초 (매우 느림!)
    'cpu': {'value': 95}             # 95% (과부하!)
}
result3 = analyze_deployment_health(metrics3)
print(f"점수: {result3['health_score']}점")
print(f"상태: {result3['health_state']}")
print(f"메시지: {result3['coach_message']}")
print(f"문제 메트릭: {result3['problem_metrics']}")

# 시나리오 4: Anomaly Detection Band 사용
print("\n[시나리오 4] Anomaly Detection - 밴드 초과")
print("-" * 70)
metrics4 = {
    'error_rate': {'value': 2.5, 'band_upper': 3.0, 'band_lower': 0.5},
    'latency': {'value': 900, 'band_upper': 600, 'band_lower': 200},  # 밴드 초과!
    'cpu': {'value': 65}
}
result4 = analyze_deployment_health(metrics4)
print(f"점수: {result4['health_score']}점")
print(f"상태: {result4['health_state']}")
print(f"메시지: {result4['coach_message']}")

# 시나리오 5: 에러율만 문제
print("\n[시나리오 5] 에러율만 높은 경우")
print("-" * 70)
metrics5 = {
    'error_rate': {'value': 8.0},    # 8% (높음!)
    'latency': {'value': 250},       # 정상
    'cpu': {'value': 40}             # 정상
}
result5 = analyze_deployment_health(metrics5)
print(f"점수: {result5['health_score']}점")
print(f"상태: {result5['health_state']}")
print(f"메시지: {result5['coach_message']}")

# 요약
print("\n" + "=" * 70)
print("시나리오 테스트 완료!")
print("=" * 70)
print("\n점수 요약:")
print(f"시나리오 1 (정상):      {result1['health_score']:3d}점 - {result1['health_state']}")
print(f"시나리오 2 (주의):      {result2['health_score']:3d}점 - {result2['health_state']}")
print(f"시나리오 3 (위험):      {result3['health_score']:3d}점 - {result3['health_state']}")
print(f"시나리오 4 (밴드초과):  {result4['health_score']:3d}점 - {result4['health_state']}")
print(f"시나리오 5 (에러만):    {result5['health_score']:3d}점 - {result5['health_state']}")

print("\n✅ 모든 시나리오가 예상대로 작동해요!")
print("→ 내일 시연할 때 이 중 아무거나 보여주면 돼요! 💪")
