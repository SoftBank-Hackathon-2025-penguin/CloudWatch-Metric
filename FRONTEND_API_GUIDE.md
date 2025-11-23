# 🐧 Penguin-Land 프론트엔드 API 연동 가이드

백엔드 파트에서 프론트엔드 파트로 전달하는 API 명세서입니다.

---

## 🚀 빠른 시작

### 1. 백엔드 서버 실행
```bash
cd backend
python main.py
```
→ 서버가 `http://localhost:8000`에서 실행됩니다.

### 2. API 베이스 URL
```javascript
const API_BASE_URL = 'http://localhost:8000';
```

---

## 📡 API 엔드포인트

### 1. 모니터링 데이터 조회 (메인 API)

**프론트엔드에서 5초마다 이 API를 호출하세요!**

```http
GET /monitoring
```

#### 응답 예시
```json
{
  "metrics": {
    "cpuUsage": 35.2,          // CPU 사용률 (0-100)
    "latency": 180.5,          // 응답시간 (ms)
    "errorRate": 0.3,          // 에러율 (0-100%)
    "timestamp": "2025-11-22T03:05:32.123Z"
  },
  "anomaly": {
    "healthScore": 12,         // 건강 점수 (0-100, 낮을수록 좋음)
    "healthState": "healthy",  // 'healthy' | 'warning' | 'danger'
    "penguinAnimation": "happy", // 'happy' | 'worried' | 'crying'
    "coachMessage": "완벽해요! 모든 지표가 정상이에요!"
  },
  "alerts": [
    {
      "id": "alert-error_rate-1234567890",
      "level": "warning",      // 'info' | 'warning' | 'critical'
      "message": "Error Rate 주의 필요 (심각도: 50%)",
      "timestamp": "2025-11-22T03:05:32.123Z",
      "acknowledged": false
    }
  ]
}
```

#### 프론트엔드 예제 코드
```javascript
// 5초마다 모니터링 데이터 가져오기
setInterval(async () => {
  try {
    const response = await fetch('http://localhost:8000/monitoring');
    const data = await response.json();

    // UI 업데이트
    updateScore(data.anomaly.healthScore);
    updateState(data.anomaly.healthState);
    updatePenguin(data.anomaly.penguinAnimation);
    updateMessage(data.anomaly.coachMessage);
    updateMetrics(data.metrics);
    updateAlerts(data.alerts);
  } catch (error) {
    console.error('API 호출 실패:', error);
  }
}, 5000); // 5초마다
```

---

### 2. 자동 시나리오 전환 (🎯 시연용 - 강력 추천!)

**20초마다 자동으로 3가지 상태가 바뀝니다!**

```http
POST /monitoring/simulate/auto?interval=20
```

#### 동작 방식
- **0-20초**: Healthy 상태 (점수 10-20점)
- **20-40초**: Warning 상태 (점수 50-60점)
- **40-60초**: Danger 상태 (점수 80-90점)
- **60초~**: 다시 Healthy로 돌아가서 무한 반복

#### 요청 예시
```bash
# 기본 20초 간격
curl -X POST http://localhost:8000/monitoring/simulate/auto

# 10초 간격으로 설정
curl -X POST "http://localhost:8000/monitoring/simulate/auto?interval=10"
```

#### JavaScript 예시
```javascript
// 자동 시뮬레이션 시작 버튼
async function startAutoDemo() {
  const response = await fetch('http://localhost:8000/monitoring/simulate/auto?interval=20', {
    method: 'POST'
  });
  const data = await response.json();
  console.log(data.message); // "20초마다 자동으로 시나리오가 전환됩니다"
}
```

---

### 3. 수동 시나리오 시작

특정 상태를 직접 설정하고 싶을 때 사용하세요.

```http
POST /monitoring/simulate/start
Content-Type: application/json

{
  "scenario": "normal",      // 'normal' | 'high_latency' | 'cpu_spike' | 'error_burst'
  "duration": 30             // 지속 시간 (초, 선택사항)
}
```

#### 시나리오 설명
| scenario | 상태 | 점수 | 설명 |
|----------|------|------|------|
| `normal` | Healthy | 10-20 | 정상 상태 |
| `high_latency` | Warning | 50-60 | 응답 시간 느림 |
| `cpu_spike` | Warning | 50-70 | CPU 사용률 높음 |
| `error_burst` | Danger | 80-90 | 에러 급증 |

#### JavaScript 예시
```javascript
// Warning 상태를 30초간 표시
async function showWarning() {
  await fetch('http://localhost:8000/monitoring/simulate/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      scenario: 'high_latency',
      duration: 30
    })
  });
}
```

---

### 4. 시뮬레이션 종료

```http
POST /monitoring/simulate/stop
```

#### JavaScript 예시
```javascript
async function stopSimulation() {
  await fetch('http://localhost:8000/monitoring/simulate/stop', {
    method: 'POST'
  });
}
```

---

## 🎨 UI 업데이트 가이드

### 건강 상태별 UI 변경

```javascript
function updateUI(data) {
  const { healthScore, healthState, penguinAnimation, coachMessage } = data.anomaly;

  // 1. 점수 표시
  document.getElementById('score').textContent = healthScore;

  // 2. 상태별 색상 변경
  const colors = {
    healthy: '#16a34a',   // 초록색
    warning: '#d97706',   // 주황색
    danger: '#dc2626'     // 빨간색
  };
  document.getElementById('score').style.color = colors[healthState];

  // 3. 펭귄 이미지 변경
  const penguinImages = {
    happy: './assets/penguin-healthy.png',
    worried: './assets/penguin-warning.png',
    crying: './assets/penguin-danger.png'
  };
  document.getElementById('penguin').src = penguinImages[penguinAnimation];

  // 4. 메시지 표시
  document.getElementById('message').textContent = coachMessage;

  // 5. 애니메이션 효과
  if (healthState === 'healthy') {
    // 펭귄 춤추기 애니메이션
    document.getElementById('penguin').classList.add('dancing');
  } else if (healthState === 'danger') {
    // 화면 흔들기 + 깜빡임
    document.body.classList.add('shake', 'flash');
  }
}
```

---

## 🎯 시연 시나리오 (3분 완벽 시연)

### 시연 순서

```bash
# 1단계: 백엔드 시작
cd backend
python main.py

# 2단계: 프론트엔드 열기
# 브라우저에서 index.html 열기

# 3단계: 자동 시뮬레이션 시작 (이것만 실행하면 끝!)
curl -X POST http://localhost:8000/monitoring/simulate/auto
```

### 자동으로 보여지는 내용
- **0-20초**: 🟢 Healthy - 펭귄이 춤추며 "완벽해요!" 메시지
- **20-40초**: 🟡 Warning - 걱정하는 펭귄, "응답이 느려지고 있어요!" 메시지
- **40-60초**: 🔴 Danger - 우는 펭귄, 화면 흔들림, "에러가 급증했어요!" 메시지
- **60초~**: 다시 처음으로 반복

---

## 📊 메트릭 값 범위

| 메트릭 | Healthy | Warning | Danger |
|--------|---------|---------|--------|
| CPU 사용률 | 20-40% | 60-80% | 85-95% |
| 응답 시간 | 150-250ms | 600-800ms | 1500-2500ms |
| 에러율 | 0-1% | 3-7% | 10-15% |

---

## 🐛 트러블슈팅

### CORS 에러 발생 시
백엔드에서 이미 CORS를 허용했지만, 문제가 있으면:
```python
# backend/main.py에서 확인
allow_origins=["*"]  # 모든 origin 허용됨
```

### 연결 안 될 때
1. 백엔드가 실행 중인지 확인: `http://localhost:8000` 접속
2. 방화벽 확인
3. 포트 8000이 사용 중인지 확인

---

## ✅ 체크리스트

프론트엔드 개발 시 확인하세요:

- [ ] `/monitoring` API를 5초마다 호출하도록 설정
- [ ] `healthScore`, `healthState`, `penguinAnimation` 값으로 UI 업데이트
- [ ] 3가지 상태별 색상/애니메이션 구현
- [ ] 시연용 자동 시뮬레이션 버튼 추가 (선택사항)
- [ ] 에러 처리 (API 호출 실패 시)

---

## 💬 질문이 있으면?

백엔드 개발자에게 물어보세요:
- API 문서: `http://localhost:8000/docs` (FastAPI 자동 문서)
- 원본 메트릭 확인: `http://localhost:8000/api/metrics/raw`

---

**🎉 이제 프론트엔드 연동 준비 완료! 화이팅! 🐧**
