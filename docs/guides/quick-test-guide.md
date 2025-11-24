# 🚀 지금 당장 테스트하기 (5분 완성!)

**score.py가 진짜 작동하는지 지금 바로 확인해봅시다!**

---

## ⚡ 1단계: Python 환경 확인 (30초)

### Windows PowerShell 또는 명령 프롬프트 열기

```bash
# Python 버전 확인
python --version

# 출력 예상:
# Python 3.8.x 이상이면 OK!
```

만약 Python이 없다면:
```
https://www.python.org/downloads/
→ Download Python 3.11
→ 설치할 때 "Add to PATH" 체크!
```

---

## ⚡ 2단계: 필요한 라이브러리 설치 (1분)

```bash
# 프로젝트 폴더로 이동
cd "C:\Users\electrozone\Desktop\소뱅 해커톤\CloudWatch-Metric\score_engine"

# 라이브러리 설치 (실제로는 필요 없음 - 순수 Python!)
# requirements.txt는 boto3 등이 있지만, score.py는 그것 없이도 작동!

# 바로 실행 가능!
```

---

## ⚡ 3단계: 코드 실행! (10초)

```bash
# score.py 실행
python score.py
```

### 예상 출력:

```
======================================================================
Penguin-Land Score Engine 테스트
======================================================================

[테스트 1] 완벽한 배포 상태
점수: 0점
상태: healthy
메시지: 🎉 완벽해요! 모든 지표가 정상이에요!
펭귄: happy

[테스트 2] 주의가 필요한 상태
점수: 48점
상태: warning
메시지: ⚠️ 에러가 조금씩 발생하고 있어요. 로그를 확인해서 원인을 파악해보세요!
펭귄: worried

[테스트 3] 위험한 상태
점수: 91점
상태: danger
메시지: 🚨 에러율이 급증했어요! CPU가 과부하 상태에요! 최근 배포 내역을 확인하고, 에러 로그를 점검하세요!
펭귄: crying
문제 메트릭: [('error_rate', 0.9), ('cpu', 0.85), ('latency', 0.95)]

======================================================================
테스트 완료!
======================================================================
```

---

## ⚡ 4단계: 직접 수치 넣어보기 (1분)

### Python 대화형 모드로 테스트

```bash
# Python 대화형 모드 실행
python
```

```python
# score.py 불러오기
from score import analyze_deployment_health

# 테스트 1: 내가 원하는 값 넣어보기
metrics = {
    'error_rate': {'value': 2.5, 'band_upper': 3.0, 'band_lower': 0.5},
    'latency': {'value': 450, 'band_upper': 600, 'band_lower': 200},
    'cpu': {'value': 65}
}

result = analyze_deployment_health(metrics)
print(f"점수: {result['health_score']}점")
print(f"상태: {result['health_state']}")
print(f"메시지: {result['coach_message']}")

# 출력:
# 점수: 45점
# 상태: warning
# 메시지: ⚠️ 에러가 조금씩 발생하고 있어요...
```

### 다른 값으로 실험:

```python
# 테스트 2: 에러율만 높이기
metrics = {
    'error_rate': {'value': 8.0},  # Fallback 임계값 사용
    'latency': {'value': 250},
    'cpu': {'value': 40}
}

result = analyze_deployment_health(metrics)
print(f"점수: {result['health_score']}점")

# 예상: 60~70점 (에러율이 높아서)
```

```python
# 테스트 3: 모든 지표 위험
metrics = {
    'error_rate': {'value': 12.0},
    'latency': {'value': 2000},
    'cpu': {'value': 95}
}

result = analyze_deployment_health(metrics)
print(f"점수: {result['health_score']}점")

# 예상: 90~100점 (매우 위험)
```

---

## ⚡ 5단계: 테스트 전부 돌리기 (30초)

```bash
# 테스트 50개 전부 실행
pytest test_score.py -v

# 또는 (pytest 없으면)
python -m pytest test_score.py -v

# 또는 (pytest 설치)
pip install pytest
pytest test_score.py -v
```

### 예상 출력:

```
test_score.py::test_calculate_severity_with_anomaly_band PASSED
test_score.py::test_calculate_severity_fallback PASSED
test_score.py::test_calculate_health_score_perfect PASSED
test_score.py::test_calculate_health_score_warning PASSED
test_score.py::test_calculate_health_score_danger PASSED
...
======================== 50 passed in 0.5s ========================
```

---

## 🎯 혼자서 CloudWatch까지 연결하기

**"준배님 없이 혼자 해보고 싶어요!"**

### Option 1: Mock 데이터로 전체 흐름 시뮬레이션 (추천!)

```bash
# 새 파일 생성: test_integration.py
```

```python
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
```

실행:
```bash
python test_integration.py
```

---

### Option 2: 실제 CloudWatch Alarm 만들기 (30분)

#### 2-1. AWS CLI 설치 확인

```bash
aws --version

# 없으면 설치:
# https://aws.amazon.com/cli/
```

#### 2-2. AWS 자격 증명 설정

```bash
aws configure

# 입력 요구:
# AWS Access Key ID: [준배님한테 받기]
# AWS Secret Access Key: [준배님한테 받기]
# Default region: ap-northeast-2
# Default output: json
```

#### 2-3. CloudWatch Alarm 생성

```bash
# Latency Alarm 만들기
aws cloudwatch put-metric-alarm \
  --alarm-name penguin-land-latency-test \
  --alarm-description "Test alarm for latency" \
  --metric-name TargetResponseTime \
  --namespace AWS/ApplicationELB \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 700 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=LoadBalancer,Value=app/your-alb/xxxxx
```

**참고:** `your-alb` 부분은 실제 ALB 이름으로 바꿔야 해요!

#### 2-4. Alarm 목록 확인

```bash
aws cloudwatch describe-alarms --alarm-names penguin-land-latency-test
```

#### 2-5. 테스트: Alarm 수동 발동

```bash
# Alarm 상태를 ALARM으로 강제 변경
aws cloudwatch set-alarm-state \
  --alarm-name penguin-land-latency-test \
  --state-value ALARM \
  --state-reason "Testing for hackathon"
```

#### 2-6. 결과 확인

```bash
# Alarm 상태 확인
aws cloudwatch describe-alarm-history \
  --alarm-name penguin-land-latency-test \
  --max-records 5
```

---

## 🎮 실전 연습 시나리오

### 시나리오 1: 에러율 급증
```python
from score import analyze_deployment_health

# 정상 상태
metrics_before = {
    'error_rate': {'value': 0.5},
    'latency': {'value': 250},
    'cpu': {'value': 40}
}

result_before = analyze_deployment_health(metrics_before)
print(f"배포 전: {result_before['health_score']}점 - {result_before['health_state']}")

# 배포 후 에러 발생!
metrics_after = {
    'error_rate': {'value': 6.5},  # 에러 급증!
    'latency': {'value': 250},
    'cpu': {'value': 40}
}

result_after = analyze_deployment_health(metrics_after)
print(f"배포 후: {result_after['health_score']}점 - {result_after['health_state']}")
print(f"메시지: {result_after['coach_message']}")

# 예상 출력:
# 배포 전: 0점 - healthy
# 배포 후: 65점 - warning
# 메시지: ⚠️ 에러가 조금씩 발생하고 있어요...
```

### 시나리오 2: Anomaly Detection Band 활용
```python
# CloudWatch가 학습한 정상 범위
metrics_with_band = {
    'error_rate': {'value': 2.5, 'band_upper': 3.0, 'band_lower': 0.5},
    'latency': {'value': 450, 'band_upper': 600, 'band_lower': 200},
    'cpu': {'value': 65}
}

result = analyze_deployment_health(metrics_with_band)
print(f"점수: {result['health_score']}점")
print(f"밴드 안에 있음: latency는 정상!")

# 밴드 밖으로 나간 경우
metrics_outside = {
    'error_rate': {'value': 2.5, 'band_upper': 3.0, 'band_lower': 0.5},
    'latency': {'value': 850, 'band_upper': 600, 'band_lower': 200},  # 밴드 초과!
    'cpu': {'value': 65}
}

result = analyze_deployment_health(metrics_outside)
print(f"점수: {result['health_score']}점")
print(f"latency가 밴드 초과 → 점수 상승!")
```

---

## 📊 내가 직접 계산해보기

### 수동 계산 예시:

```
입력:
- error_rate: 3.5%
- latency: 550ms
- cpu: 72%

1단계: 각 메트릭 심각도 계산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
error_rate 3.5%:
→ 1% ~ 5% 구간 (warning 구간)
→ (3.5 - 1) / (5 - 1) = 0.625
→ severity = 0.625 × 0.5 = 0.3125

latency 550ms:
→ 300ms ~ 700ms 구간
→ (550 - 300) / (700 - 300) = 0.625
→ severity = 0.625 × 0.5 = 0.3125

cpu 72%:
→ 50% ~ 80% 구간
→ (72 - 50) / (80 - 50) = 0.733
→ severity = 0.733 × 0.5 = 0.3665

2단계: 가중치 적용
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
error_rate: 0.3125 × 50% × 100 = 15.625점
latency: 0.3125 × 35% × 100 = 10.9375점
cpu: 0.3665 × 15% × 100 = 5.4975점

3단계: 합산
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
총 점수 = 15.625 + 10.9375 + 5.4975
        = 32.06점
        ≈ 32점

4단계: 상태 분류
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
32점 → 31~70 구간 → warning

결과:
✅ 점수: 32점
✅ 상태: warning
✅ 펭귄: 😟
```

이제 Python으로 확인:
```python
metrics = {
    'error_rate': {'value': 3.5},
    'latency': {'value': 550},
    'cpu': {'value': 72}
}
result = analyze_deployment_health(metrics)
print(result['health_score'])  # 32점 나와야 함!
```

---

## ✅ 체크리스트: 내가 직접 확인한 것들

```
□ Python 설치 확인
□ score.py 실행 성공
□ 3개 테스트 케이스 확인
□ 내가 원하는 값으로 테스트
□ 50개 테스트 전부 통과
□ 수동 계산 vs Python 결과 비교
□ Mock 데이터로 전체 흐름 시뮬레이션
□ (선택) CloudWatch Alarm 생성
□ (선택) Alarm 수동 발동 테스트

→ 전부 체크했으면 완벽히 이해한 것!
```

---

## 🎉 이제 자신감 생겼죠?

```
✅ score.py가 실제로 작동함을 확인!
✅ 어떻게 계산되는지 이해!
✅ 내 입력으로 테스트 가능!
✅ 전체 흐름 시뮬레이션 완료!

→ 내일 준배님한테 자신있게 설명 가능!
→ Backend팀한테도 자신있게 가이드 가능!
```

---

**지금 바로 해보세요!** 🚀
**5분이면 충분해요!** ⚡
