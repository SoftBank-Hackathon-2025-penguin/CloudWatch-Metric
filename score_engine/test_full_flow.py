import json
from score import analyze_deployment_health

# Step 1: SNS 메시지 시뮬레이션 (CloudWatch → SNS)
sns_message = {
    "Type": "Notification",
    "Message": json.dumps({
        "AlarmName": "penguin-land-latency-anomaly",
        "NewStateValue": "ALARM",
        "NewStateReason": "Threshold Crossed",
        "Trigger": {
            "MetricName": "TargetResponseTime",
            "Dimensions": [
                {"name": "LoadBalancer", "value": "app/penguin-land-alb/77a716d3813b8deb"}
            ]
        }
    })
}

print("=" * 70)
print("전체 플로우 시뮬레이션")
print("=" * 70)

# Step 2: Backend가 SNS 메시지 파싱
alarm_data = json.loads(sns_message["Message"])
print(f"\n[1] CloudWatch Alarm 수신")
print(f"    Alarm: {alarm_data['AlarmName']}")
print(f"    상태: {alarm_data['NewStateValue']}")

# Step 3: CloudWatch에서 실제 메트릭 값 가져오기 (시뮬레이션)
# 실제로는 Backend가 CloudWatch API 호출
metrics = {
    'error_rate': {'value': 2.0},
    'latency': {'value': 850.0},  # Alarm 발생한 값
    'cpu': {'value': 60}
}

print(f"\n[2] 메트릭 데이터 수집")
print(f"    Error Rate: {metrics['error_rate']['value']}%")
print(f"    Latency: {metrics['latency']['value']}ms")
print(f"    CPU: {metrics['cpu']['value']}%")

# Step 4: 점수 계산 (승규님 로직!)
result = analyze_deployment_health(metrics)

print(f"\n[3] 점수 엔진 실행")
print(f"    건강 점수: {result['health_score']}점")
print(f"    상태: {result['health_state']}")
print(f"    펭귄: {result['penguin_animation']}")
print(f"    메시지: {result['coach_message']}")

# Step 5: Frontend로 전달할 JSON
response = {
    "session_id": "test-session-001",
    "timestamp": "2025-11-22T03:00:00Z",
    "health_score": result['health_score'],
    "health_state": result['health_state'],
    "coach_message": result['coach_message'],
    "penguin_animation": result['penguin_animation']
}

print(f"\n[4] Frontend로 응답")
print(json.dumps(response, indent=2, ensure_ascii=False))

print("\n" + "=" * 70)
print("✅ 전체 플로우 테스트 완료!")
print("=" * 70)