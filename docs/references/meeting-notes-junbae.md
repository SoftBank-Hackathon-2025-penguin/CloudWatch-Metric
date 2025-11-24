# 💬 내일 준배님과의 대화 스크립트

**복붙해서 그대로 말하면 됩니다!**

---

## 🌅 오전 9시 30분: CloudWatch 설정 시작

### 인사 & 오늘 할 일 설명 (2분)

```
승규: 안녕하세요 준배님! 오늘 CloudWatch Alarm 설정하시죠?

승규: 제가 어제 점수 계산 로직이랑 임계값들을 다 정리해놨어요.
     지금부터 Alarm 3개 만들어야 하는데,
     제가 옆에서 "이 값으로 해주세요" 알려드릴게요!

승규: 시간은 30분~1시간 정도 걸릴 것 같아요.
     준배님이 AWS Console이나 Terraform으로 설정하시면,
     제가 값 확인해드릴게요!
```

---

## 📋 Alarm 1: 에러율 설정

### 준배님한테 알려줄 정보:

```
승규: 첫 번째 Alarm은 "에러율" 감지용이에요.

승규: 이렇게 설정해주시면 돼요:
     ┌─────────────────────────────────┐
     │ Alarm 이름                      │
     │ penguin-land-error-rate         │
     │                                 │
     │ Metric 정보                     │
     │ - Namespace: AWS/ApplicationELB │
     │ - Metric: HTTPCode_Target_5XX_Count │
     │ - Statistic: Sum                │
     │ - Period: 300초 (5분)           │
     │                                 │
     │ Threshold (임계값)              │
     │ - Type: Anomaly Detection 🎯    │
     │ - Comparison: Greater than band │
     │                                 │
     │ (Anomaly Detection 안 되면)     │
     │ - Type: Static                  │
     │ - Threshold: 50 (5XX 에러 50개) │
     │ - Comparison: GreaterThanThreshold │
     │                                 │
     │ Actions (알림)                  │
     │ - SNS Topic: penguin-land-alarms│
     └─────────────────────────────────┘

승규: 에러율이 가장 중요해서 가중치를 50%로 뒀어요.
     Anomaly Detection을 쓰면 CloudWatch가 자동으로
     "평소와 다른 패턴"을 감지해줘서 좋아요!

승규: 혹시 Anomaly Detection 설정이 어려우면
     일단 Static Threshold로 해도 괜찮아요.
     나중에 바꿀 수 있으니까요!
```

#### 준배님이 물어볼 수 있는 질문:

**Q: "왜 Sum이에요? Average는 안 돼요?"**
```
승규: 에러는 "개수"가 중요해서 Sum을 써요!
     Average를 쓰면 에러가 1개 나도, 100개 나도 비슷하게 나올 수 있어요.
     Sum은 실제 에러 개수를 세서, 더 정확해요.
```

**Q: "Period는 왜 300초예요?"**
```
승규: 5분이 적당해서요!
     - 너무 짧으면 (60초): 일시적 에러에도 알림 → 피로도 증가
     - 너무 길면 (600초): 감지가 늦어서 위험
     300초 = 5분이 업계 표준이에요!
```

**Q: "Anomaly Detection Band 폭은?"**
```
승규: CloudWatch 기본값 (2 standard deviations)으로 하면 돼요!
     우리 로직에서 자동으로 처리하게 만들어놨어요.
```

---

## 📋 Alarm 2: 레이턴시 설정

```
승규: 두 번째 Alarm은 "응답 속도" 감지용이에요.

승규: 설정값은:
     ┌─────────────────────────────────┐
     │ Alarm 이름                      │
     │ penguin-land-latency            │
     │                                 │
     │ Metric 정보                     │
     │ - Namespace: AWS/ApplicationELB │
     │ - Metric: TargetResponseTime    │
     │ - Statistic: p90 (90 percentile)│
     │ - Period: 300초                 │
     │                                 │
     │ Threshold                       │
     │ - Type: Anomaly Detection 🎯    │
     │ - Comparison: Greater than band │
     │                                 │
     │ (Anomaly Detection 안 되면)     │
     │ - Type: Static                  │
     │ - Threshold: 0.7 (700ms)        │
     │ - Comparison: GreaterThanThreshold │
     │                                 │
     │ Actions                         │
     │ - SNS Topic: penguin-land-alarms│
     └─────────────────────────────────┘

승규: 레이턴시는 가중치 35%로 두 번째로 중요해요.
     p90을 쓰는 이유는 "상위 10% 느린 요청"을 보기 위해서예요.
     Average를 쓰면 대부분 빠른 요청에 묻혀서 문제를 못 찾아요!
```

#### 준배님이 물어볼 수 있는 질문:

**Q: "p90이 뭐예요?"**
```
승규: 90th percentile이에요!
     100개 요청 중 느린 쪽 10개의 경계값이에요.

     예시:
     - 90개 요청: 200ms (빠름)
     - 10개 요청: 1000ms (느림)
     → Average: 280ms (정상처럼 보임 ❌)
     → p90: 1000ms (문제 감지! ✅)

     일부 사용자가 느리게 경험하는 걸 잡아내려면 p90이 필수예요!
```

**Q: "p99는 안 써요?"**
```
승규: p99는 너무 민감해요.
     해커톤에서는 p90이 적당해요!
     실제 프로덕션에서는 p95나 p99도 같이 보지만,
     지금은 p90으로 충분해요.
```

---

## 📋 Alarm 3: CPU 설정

```
승규: 세 번째는 "CPU 사용률" 이에요.

승규: 설정값:
     ┌─────────────────────────────────┐
     │ Alarm 이름                      │
     │ penguin-land-cpu                │
     │                                 │
     │ Metric 정보                     │
     │ - Namespace: AWS/EC2            │
     │ - Metric: CPUUtilization        │
     │ - Statistic: Average            │
     │ - Period: 300초                 │
     │ - Dimensions:                   │
     │   * InstanceId: [EC2 인스턴스 ID]│
     │   또는                          │
     │   * AutoScalingGroupName: [ASG명]│
     │                                 │
     │ Threshold                       │
     │ - Type: Static (단순 임계값)    │
     │ - Threshold: 80 (80%)           │
     │ - Comparison: GreaterThanThreshold │
     │                                 │
     │ Actions                         │
     │ - SNS Topic: penguin-land-alarms│
     └─────────────────────────────────┘

승규: CPU는 가중치 15%로 제일 낮아요.
     사용자한테는 직접적인 영향이 적지만,
     "오토스케일링 필요하다"는 조기 경고 역할이에요!

승규: CPU는 Anomaly Detection 안 써도 돼요.
     80% 넘으면 무조건 주의가 필요하거든요.
```

#### 준배님이 물어볼 수 있는 질문:

**Q: "Dimensions이 뭐예요?"**
```
승규: "어떤 서버의 CPU를 볼 건지" 지정하는 거예요!

     만약 EC2 인스턴스가 1개면:
     → InstanceId: i-1234567890abcdef

     만약 Auto Scaling Group을 쓰면:
     → AutoScalingGroupName: penguin-land-asg

     준배님 환경에 맞게 설정해주시면 돼요!
```

**Q: "왜 80%예요?"**
```
승규: AWS Best Practice가 80%예요!
     - 80% 미만: 여유로움 (트래픽 급증 대응 가능)
     - 80% 이상: 오토스케일링 고려 필요
     - 95% 이상: 포화 상태 (위험!)

     우리는 80%에서 알림 받아서 조기에 대응하려는 거예요.
```

---

## 📞 Alarm 3개 완성 후: SNS 연결 (10분)

```
승규: Alarm 3개 다 만드셨나요? 고생하셨어요!
     이제 SNS Topic 연결해야 해요.

승규: SNS Topic 이름은 "penguin-land-alarms"로 만들어주세요.

승규: 각 Alarm의 "Actions" 부분에
     이 SNS Topic을 연결하면 돼요!

승규: 그러면 Alarm이 발생할 때마다
     SNS가 Backend로 메시지를 보내줄 거예요.
```

### SNS Subscription 설정:

```
승규: SNS Topic을 만드셨으면,
     이제 "누구한테 알림 보낼지" 설정해야 해요.

승규: Subscription 정보:
     ┌─────────────────────────────────┐
     │ Topic ARN                       │
     │ arn:aws:sns:ap-northeast-2:...:penguin-land-alarms │
     │                                 │
     │ Protocol                        │
     │ HTTPS                           │
     │                                 │
     │ Endpoint                        │
     │ https://your-backend.com/api/cloudwatch/alarm │
     │                                 │
     │ (또는 이메일로 테스트)          │
     │ Protocol: Email                 │
     │ Endpoint: your-email@example.com│
     └─────────────────────────────────┘

승규: Backend 팀한테 Endpoint URL 물어보면 돼요!
     아직 Backend가 준비 안 됐으면,
     일단 이메일로 받아서 테스트할 수 있어요.
```

---

## 🧪 설정 완료 후: 테스트 (15분)

```
승규: 설정 다 끝났으면, 제대로 작동하는지 테스트해볼까요?

승규: AWS CLI로 Alarm을 수동으로 발동시킬게요!
```

### 터미널에서 실행:

```bash
# Alarm 1 테스트
승규: (타이핑하면서) "이 명령어로 에러율 Alarm을 강제로 발동시킬게요"

aws cloudwatch set-alarm-state \
  --alarm-name penguin-land-error-rate \
  --state-value ALARM \
  --state-reason "Testing for hackathon demo"

승규: "이제 SNS로 메시지가 갔을 거예요. 확인해볼까요?"

# SNS 메시지 확인 (이메일 설정했으면)
승규: "준배님 이메일 확인해보세요! SNS 메시지 왔나요?"
```

### 예상 SNS 메시지:

```
승규: "이런 식으로 메시지가 왔을 거예요"

승규: (화면 보여주면서)
     ┌─────────────────────────────────┐
     │ Subject:                        │
     │ ALARM: penguin-land-error-rate  │
     │                                 │
     │ Message:                        │
     │ {                               │
     │   "AlarmName": "penguin-land-error-rate", │
     │   "NewStateValue": "ALARM",     │
     │   "StateChangeTime": "2025-11-21T10:30:00Z" │
     │ }                               │
     └─────────────────────────────────┘

승규: "이 메시지를 Backend가 받아서,
     제가 만든 점수 계산 로직을 실행하면 돼요!"
```

---

## 🔍 문제 해결

### 준배님: "Alarm이 안 만들어져요!"

```
승규: 어떤 에러가 나나요?

[에러 1: Metric을 찾을 수 없음]
승규: 아, ALB나 EC2가 아직 안 만들어진 거 같아요.
     일단 Alarm은 만들어두고,
     나중에 실제 리소스 생기면 자동으로 연결될 거예요!
     지금은 테스트용으로 Metric Namespace만 맞게 설정해두세요.

[에러 2: Anomaly Detection을 설정할 수 없음]
승규: 괜찮아요! Static Threshold로 바꾸면 돼요.
     제 로직은 두 가지 다 지원하거든요.
     Anomaly Detection은 "있으면 좋고, 없어도 작동"이에요!

[에러 3: SNS Topic 권한 에러]
승규: CloudWatch Alarm이 SNS로 메시지를 보낼 권한이 없는 거예요.a
     SNS Topic의 "Access Policy"에서
     cloudwatch.amazonaws.com을 추가해주세요!
```

---

## ✅ 완료 체크리스트

```
승규: "이제 다 끝났나요? 확인해볼까요?"

□ Alarm 3개 생성 완료
  - penguin-land-error-rate ✅
  - penguin-land-latency ✅
  - penguin-land-cpu ✅

□ 각 Alarm 설정 확인
  - Metric 이름 맞음 ✅
  - Period 300초 ✅
  - Threshold 설정됨 ✅

□ SNS Topic 생성
  - penguin-land-alarms ✅

□ Alarm → SNS 연결
  - 각 Alarm의 Actions에 SNS 추가됨 ✅

□ SNS Subscription 설정
  - Backend Endpoint 또는 Email 등록 ✅

□ 테스트 알림 발송 성공
  - 수동으로 Alarm 발동 ✅
  - SNS 메시지 수신 확인 ✅

승규: "전부 체크됐으면 완료예요! 고생하셨어요! 🎉"
```

---

## 🕐 다음 스텝 안내

```
승규: "CloudWatch 설정은 끝났어요!
     이제 Backend팀이랑 연동 테스트 해야 해요."

승규: "점심 먹고 오후 3시쯤에
     Backend 팀이랑 같이 통합 테스트 하면 될 것 같아요!"

승규: "그때는 제가 '예상 점수'를 미리 계산해서 알려드릴게요.
     실제 점수랑 비교해서 맞는지 확인하면 돼요!"
```

---

## 💡 준배님한테 공유할 문서

```
승규: "준배님, 지금 설정하신 내용이
     제가 어제 만든 '03_API명세서.md'에 다 정리되어 있어요!"

승규: "나중에 다시 보실 일 있으면 그 문서 참고하세요!
     CloudWatch 섹션에 모든 설정값이 적혀있어요."

승규: "그리고 '지금당장테스트하기.md'에
     수동으로 Alarm 테스트하는 방법도 있으니
     필요하면 보세요!"
```

---

## 🎯 핵심 요약

### 승규님이 준배님한테 알려줄 것:

```
1. Alarm 3개 설정값
   ✅ 정확한 Metric 이름
   ✅ 임계값 (Threshold)
   ✅ Period, Statistic

2. 왜 이 값을 선택했는지
   ✅ 가중치 (50%, 35%, 15%)
   ✅ 임계값 근거
   ✅ Anomaly Detection vs Static

3. 테스트 방법
   ✅ 수동 Alarm 발동
   ✅ SNS 메시지 확인
   ✅ 예상 점수 계산
```

### 승규님이 할 일:

```
✅ 옆에서 설정 과정 보면서 값 확인
✅ 질문 답변
✅ 테스트 도와주기
✅ 문서 공유

→ 직접 설정은 준배님이 함!
→ 승규님은 "컨설턴트" 역할!
```

---

**이 스크립트 그대로 읽으면서 진행하면 돼요!** 📝
**준비 끝!** 🚀
