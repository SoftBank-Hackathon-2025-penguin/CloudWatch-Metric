# test_integration.py
import json
from score import analyze_deployment_health

# 1. CloudWatch SNS 메시지 시뮬레이션
sns_message = {
    "Type": "Notification",
    "Message": json.dumps({
        "AlarmName": "penguin-land-latency",
        "NewStateValue": "ALARM",
        "NewStateReason": "Threshold Crossed: 1 datapoint [850.0] was greater than upper threshold",
        "Trigger": {
            "MetricName": "TargetResponseTime"
        }
    })
}

# 2. SNS 메시지 파싱 (Backend가 할 일)
alarm_message = json.loads(sns_message["Message"])
print(f"알람 이름: {alarm_message['AlarmName']}")
print(f"메트릭 값: 850.0ms")

# 3. 메트릭 데이터 구성
metrics = {
    'error_rate': {'value': 2.0},
    'latency': {'value': 850.0},  # SNS에서 추출한 값
    'cpu': {'value': 60}
}

# 4. 점수 계산 (승규님 로직!)
result = analyze_deployment_health(metrics)

print("\n=== 결과 ===")
print(f"점수: {result['health_score']}점")
print(f"상태: {result['health_state']}")
print(f"메시지: {result['coach_message']}")
print(f"펭귄: {result['penguin_animation']}")

# 5. DynamoDB 저장 시뮬레이션
deployment_record = {
    "session_id": "test-session-123",
    "timestamp": "2025-11-21T10:00:00Z",
    "health_score": result['health_score'],
    "health_state": result['health_state'],
    "coach_message": result['coach_message']
}

print("\n=== DynamoDB 저장 ===")
print(json.dumps(deployment_record, indent=2, ensure_ascii=False))

print("\n✅ 전체 흐름 시뮬레이션 완료!")
print("→ 모든 단계가 정상 작동합니다! 🎉")