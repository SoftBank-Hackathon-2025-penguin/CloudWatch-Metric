# 📋 내일 필요한 것 (A4 1장 치트시트)

**출력해서 책상에 놓고 보세요!**

---

## ⚡ CloudWatch Alarm 설정값 (외워두기!)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alarm 1: penguin-land-error-rate
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric: HTTPCode_Target_5XX_Count (Sum, 5분)
Threshold: Anomaly Detection (또는 Static 50개)
가중치: 50% (가장 중요!)
이유: 에러는 사용자한테 치명적

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alarm 2: penguin-land-latency
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric: TargetResponseTime (p90, 5분)
Threshold: Anomaly Detection (또는 Static 0.7초)
가중치: 35%
이유: 느리면 짜증나지만 일단 작동은 함

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Alarm 3: penguin-land-cpu
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Metric: CPUUtilization (Average, 5분)
Threshold: Static 80%
가중치: 15%
이유: 조기 경고용 (오토스케일링 신호)
```

---

## 📊 점수 계산 빠른 참조

```
점수 구간:
0-30점   = 건강 (🟢) = 펭귄 😊
31-70점  = 주의 (🟡) = 펭귄 😟
71-100점 = 위험 (🔴) = 펭귄 😭

임계값 (Fallback):
에러율: 1% / 5% / 10%
레이턴시: 300ms / 700ms / 1500ms
CPU: 50% / 80% / 95%
```

---

## 🧮 빠른 점수 계산 (암산용)

```
예시 1: 에러율만 높은 경우
━━━━━━━━━━━━━━━━━━━━━━━━━━
error_rate: 5% (severity 0.5)
latency: 250ms (severity 0.0)
cpu: 40% (severity 0.0)

계산:
0.5 × 50% = 25점 → 25점 (healthy)

━━━━━━━━━━━━━━━━━━━━━━━━━━
예시 2: 모두 warning 구간
━━━━━━━━━━━━━━━━━━━━━━━━━━
error_rate: 3% (severity ~0.4)
latency: 500ms (severity ~0.3)
cpu: 65% (severity ~0.3)

계산:
(0.4 × 50%) + (0.3 × 35%) + (0.3 × 15%)
= 20 + 10.5 + 4.5 = 35점 (warning)

━━━━━━━━━━━━━━━━━━━━━━━━━━
예시 3: 위험 상태
━━━━━━━━━━━━━━━━━━━━━━━━━━
error_rate: 10% (severity 0.8)
latency: 1500ms (severity 0.8)
cpu: 95% (severity 1.0)

계산:
(0.8 × 50%) + (0.8 × 35%) + (1.0 × 15%)
= 40 + 28 + 15 = 83점 (danger)
```

---

## 💬 자주 나올 질문 & 답변

```
Q: "왜 Anomaly Detection을 써요?"
A: "평소 패턴을 학습해서 '이상한 것'을 자동으로 감지해줘요.
   없어도 Fallback 임계값으로 작동하니 괜찮아요!"

Q: "p90이 뭐예요?"
A: "90th percentile이에요. 느린 쪽 10% 요청을 보는 거예요.
   Average보다 실제 사용자 경험을 잘 반영해요!"

Q: "왜 300초(5분)예요?"
A: "업계 표준이에요! 너무 짧으면 노이즈, 너무 길면 늦어요."

Q: "가중치는 왜 50/35/15예요?"
A: "에러가 가장 치명적이고, 레이턴시가 그 다음,
   CPU는 조기 경고용이라 낮게 뒀어요!"

Q: "이 점수 계산 맞아요?"
A: "네! Python으로 50개 테스트 다 통과했어요!"
```

---

## ⏰ 내일 일정 (한눈에)

```
09:00 - 09:30  킥오프 (Python 로직 시연)
09:30 - 11:00  CloudWatch Alarm 설정 (준배님)
11:00 - 12:00  Backend 코드 검토

[점심]

13:00 - 14:00  문서 정리 & 시나리오 준비
14:00 - 15:00  DynamoDB 확인
15:00 - 17:00  통합 테스트 (가장 중요!)
17:00 - 18:00  버그 수정

목표: 한 번이라도 전체 흐름 성공!
```

---

## ✅ 내일 성공 체크리스트

```
오전:
□ Alarm 3개 생성 확인
□ SNS 연결 확인
□ 테스트 메시지 수신 확인
□ Backend Java 코드 = Python 로직 검증

오후:
□ 수동 Alarm 발동 → 점수 계산
□ 예상 점수 vs 실제 점수 비교
□ DynamoDB 저장 확인
□ Frontend 펭귄 변경 확인

최소 목표:
✅ 한 번이라도 전체 흐름 성공!
```

---

## 🎯 준배님한테 알려줄 핵심 (30초 버전)

```
"Alarm 3개 만들어야 해요:

1. 에러율 - HTTPCode_Target_5XX_Count
2. 레이턴시 - TargetResponseTime (p90)
3. CPU - CPUUtilization

전부 5분 단위로, Anomaly Detection 쓰면 좋고,
안 되면 Static으로 해도 돼요!

SNS로 Backend한테 알림 가게 연결하면 끝이에요!"
```

---

## 🚨 긴급 연락처

```
준배님: [전화번호]
Backend팀: [전화번호]
Frontend팀: [전화번호]

막히면 바로 연락!
```

---

## 📦 챙겨갈 것

```
□ 노트북 + 충전기
□ 이 치트시트 (출력)
□ 03_API명세서.md (출력 or 태블릿)
□ 계산기
□ 물 + 간식 + 카페인
```

---

## 🎉 마음가짐

```
✅ 승규님은 이미 80% 완성!
✅ 내일은 "연결"만 하면 됨!
✅ 모르는 거 물어보면 OK!
✅ 실수해도 괜찮아!
✅ 한 번만 성공하면 시연 가능!

→ 자신감 갖고 가세요! 💪
```

---

## 🔥 급할 때 Python 빠른 테스트

```bash
# 터미널에서
cd score_engine
python

# Python에서
from score import analyze_deployment_health

# 빠른 테스트
metrics = {
    'error_rate': {'value': 5.0},
    'latency': {'value': 700},
    'cpu': {'value': 80}
}

result = analyze_deployment_health(metrics)
print(f"{result['health_score']}점 - {result['health_state']}")

# Ctrl+D로 종료
```

---

**이 종이 하나면 내일 충분해요!** 📄
**화이팅!** 🚀
