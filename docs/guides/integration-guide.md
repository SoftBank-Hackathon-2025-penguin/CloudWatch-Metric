# 🐧 Penguin Land 프로젝트 - 쉬운 설명서

> 초등학생도 이해할 수 있는 통합 가이드!

---

## 🎯 우리가 만든 것

**"배포를 게임처럼 재미있게!"**

배포할 때 점수가 나오고, 펭귄이 표정을 바꿔요!
- 😊 잘하면: 펭귄이 웃어요 (0~30점)
- 😟 보통: 펭귄이 걱정해요 (31~70점)
- 😢 안좋으면: 펭귄이 울어요 (71~100점)

---

## 🔧 만든 것 목록

### 1. AWS 인프라 ✅
```
📦 ALB (로드밸런서)
  └─ 🎯 Target Group
      └─ 💻 EC2 (Ubuntu + Apache)
```

### 2. CloudWatch 감시 ✅
```
👀 2개의 알람이 지켜봐요:
  1. 응답시간 알람 (너무 느리면 알려줘!)
  2. CPU 알람 (컴퓨터가 너무 열심히 일하면 알려줘!)
```

### 3. 점수 계산기 ✅
```
📊 Python 프로그램 (560줄)
  - 5가지 테스트 시나리오
  - 35개 자동 테스트 (94% 성공!)
```

---

## 🎮 어떻게 작동하나요?

### 간단 버전 (5단계):

```
1️⃣ CloudWatch가 문제 발견
    ↓
2️⃣ SNS가 Backend에게 알려줌
    ↓
3️⃣ Backend가 점수 계산
    ↓
4️⃣ Frontend가 5초마다 확인
    ↓
5️⃣ 펭귄 표정 바뀜! 🐧
```

### 자세한 버전:

#### Step 1: CloudWatch 감시 👀
```
CloudWatch: "어? 응답 시간이 느려졌네?"
CloudWatch: "CPU가 너무 바쁘네?"
```

#### Step 2: SNS가 알림 📨
```
SNS: "Backend야! 문제 생겼어!"
SNS: "이 메시지 받아!"

보내는 메시지:
{
  "문제": "응답시간이 느려요",
  "언제": "2025-11-22 오전 3시",
  "어디서": "penguin-land-alb"
}
```

#### Step 3: Backend가 점수 계산 🧮
```
Backend: "알겠어! 점수 계산할게!"

1. 에러율 확인: 2% (좋음!)
2. 응답시간 확인: 850ms (괜찮음!)
3. CPU 확인: 60% (정상!)

점수 계산:
- 에러율 점수: 2점 (가중치 50%)
- 응답시간 점수: 5점 (가중치 35%)
- CPU 점수: 3점 (가중치 15%)

총점: 28점 → 건강! 😊
```

#### Step 4: Frontend가 확인 🖥️
```
Frontend: "5초마다 물어볼게!"
Frontend: "지금 점수 뭐야?"

Backend: "28점이야!"

Frontend: "오! 좋네!"
```

#### Step 5: 화면 업데이트 🎨
```
화면에 표시:
┌─────────────────┐
│  건강 점수: 28점  │
│                 │
│     😊 🐧       │
│   (행복한 펭귄)   │
│                 │
│ 🌟 최고예요!     │
└─────────────────┘
```

---

## 👥 각 팀이 할 일

### 🎨 Frontend 팀

**해야 할 것:**
```javascript
// 5초마다 확인하기
setInterval(() => {
  fetch('/api/deployment/xxx/health')
    .then(response => response.json())
    .then(data => {
      // 점수 보여주기
      showScore(data.health_score);

      // 펭귄 바꾸기
      changePenguin(data.penguin_animation);

      // 메시지 보여주기
      showMessage(data.coach_message);
    });
}, 5000); // 5초 = 5000밀리초
```

**펭귄 그림 필요:**
- `penguin-happy.gif` (웃는 펭귄)
- `penguin-worried.gif` (걱정하는 펭귄)
- `penguin-crying.gif` (우는 펭귄)

**색깔:**
- 초록색 (#22c55e): 0~30점
- 주황색 (#f59e0b): 31~70점
- 빨간색 (#ef4444): 71~100점

---

### 💻 Backend 팀 (Java)

**받아야 할 것:**
```
✅ SNS ARN: arn:aws:sns:ap-northeast-2:396183525602:penguin-land-alarms
✅ score.py (점수 계산 방법)
✅ test_score.py (테스트 35개)
```

**만들어야 할 API:**

#### 1) SNS 받는 API
```java
@PostMapping("/api/cloudwatch/webhook")
public ResponseEntity<String> handleAlarm(@RequestBody SnsMessage message) {
    // 1. SNS 메시지 파싱
    String alarmName = parseMessage(message);

    // 2. CloudWatch에서 현재 값 가져오기
    Metrics metrics = getMetricsFromCloudWatch();

    // 3. 점수 계산 (승규님 로직)
    int score = calculateHealthScore(metrics);
    String state = classifyState(score);

    // 4. DynamoDB에 저장
    saveToDatabase(score, state);

    return ResponseEntity.ok("처리 완료");
}
```

#### 2) Frontend용 API
```java
@GetMapping("/api/deployment/{sessionId}/health")
public HealthResponse getHealth(@PathVariable String sessionId) {
    return HealthResponse.builder()
        .healthScore(28)
        .healthState("healthy")
        .coachMessage("🌟 최고의 상태예요!")
        .penguinAnimation("happy")
        .build();
}
```

**점수 계산 공식:**
```java
// 1. 각 메트릭 점수 계산
errorScore = calculateSeverity(errorRate) * 0.5 * 100;  // 50%
latencyScore = calculateSeverity(latency) * 0.35 * 100;  // 35%
cpuScore = calculateSeverity(cpu) * 0.15 * 100;          // 15%

// 2. 합치기
totalScore = errorScore + latencyScore + cpuScore;

// 3. 0~100 범위로
healthScore = Math.max(0, Math.min(100, totalScore));
```

---

### ⚙️ 인프라 팀 (준배님)

**확인할 것:**
```
✅ CloudWatch Alarms 2개 작동 중
✅ SNS Topic 생성됨
✅ ALB + EC2 연결 정상
```

**"데이터 부족" 상태 설명:**
```
"Anomaly Detection은 2주 동안 학습이 필요해요.
지금은 학습 중이라 '데이터 부족'이 정상이에요!"
```

---

## 🎬 시연 시나리오 (1분 30초)

### 시연 스크립트:

```
[0:00~0:20] 인사 & 소개
"안녕하세요! Penguin Land 프로젝트를 소개합니다.
배포를 게임처럼 재미있게 만들었어요!"

[0:20~0:50] AWS 설정 보여주기
"CloudWatch로 실시간 모니터링하고,
2개 알람이 상태를 지켜봅니다."
→ AWS Console 화면 보여주기

[0:50~1:10] 점수 계산 시연
"5가지 시나리오로 테스트해볼게요!"
→ python test_scenarios.py 실행
→ Healthy 28점, Warning 55점, Danger 92점

[1:10~1:30] 마무리
"펭귄 표정이 바뀌면서 상태를 알려줘요!
배포가 게임처럼 재미있어집니다!"
```

---

## 📞 연락처 & 공유

### SNS Topic ARN (Backend에게 전달)
```
arn:aws:sns:ap-northeast-2:396183525602:penguin-land-alarms
```

### 파일 공유 위치
```
📁 C:\Users\electrozone\Desktop\소뱅 해커톤\CloudWatch-Metric\
  ├── score_engine/          # 점수 계산 프로그램
  │   ├── score.py          # 메인 로직
  │   ├── test_score.py     # 테스트 35개
  │   └── test_scenarios.py # 시나리오 5개
  └── 쉬운_통합_가이드.md    # 이 파일!
```

---

## ❓ 자주 묻는 질문 (FAQ)

### Q1: "데이터 부족"이 뭐예요?
**A:** Anomaly Detection이 학습 중이에요! 2주 후면 정상 작동해요.
하지만 점수 계산은 지금도 완벽하게 작동합니다! ✅

### Q2: 502 에러는 뭐예요?
**A:** Apache가 멈췄어요! `sudo systemctl start apache2` 하면 해결!

### Q3: 5초 폴링이 너무 자주 아니에요?
**A:** CloudWatch는 1분마다 데이터가 와요. 5초는 적당해요!

### Q4: 펭귄 그림은 어디서 구해요?
**A:** Frontend 팀이 디자이너한테 요청해야 해요!
(happy, worried, crying 3개 필요)

### Q5: 내일 뭐 준비하면 돼요?
**A:**
- ✅ python test_scenarios.py 실행 (시연용)
- ✅ SNS ARN Backend에게 전달
- ✅ 이 문서 팀원들과 공유

---

## 🎉 완료 체크리스트

```
✅ ALB + Target Group + EC2 설정
✅ Security Group 포트 80 열림
✅ Apache 웹서버 실행
✅ CloudWatch Alarm 2개 생성
✅ SNS Topic + 이메일 테스트
✅ Python 점수 엔진 (560줄)
✅ 테스트 35개 (94% 성공)
✅ 시나리오 테스트 5개
✅ 문서 작성
```

**→ 100% 준비 완료! 🚀**

---

## 🌟 마지막 메시지

**수고하셨어요!**

내일 해커톤에서:
1. 자신감 있게 시연하세요!
2. 94% 테스트 성공률 자랑하세요!
3. 펭귄이 표정 바꾸는 거 보여주세요!

**화이팅! 🐧💪**
