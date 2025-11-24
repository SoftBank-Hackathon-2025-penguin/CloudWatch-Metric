# 🐧 팀원 공유용 - 승규님 파트 요약

## 📌 강종연님 질문 답변

### Q1: 파이썬 프레임워크 쪽 뭐 쓰시는지?

**답변**:
```
프레임워크 사용 안 합니다! (Flask/FastAPI 불필요)

이유:
- Python 코드는 "참조용"입니다
- 실제 서비스는 Java Spring Boot로 구현
- 순수 Python 함수로 구현 → Java로 쉽게 이식 가능

의존성:
- boto3 (CloudWatch 테스트용만)
- pytest (테스트 자동화)
- python-dotenv (환경변수)

설치:
pip install boto3 pytest python-dotenv
```

### Q2: 점수 시스템 어떤 걸로 만들지?

**답변**:
```
✅ 이미 완성했습니다!

핵심 로직:
1. 0~100점 점수 시스템
   - 0점 = 완벽
   - 30점 이하 = 건강
   - 31~70점 = 주의
   - 71~100점 = 위험

2. 점수 계산 방식
   score = (에러율 × 50%) + (레이턴시 × 35%) + (CPU × 15%)

3. Anomaly Detection + Fallback 임계값
   - ML 밴드 있으면 사용
   - 없으면 하드코딩 임계값 사용

파일 위치:
/score_engine/score.py
```

---

## 🎯 각 팀원별로 필요한 정보

### 👨‍💻 전준배님 (CloudWatch 구축)

#### 필요한 CloudWatch Alarm 설정

**1. 에러율 알람**
```yaml
AlarmName: penguin-land-error-rate-anomaly
MetricName: HTTPCode_Target_5XX_Count
Namespace: AWS/ApplicationELB
Statistic: Sum
Period: 300 (5분)
Threshold: ANOMALY_DETECTION_BAND
TreatMissingData: notBreaching
```

**2. 레이턴시 알람**
```yaml
AlarmName: penguin-land-latency-anomaly
MetricName: TargetResponseTime
Namespace: AWS/ApplicationELB
Statistic: p90
Period: 300
Threshold: ANOMALY_DETECTION_BAND
```

**3. CPU 알람**
```yaml
AlarmName: penguin-land-cpu-anomaly
MetricName: CPUUtilization
Namespace: AWS/EC2
Statistic: Average
Period: 300
Threshold: ANOMALY_DETECTION_BAND
```

#### SNS Topic 설정
```
Topic Name: penguin-land-alarms
Subscription: HTTPS → Backend Webhook
Endpoint: https://your-backend.com/api/cloudwatch/alarm
```

#### 질문 리스트
- [ ] ALB를 사용하나요? (추천!)
- [ ] Backend Webhook URL: `/api/cloudwatch/alarm` 이거로 할까요?
- [ ] Lambda 거칠까요, 직접 연결할까요? (직접 연결 추천!)

---

### 🎨 강종연님 (Frontend)

#### API 엔드포인트
```http
GET /api/deployment/status?session_id=xxx

Response:
{
  "health_score": 45,
  "health_state": "warning",
  "coach_message": "⚠️ 에러가 조금씩 발생하고 있어요!",
  "penguin_animation": "worried",
  "metrics": {...}
}
```

#### 폴링 로직 (3~5초마다)
```javascript
useEffect(() => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/deployment/status?session_id=${sessionId}`);
    const data = await response.json();

    setHealthScore(data.health_score);
    setPenguinState(data.penguin_animation);
    setMessage(data.coach_message);
  }, 3000);

  return () => clearInterval(interval);
}, [sessionId]);
```

#### 필요한 NPM 패키지
```bash
npm install lottie-react        # 펭귄 애니메이션
npm install canvas-confetti     # 컨페티 효과
npm install use-sound          # 사운드 효과
npm install framer-motion      # 애니메이션
```

#### 펭귄 상태별 스타일
```javascript
const styles = {
  healthy: {
    bg: '#10b981',      // 초록
    emoji: '😊',
    animation: 'happy'
  },
  warning: {
    bg: '#f59e0b',      // 노랑
    emoji: '😐',
    animation: 'worried'
  },
  danger: {
    bg: '#ef4444',      // 빨강
    emoji: '😭',
    animation: 'crying'
  }
}
```

#### 시뮬레이션 버튼 (데모용)
```javascript
const simulateDanger = async () => {
  // Mock 데이터로 즉시 표시 (Backend 호출 불필요!)
  setHealthScore(95);
  setPenguinState('crying');
  setMessage('🚨 위험! 에러율이 급증했어요!');

  setTimeout(() => {
    setHealthScore(15);
    setPenguinState('happy');
  }, 10000);
}
```

---

### ⚙️ 장윤호님 (Terraform)

#### Terraform으로 생성 필요
```hcl
# CloudWatch Alarm (3개)
resource "aws_cloudwatch_metric_alarm" "error_rate" { ... }
resource "aws_cloudwatch_metric_alarm" "latency" { ... }
resource "aws_cloudwatch_metric_alarm" "cpu" { ... }

# SNS Topic
resource "aws_sns_topic" "alarms" {
  name = "penguin-land-alarms"
}

# DynamoDB 테이블 (2개)
resource "aws_dynamodb_table" "deployments" { ... }
resource "aws_dynamodb_table" "alarms" { ... }
```

---

## 🎉 가산점 아이디어 (2일 안에 개발 가능!)

### ⭐ Priority 1: 반드시 구현 (WOW 효과!)

#### 1. 펭귄 춤추는 애니메이션 🐧💃
```
- 정상 상태일 때: 펭귄이 좌우로 흔들며 춤
- 컨페티 터지는 효과
- 빵빠레 사운드

구현 방법:
- Lottie 애니메이션 (1시간)
- canvas-confetti (30분)

WOW 포인트: "귀여워!" 반응 100%
```

#### 2. 실시간 점수 카운터 애니메이션 🔢
```
- 점수가 변경될 때 숫자가 카운트되며 변화
- 예: 15 → 45 (숫자가 올라가는 애니메이션)

구현 방법:
- setInterval로 점진적 증가 (30분)

WOW 포인트: 게임처럼 느껴짐
```

#### 3. 위험 상태 화면 흔들림 효과 📳
```
- 점수 70점 넘으면 화면이 흔들림
- 붉은색 깜빡임

구현 방법:
- CSS keyframe animation (30분)

WOW 포인트: 긴장감 연출
```

### ⭐ Priority 2: 있으면 좋음

#### 4. 배포 스트릭 카운터 🔥
```
- 연속 성공 배포 횟수 표시
- "5회 연속 완벽한 배포!"

구현 방법:
- 로컬스토리지 or DynamoDB (1시간)

WOW 포인트: 게이미피케이션
```

#### 5. 위험 상태 긴급 액션 버튼 🚨
```
- 위험 상태일 때만 버튼 표시
- "🔙 롤백" "📋 로그 확인" "📢 팀 알림"

구현 방법:
- 조건부 렌더링 (1시간)

WOW 포인트: 실용성!
```

#### 6. 로딩 메시지 재미 요소 💬
```
- 배포 중 귀여운 메시지
- "펭귄들이 코드를 검토하고 있어요... 🐧"
- "서버가 준비운동을 하고 있어요... 💪"

구현 방법:
- 메시지 배열 + random (30분)

WOW 포인트: 기다리는 동안 미소!
```

### ⭐ Priority 3: 시간 남으면

#### 7. 배포 히스토리 그래프 📊
```
- 최근 10번 배포의 점수 그래프
- 선 그래프로 시각화

구현 방법:
- recharts (2시간)

WOW 포인트: 프로덕션 레벨!
```

#### 8. 펭귄 스킨 커스터마이징 🎨
```
- 업적 달성 시 스킨 해금
- 골든 펭귄, 산타 펭귄 등

구현 방법:
- 여러 Lottie 파일 + 조건부 렌더링 (2시간)

WOW 포인트: 수집 욕구!
```

---

## 📋 구현 우선순위 요약

```
Day 1 (오늘):
✅ 설계 문서 완성
✅ Python 점수 엔진 완성
✅ 테스트 코드 완성
⬜ API 스펙 문서
⬜ 팀원 질문 해결

Day 2 (내일):
⬜ CloudWatch 설정
⬜ Backend 연동
⬜ Frontend 기본 구현
⬜ 펭귄 애니메이션
⬜ 컨페티 효과

Day 3 (D-Day):
⬜ 버그 수정
⬜ 시뮬레이션 모드
⬜ 가산점 아이디어 1~3개 추가
⬜ 발표 연습
```

---

## 🎯 해커톤 1등을 위한 핵심 포인트

### 기술적 완성도 (40%)
- ✅ Anomaly Detection (ML 기반)
- ✅ Fallback 임계값 시스템 (안정성)
- ✅ 실시간 점수 계산

### 사용자 경험 (40%)
- ✅ 펭귄 캐릭터 (감정적 연결)
- ✅ 게이미피케이션 (재미)
- ✅ 직관적인 메시지 (초보자 친화)

### 발표력 (20%)
- ✅ 라이브 데모 (WOW 효과)
- ✅ 문제 공감 → 솔루션 → 데모
- ✅ "누군가가 '이거 꼭 써보고 싶다!'라고 생각하게 만들기"

---

## 📞 승규님 연락처

- 역할: CloudWatch Anomaly Detection + 점수 시스템
- 파일 위치: `/score_engine/`
- 질문 있으면 언제든지 연락 주세요!

---

**화이팅! 해커톤 1등 가자! 🐧🏆**
