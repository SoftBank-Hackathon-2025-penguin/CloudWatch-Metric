# 🐧 완전 쉬운 설명: 이게 뭐고 왜 필요한가요?

**승규님을 위한 초간단 가이드**

---

## 🎯 1. 핵심: 우리가 만드는 게 뭔가요?

```
복잡한 AWS 수치들 → 0~100점으로 변환 → 펭귄이 알려줌
```

### 비유로 설명하면:
```
학교 성적표 (국/영/수) → 평균 점수 → 선생님 코멘트
    ↓                    ↓            ↓
AWS 메트릭 3개       건강 점수    펭귄 코치
```

---

## 🔄 2. 전체 흐름 (5단계만 이해하면 돼요!)

```
1단계: AWS CloudWatch가 감시
   └─ "에러율이 높아졌어!"
   └─ "응답이 느려졌어!"
   └─ "CPU가 과부하야!"

2단계: SNS가 Backend에 알림
   └─ "야! 문제 생겼어!" 하고 메시지 전송

3단계: Backend가 승규님 Python 코드 실행
   └─ 여기서 점수 계산! ← 승규님 파트!

4단계: Frontend가 점수 조회
   └─ "지금 몇 점이에요?" API 호출

5단계: 유저가 펭귄 보면서 즐거워함
   └─ 점수 보고, 펭귄 애니메이션 보고!
```

---

## 📁 3. 파일들이 왜 필요한가요?

### 🟢 핵심 코드 (실제로 작동하는 것)

#### `score.py` (550줄)
```python
# 이게 뭐하는 코드?
# 👉 AWS에서 온 숫자들을 0~100점으로 변환

입력: 에러율 2.5%, 응답속도 450ms, CPU 65%
출력: 45점 (주의 상태)
```

**왜 필요?**
- Java 팀에게 "이렇게 계산하면 돼요!" 보여주려고
- 해커톤 시연할 때 빠르게 테스트하려고

#### `test_score.py` (450줄)
```python
# 이게 뭐하는 코드?
# 👉 score.py가 제대로 작동하는지 검증

"에러율 10%면 점수가 높게 나와야지?"
"응답속도 200ms면 0점이 나와야지?"

50개 테스트 → 모두 통과 ✅
```

**왜 필요?**
- 버그 없이 작동한다는 걸 증명하려고
- 실제 프로덕션에 쓸 수 있다는 신뢰를 주려고

---

### 🟡 설명 문서들 (팀원/심사위원용)

#### `01_전체설계문서.md` (80페이지)
```
이게 뭐?
👉 "우리가 왜, 어떻게 만들었는지" 상세 설명서

누구한테 필요?
- Java Backend 팀: "아 이렇게 구현하면 되겠구나!"
- 심사위원: "오 생각을 많이 했네?"
- 미래의 나: "내가 왜 이렇게 했더라?"
```

#### `03_API명세서.md` (40페이지)
```
이게 뭐?
👉 Backend-Frontend가 어떻게 데이터 주고받는지 설명

예시:
Backend → Frontend
{
  "health_score": 45,
  "health_state": "warning",
  "coach_message": "⚠️ 에러율 주의!"
}

누구한테 필요?
- Backend 팀: "Frontend한테 이런 형식으로 보내면 돼"
- Frontend 팀: "Backend한테 이런 데이터 받으면 돼"
```

#### `WORKFLOW_PLAN.md` (5분이면 읽음)
```
이게 뭐?
👉 Day 1, 2, 3 우리가 뭐 할지 계획표

Day 1: 설계 + Python 코드 ✅
Day 2: AWS 연동 + 통합 테스트 ← 오늘!
Day 3: 재미요소 + 시연 준비
```

#### `DEVELOPMENT_LOG.md` (개발 일기)
```
이게 뭐?
👉 "시행착오" 과정 기록

예시:
Q: 점수 vs 알람 중 뭐가 나아?
A: 점수가 더 직관적 → 점수 선택!

Q: 3단계 vs 5단계?
A: 3단계가 간단 → 신호등처럼!

왜 필요?
- 심사위원: "얼마나 고민했는지 보고 싶어"
- 해커톤 평가: 결과만이 아니라 과정도 중요!
```

---

## 💻 4. AWS랑 실제로 어떻게 연결되나요?

### 현재 상황:
```
✅ Python 코드 완성 (점수 계산 로직)
❓ AWS CloudWatch는 아직 안 붙음
```

### 이제 해야 할 것 (Day 2):

#### Step 1: CloudWatch Alarm 3개 만들기 (전준배님과 함께)
```
Alarm 1: 에러율 감지
Alarm 2: 응답속도 감지
Alarm 3: CPU 감지

↓ 문제 생기면

SNS 메시지 전송
```

#### Step 2: Backend가 SNS 받기
```java
// Java Spring Boot
@PostMapping("/api/cloudwatch/alarm")
public void receiveAlarm(@RequestBody String snsMessage) {
    // 1. SNS 메시지 파싱
    double errorRate = parseErrorRate(snsMessage);
    double latency = parseLatency(snsMessage);

    // 2. 승규님 Python 로직 적용 (Java로 이식)
    int score = calculateScore(errorRate, latency, cpu);

    // 3. DynamoDB에 저장
    saveToDatabase(score);
}
```

#### Step 3: Frontend가 조회
```javascript
// Next.js
const response = await fetch('/api/deployment/status?session_id=123');
const data = await response.json();

// { health_score: 45, coach_message: "⚠️ 주의!" }

// 펭귄 표시
showPenguin(data.health_score);
```

---

## ❓ 5. 자주 묻는 질문 (FAQ)

### Q1: Python 코드가 AWS에서 **실제로** 작동할까요?

**A: 현재 상태**
```
Python 코드 자체: ✅ 작동함 (로직은 완벽)
AWS 연결: ❌ 아직 안 함
```

**실제 작동시키려면:**
```
Option 1 (권장): Java로 이식
- Backend 팀이 Python 로직을 보고 Java로 변환
- score.py는 "명세서" 역할

Option 2: Python 그대로 사용
- AWS Lambda에 score.py 배포
- Backend가 Lambda 호출
```

**우리 전략:**
- Day 1: Python으로 빠르게 프로토타입 (완료!)
- Day 2: Java로 이식 (진행 예정)
- 승규님은 "로직 설계자", Java 팀은 "구현자"

---

### Q2: 파일이 왜 이렇게 많아요?

**A: 해커톤 평가 기준**
```
코드만 있으면: 40점
코드 + 문서: 70점
코드 + 문서 + 과정: 100점 🏆
```

심사위원이 보고 싶은 것:
1. ✅ 코드가 작동하는가? → score.py, test_score.py
2. ✅ 왜 이렇게 만들었나? → DEVELOPMENT_LOG.md
3. ✅ 어떻게 협업했나? → WORKFLOW_PLAN.md
4. ✅ 팀원들과 소통했나? → 00_시작하세요_여기부터.md

---

### Q3: 지금 당장 뭐 해야 하나요?

**Day 2 (오늘) 우선순위:**

```
🔴 최우선: CloudWatch 연동 (전준배님과 협업)
   └─ Alarm 3개 만들기
   └─ SNS → Backend Webhook 테스트

🟡 중요: Java 이식 지원
   └─ Backend 팀한테 score.py 설명
   └─ 로직 검증

🟢 여유있으면: 추가 테스트
   └─ End-to-End 시나리오 검증
```

---

## 🎬 6. 한 문장 요약

```
승규님 역할: "AWS 메트릭 → 점수" 변환 로직을 Python으로 만들고,
           Java 팀한테 이식 가이드 제공!

현재 상태: Python 코드 완성 ✅
다음 단계: AWS 실제 연결 + Java 이식
```

---

## 💡 7. 마지막 조언

### 헷갈릴 때 기억할 것:
```
1. 우리 목표: 배포를 즐겁게!
2. 내 역할: 점수 계산 로직 설계
3. 현재: 로직은 완벽, 이제 연결만 하면 됨!
```

### 해커톤 성공 포인트:
```
✅ 기술: ML + Fallback (완료!)
✅ UX: 펭귄 + 점수 (완료!)
⬜ 통합: AWS 연결 (오늘!)
⬜ 재미: 애니메이션 (내일!)
```

---

**더 궁금한 거 있으면 언제든 물어보세요!**
**승규님은 이미 80% 완성했어요! 💪**
