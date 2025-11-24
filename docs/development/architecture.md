# 🐧 CloudWatch Anomaly Detection 설계 문서 (이승규 담당)

**프로젝트**: Penguin-Land - 배포가 즐거운 경험
**담당자**: 이승규
**최종 수정일**: 2025-11-20
**목표**: CloudWatch 메트릭 기반 Anomaly Detection + 점수 시스템 + 재미있는 배포 코칭

---

## 📋 목차

1. [개요](#1-개요)
2. [핵심 목표](#2-핵심-목표)
3. [모니터링 대상 메트릭 정의](#3-모니터링-대상-메트릭-정의)
4. [Anomaly Detection 설계](#4-anomaly-detection-설계)
5. [점수 계산 시스템](#5-점수-계산-시스템)
6. [게이미피케이션 & 재미 요소](#6-게이미피케이션--재미-요소)
7. [시스템 아키텍처](#7-시스템-아키텍처)
8. [API 인터페이스 설계](#8-api-인터페이스-설계)
9. [구현 우선순위](#9-구현-우선순위)
10. [팀원 질문 답변](#10-팀원-질문-답변)

---

## 1. 개요

### 1.1 문제 정의

  배포 후 "내 서비스가 정상인가?"를 확인하는 것은 **불안하고 지루한 경험**입니다.
  - 모니터링 대시보드는 복잡하고 직관적이지 않음
  - 초보 개발자는 어떤 지표를 봐야 할지 모름
  - 배포 후 불안한 마음으로 그래프만 응시

### 1.2 우리의 솔루션

**"배포가 게임처럼 즐겁고, 펭귄이 코치해주는 경험"**

1. **실시간 건강 점수**: 0~100점으로 배포 상태를 즉시 이해
2. **펭귄 코치**: 귀여운 펭귄이 상황에 맞는 조언 제공
3. **게이미피케이션**: 성공 시 빵빠레, 위험 시 긴장감 있는 연출
4. **자동화된 이상 감지**: CloudWatch Anomaly Detection으로 평소와 다른 패턴 자동 감지

### 1.3 핵심 가치

> "누군가가 '이거 꼭 써보고 싶다!'라고 생각할 만큼 매력적인 배포 경험"

---

## 2. 핵심 목표

### 2.1 기술적 목표

- ✅ CloudWatch Anomaly Detection을 활용한 자동 이상 감지
- ✅ 초기 데이터 부족 시 Fallback 임계값 시스템
- ✅ 실시간 점수 계산 및 상태 분류 (정상/주의/위험)
- ✅ SNS → Lambda → Backend API 파이프라인 구축

### 2.2 사용자 경험 목표

- ✅ 배포 후 3초 이내에 첫 피드백 제공
- ✅ 펭귄 캐릭터로 감정적 연결 형성
- ✅ 초보자도 이해할 수 있는 명확한 메시지
- ✅ 시연을 위한 데모 시뮬레이션 모드

### 2.3 해커톤 성공 기준

- ✅ 심사위원이 "오!" 하는 WOW 효과
- ✅ 기술적 완성도 + 재미 요소의 완벽한 조합
- ✅ 실제 사용 가능한 프로덕트 레벨의 완성도

---

## 3. 모니터링 대상 메트릭 정의

### 3.1 핵심 메트릭 (3가지)

| 메트릭명 | CloudWatch 네임스페이스 | 단위 | 설명 | 중요도 |
|---------|------------------------|-----|------|--------|
| **5xx 에러율** | `AWS/ApplicationELB` → `HTTPCode_Target_5XX_Count` | % | 서버 에러 발생 비율 | ⭐⭐⭐ |
| **응답 지연시간** | `AWS/ApplicationELB` → `TargetResponseTime` | ms | P90 응답 시간 | ⭐⭐⭐ |
| **CPU 사용률** | `AWS/EC2` → `CPUUtilization` | % | EC2 인스턴스 부하 | ⭐⭐ |

### 3.2 메트릭 계산 공식

#### (1) 5xx 에러율
```python
error_rate = (HTTPCode_Target_5XX_Count / RequestCount) * 100
```

#### (2) 응답 지연시간
```python
latency_p90 = TargetResponseTime (Statistic=p90)
```

#### (3) CPU 사용률
```python
cpu_usage = CPUUtilization (Statistic=Average)
```

### 3.3 데이터 수집 주기

- **메트릭 수집**: 1분 간격 (CloudWatch 기본)
- **이상 감지 평가**: 5분 간격
- **프론트엔드 폴링**: 3~5초 간격

### 3.4 전준배님께 확인할 사항 ✅

**질문 1**: 모니터링 대상 애플리케이션
- [ ] ALB 뒤에 있는 EC2 애플리케이션을 모니터링하나요?
- [ ] 애플리케이션 타입: Spring Boot / Node.js / Nginx?
- [ ] 추천: **ALB 메트릭 사용** (가장 정확하고 설정 간단)

**질문 2**: CloudWatch Logs 사용 여부
- [ ] 애플리케이션 로그를 CloudWatch Logs에 전송하나요?
- [ ] Metric Filter를 통한 커스텀 메트릭 생성 필요한가요?

**질문 3**: SNS → Backend Webhook URL
- [ ] Webhook 엔드포인트 경로: `/api/cloudwatch/alarm` ?
- [ ] Lambda를 거쳐서 오나요, SNS에서 직접 오나요?

---

## 4. Anomaly Detection 설계

### 4.1 CloudWatch Anomaly Detection 설정

#### 기본 설정값
```yaml
AnomalyDetection:
  Model: Standard (ML 기반 자동 학습)
  EvaluationPeriods: 5 (5분 연속 이상 시 알람)
  DatapointsToAlarm: 3 (5개 중 3개 이상 이상 시 알람)
  Threshold: BAND (상한/하한 밴드 벗어남)
  TrainingPeriod: 최소 3시간 (실제로는 2주 권장)
```

#### 민감도 설정
```python
# Anomaly Detector Band 설정
BandWidth = 2  # 표준편차의 2배 (기본값)

# 더 민감하게: BandWidth = 1.5
# 더 둔감하게: BandWidth = 2.5
```

### 4.2 Fallback 임계값 시스템 (중요!)

해커톤 특성상 **초기 데이터가 부족**하므로, Anomaly Detection이 작동하지 않을 때를 대비한 **하드코딩 임계값 시스템** 필수!

#### Fallback 임계값 테이블

| 메트릭 | 정상 (0-30점) | 주의 (31-70점) | 위험 (71-100점) |
|--------|--------------|---------------|----------------|
| **5xx 에러율** | < 1% | 1% ~ 5% | > 5% |
| **응답 지연시간 (P90)** | < 300ms | 300ms ~ 700ms | > 700ms |
| **CPU 사용률** | < 50% | 50% ~ 80% | > 80% |

#### Fallback 로직 플로우차트
```
1. CloudWatch Anomaly Detection 밴드 확인
   ↓
2. 밴드 데이터 없음? → Fallback 임계값 사용
   ↓
3. 밴드 데이터 있음? → ML 기반 이상 감지 사용
   ↓
4. 점수 계산
```

### 4.3 알람 설정 전략

#### (1) 에러율 알람
```yaml
AlarmName: penguin-land-error-rate-anomaly
MetricName: HTTPCode_Target_5XX_Count
Namespace: AWS/ApplicationELB
Statistic: Sum
Period: 300 (5분)
EvaluationPeriods: 1
ThresholdMetricId: anomaly_detection_band
TreatMissingData: notBreaching
```

#### (2) 레이턴시 알람
```yaml
AlarmName: penguin-land-latency-anomaly
MetricName: TargetResponseTime
Namespace: AWS/ApplicationELB
Statistic: p90
Period: 300
EvaluationPeriods: 1
ThresholdMetricId: anomaly_detection_band
```

#### (3) CPU 알람
```yaml
AlarmName: penguin-land-cpu-anomaly
MetricName: CPUUtilization
Namespace: AWS/EC2
Statistic: Average
Period: 300
EvaluationPeriods: 2  # CPU는 좀 더 여유있게
ThresholdMetricId: anomaly_detection_band
```

### 4.4 시뮬레이션 모드 (데모용)

시연을 위해 **강제로 이상 상태를 만드는 기능** 필요!

#### 시뮬레이션 트리거 방법

**방법 1: Backend API 엔드포인트**
```http
POST /api/cloudwatch/simulate
{
  "metric": "latency",
  "severity": "danger",
  "duration_seconds": 30
}
```

**방법 2: CloudWatch PutMetricData로 가짜 데이터 주입**
```python
cloudwatch.put_metric_data(
    Namespace='PenguinLand/Demo',
    MetricData=[{
        'MetricName': 'SimulatedLatency',
        'Value': 5000,  # 5초 레이턴시 (매우 느림!)
        'Unit': 'Milliseconds',
        'Timestamp': datetime.now()
    }]
)
```

**방법 3: 프론트엔드에서 직접 Mock 데이터**
```javascript
// 시연 버튼 클릭 시
const simulateDanger = () => {
  setHealthScore(95);
  setPenguinState('crying');
  setMessage('🚨 위험! 레이턴시가 5초를 넘었어요!');

  setTimeout(() => {
    setHealthScore(15);
    setPenguinState('happy');
  }, 10000); // 10초 후 정상 복귀
}
```

**추천**: 방법 3이 가장 간단하고 확실함! (해커톤 시연용)

---

## 5. 점수 계산 시스템

### 5.1 점수 계산 알고리즘

#### 핵심 개념
```
건강 점수 (Health Score) = 100점 만점
- 점수가 낮을수록 좋음 (0점 = 완벽, 100점 = 위험)
- 여러 메트릭의 이상도를 종합하여 계산
```

#### 계산 공식
```python
def calculate_health_score(metrics: dict) -> int:
    """
    건강 점수 계산

    Args:
        metrics: {
            'error_rate': {'value': 0.5, 'band_upper': 2.0, 'band_lower': 0.1},
            'latency': {'value': 450, 'band_upper': 600, 'band_lower': 200},
            'cpu': {'value': 65, 'band_upper': 80, 'band_lower': 30}
        }

    Returns:
        int: 0~100 점수
    """

    total_score = 0
    weights = {
        'error_rate': 50,  # 에러율이 가장 중요 (50%)
        'latency': 35,     # 레이턴시 (35%)
        'cpu': 15          # CPU (15%)
    }

    for metric_name, weight in weights.items():
        metric_data = metrics.get(metric_name)
        if not metric_data:
            continue

        # 개별 메트릭 이상도 계산
        severity = calculate_severity(
            value=metric_data['value'],
            band_upper=metric_data.get('band_upper'),
            band_lower=metric_data.get('band_lower'),
            metric_type=metric_name
        )

        # 가중치 적용
        total_score += severity * weight

    # 0~100 범위로 클리핑
    return int(max(0, min(100, total_score)))


def calculate_severity(value, band_upper, band_lower, metric_type):
    """
    개별 메트릭의 심각도 계산

    Returns:
        float: 0.0 ~ 1.0 (0 = 정상, 1 = 매우 위험)
    """

    # Anomaly Detection Band가 있는 경우
    if band_upper and band_lower:
        if value <= band_upper and value >= band_lower:
            return 0.0  # 밴드 안 = 정상

        # 밴드 밖으로 얼마나 벗어났는지 계산
        if value > band_upper:
            deviation = (value - band_upper) / band_upper
        else:
            deviation = (band_lower - value) / band_lower

        # 벗어난 정도를 0~1로 변환
        severity = min(1.0, deviation * 2)  # 50% 벗어나면 위험
        return severity

    # Fallback 임계값 사용
    else:
        thresholds = FALLBACK_THRESHOLDS[metric_type]

        if value <= thresholds['normal']:
            return 0.0
        elif value <= thresholds['warning']:
            # 정상~주의 구간에서 선형 보간
            ratio = (value - thresholds['normal']) / \
                    (thresholds['warning'] - thresholds['normal'])
            return 0.3 + (ratio * 0.4)  # 0.3 ~ 0.7
        else:
            # 주의~위험 구간에서 선형 보간
            ratio = (value - thresholds['warning']) / \
                    (thresholds['danger'] - thresholds['warning'])
            return 0.7 + (ratio * 0.3)  # 0.7 ~ 1.0


# Fallback 임계값 상수
FALLBACK_THRESHOLDS = {
    'error_rate': {
        'normal': 1.0,    # 1% 이하
        'warning': 5.0,   # 5% 이하
        'danger': 10.0    # 10% 초과
    },
    'latency': {
        'normal': 300,    # 300ms 이하
        'warning': 700,   # 700ms 이하
        'danger': 1500    # 1500ms 초과
    },
    'cpu': {
        'normal': 50,     # 50% 이하
        'warning': 80,    # 80% 이하
        'danger': 95      # 95% 초과
    }
}
```

### 5.2 상태 분류 시스템

#### 3단계 상태 분류
```python
def classify_state(score: int) -> str:
    """
    점수를 3단계 상태로 분류

    Args:
        score: 0~100 건강 점수

    Returns:
        'healthy' | 'warning' | 'danger'
    """
    if score <= 30:
        return 'healthy'
    elif score <= 70:
        return 'warning'
    else:
        return 'danger'
```

#### 상태별 특성

| 상태 | 점수 범위 | 펭귄 표정 | 배경색 | 의미 |
|-----|----------|---------|--------|------|
| **Healthy** | 0-30 | 😊 웃음 | 🟢 초록색 | 완벽한 상태! |
| **Warning** | 31-70 | 😐 보통 | 🟡 노란색 | 주의가 필요함 |
| **Danger** | 71-100 | 😭 울음 | 🔴 빨간색 | 즉시 조치 필요! |

### 5.3 코칭 메시지 생성

#### 메시지 생성 로직
```python
def generate_coach_message(state: str, metrics: dict) -> str:
    """
    상황에 맞는 코칭 메시지 생성

    Args:
        state: 'healthy' | 'warning' | 'danger'
        metrics: 메트릭 데이터

    Returns:
        str: 코칭 메시지
    """

    if state == 'healthy':
        return random.choice(HEALTHY_MESSAGES)

    # 어떤 메트릭이 문제인지 파악
    problem_metrics = identify_problem_metrics(metrics)

    if state == 'warning':
        return generate_warning_message(problem_metrics)

    if state == 'danger':
        return generate_danger_message(problem_metrics)


# 메시지 템플릿
HEALTHY_MESSAGES = [
    "🎉 완벽해요! 모든 지표가 정상이에요!",
    "👍 아주 안정적이에요! 지금 상태로도 충분해요!",
    "✨ 훌륭한 배포에요! 펭귄이 춤추고 있어요!",
    "🌟 최고의 상태에요! 이대로 유지해주세요!",
    "🏆 완벽한 점수! 축하드려요!"
]

def generate_warning_message(problem_metrics: list) -> str:
    """주의 상태 메시지"""

    if 'latency' in problem_metrics:
        return "⚠️ 응답 속도가 약간 느려지고 있어요. DB나 외부 API를 확인해보면 좋아요!"

    if 'cpu' in problem_metrics:
        return "⚠️ CPU 사용률이 높아지고 있어요. 트래픽이 증가했나요?"

    if 'error_rate' in problem_metrics:
        return "⚠️ 에러가 조금씩 발생하고 있어요. 로그를 확인해보세요!"

    return "⚠️ 조금 불안정해 보여요. 모니터링을 계속 지켜봐주세요!"


def generate_danger_message(problem_metrics: list) -> str:
    """위험 상태 메시지"""

    messages = []

    if 'error_rate' in problem_metrics:
        messages.append("🚨 에러율이 급증했어요! 최근 배포 내역을 확인하세요!")

    if 'latency' in problem_metrics:
        messages.append("🚨 응답이 매우 느려요! DB 연결이나 외부 API를 점검하세요!")

    if 'cpu' in problem_metrics:
        messages.append("🚨 CPU가 과부하 상태에요! 오토스케일링을 고려하세요!")

    if messages:
        return " ".join(messages)

    return "🚨 위험한 상태에요! 즉시 조치가 필요해요!"


def identify_problem_metrics(metrics: dict) -> list:
    """문제가 있는 메트릭 식별"""
    problems = []

    for metric_name, metric_data in metrics.items():
        severity = calculate_severity(
            value=metric_data['value'],
            band_upper=metric_data.get('band_upper'),
            band_lower=metric_data.get('band_lower'),
            metric_type=metric_name
        )

        if severity > 0.4:  # 40% 이상 이상하면 문제로 간주
            problems.append(metric_name)

    return problems
```

---

## 6. 게이미피케이션 & 재미 요소

### 6.1 핵심 재미 요소

#### (1) 펭귄 캐릭터 애니메이션
```javascript
// 상태별 펭귄 애니메이션
const PenguinStates = {
  healthy: {
    animation: 'happy-dance',      // 춤추는 애니메이션
    lottieFile: 'penguin-happy.json',
    duration: 2000,
    loop: true
  },
  warning: {
    animation: 'nervous-walk',     // 불안하게 걷는 애니메이션
    lottieFile: 'penguin-worried.json',
    duration: 1500,
    loop: true
  },
  danger: {
    animation: 'crying',           // 우는 애니메이션
    lottieFile: 'penguin-crying.json',
    duration: 1000,
    loop: true,
    shake: true                    // 화면 흔들림 효과
  }
}
```

#### (2) 배경 효과 & 사운드
```javascript
const BackgroundEffects = {
  healthy: {
    color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    particles: 'confetti',         // 컨페티 효과
    sound: 'success-fanfare.mp3',  // 빵빠레 소리
    duration: 3000
  },
  warning: {
    color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    particles: 'warning-icons',    // 경고 아이콘 떨어지는 효과
    sound: 'warning-beep.mp3',
    pulse: true                    // 펄스 효과
  },
  danger: {
    color: 'linear-gradient(135deg, #ff0844 0%, #ffb199 100%)',
    particles: 'fire',             // 불 이펙트
    sound: 'alarm-urgent.mp3',
    shake: true,                   // 화면 흔들림
    flash: true                    // 깜빡임 효과
  }
}
```

#### (3) 실시간 점수 카운터 애니메이션
```javascript
// 점수가 변경될 때 숫자가 카운트되는 애니메이션
const animateScoreChange = (oldScore, newScore) => {
  const duration = 1000; // 1초
  const steps = 30;
  const increment = (newScore - oldScore) / steps;

  let current = oldScore;
  const interval = setInterval(() => {
    current += increment;
    setDisplayScore(Math.round(current));

    if (Math.abs(current - newScore) < Math.abs(increment)) {
      setDisplayScore(newScore);
      clearInterval(interval);
    }
  }, duration / steps);
}
```

### 6.2 추가 재미 요소 아이디어 💡

#### (1) 배포 스트릭 & 업적 시스템
```javascript
const Achievements = {
  'perfect-deployer': {
    title: '완벽주의자',
    description: '5번 연속 점수 0~10점으로 배포',
    icon: '🏆',
    reward: 'golden-penguin-skin'
  },
  'lucky-survivor': {
    title: '행운의 생존자',
    description: '위험 상태에서 3분 안에 정상 복구',
    icon: '🍀',
    reward: 'lucky-penguin-skin'
  },
  'night-owl': {
    title: '야행성 개발자',
    description: '새벽 2시~5시 사이에 배포 성공',
    icon: '🦉',
    reward: 'sleepy-penguin-skin'
  },
  'speed-demon': {
    title: '스피드 데몬',
    description: '배포 후 10초 이내에 모든 지표 정상',
    icon: '⚡',
    reward: 'racing-penguin-skin'
  }
}
```

#### (2) 펭귄 커스터마이징
```javascript
const PenguinSkins = {
  default: 'classic-penguin.json',
  golden: 'golden-penguin.json',      // 완벽주의자 업적
  lucky: 'clover-penguin.json',       // 행운의 생존자
  sleepy: 'sleepy-penguin.json',      // 야행성 개발자
  racing: 'racing-penguin.json',      // 스피드 데몬
  santa: 'santa-penguin.json',        // 크리스마스 시즌
  ninja: 'ninja-penguin.json'         // 히든 업적
}
```

#### (3) 배포 BGM & 사운드 이펙트
```javascript
const SoundEffects = {
  deploy_start: 'deploy-countdown.mp3',
  healthy: 'success-fanfare.mp3',
  warning: 'warning-beep.mp3',
  danger: 'alarm-siren.mp3',
  recovery: 'recovery-jingle.mp3',
  achievement_unlock: 'achievement-unlock.mp3',

  // BGM (루프)
  bgm_normal: 'calm-music.mp3',
  bgm_warning: 'tension-music.mp3',
  bgm_danger: 'dramatic-music.mp3'
}
```

#### (4) 배포 히스토리 & 리더보드
```javascript
// 배포 히스토리 저장
const DeploymentHistory = {
  user_id: 'user123',
  deployments: [
    {
      timestamp: '2025-11-20T14:30:00Z',
      score: 15,
      state: 'healthy',
      duration: '2m 30s',
      metrics_snapshot: {...}
    },
    // ...
  ],
  stats: {
    total_deployments: 47,
    success_rate: 0.94,
    average_score: 23,
    best_score: 5,
    current_streak: 8
  }
}

// 팀 리더보드
const Leaderboard = [
  { team: 'Team Penguin', avg_score: 12, perfect_deploys: 15 },
  { team: 'Team Rocket', avg_score: 18, perfect_deploys: 12 },
  { team: 'Team Alpha', avg_score: 25, perfect_deploys: 8 }
]
```

#### (5) 위험 상태 시 긴급 액션 버튼
```javascript
// 위험 상태일 때 빠른 대응 버튼 표시
const EmergencyActions = {
  rollback: {
    label: '🔙 이전 버전으로 롤백',
    action: () => triggerRollback(),
    confirm: true
  },
  scale_up: {
    label: '⬆️ 인스턴스 증설',
    action: () => triggerAutoScaling(),
    confirm: true
  },
  view_logs: {
    label: '📋 에러 로그 확인',
    action: () => openCloudWatchLogs(),
    confirm: false
  },
  notify_team: {
    label: '📢 팀에 알림 보내기',
    action: () => sendSlackAlert(),
    confirm: false
  }
}
```

#### (6) 배포 중 로딩 메시지
```javascript
const LoadingMessages = [
  "펭귄들이 코드를 검토하고 있어요... 🐧",
  "서버가 준비운동을 하고 있어요... 💪",
  "데이터베이스와 인사를 나누는 중이에요... 👋",
  "네트워크 경로를 확인하고 있어요... 🗺️",
  "보안 검사를 통과하는 중이에요... 🔐",
  "거의 다 왔어요! 펭귄들이 힘내고 있어요! 🎉",
  "마지막 점검 중이에요... ✅"
]
```

#### (7) 계절/이벤트별 테마
```javascript
const SeasonalThemes = {
  christmas: {
    penguin: 'santa-penguin',
    background: 'snow-particles',
    music: 'jingle-bells-techno.mp3'
  },
  halloween: {
    penguin: 'ghost-penguin',
    background: 'spooky-fog',
    music: 'spooky-deployment.mp3'
  },
  new_year: {
    penguin: 'party-penguin',
    background: 'fireworks',
    music: 'celebration.mp3'
  }
}
```

### 6.3 시연용 데모 시나리오

#### 시나리오 1: 완벽한 배포 (30초)
```
1. [0s] 배포 시작 버튼 클릭
2. [3s] 로딩 화면 + 귀여운 메시지
3. [8s] 배포 완료! 빵빠레 효과
4. [10s] 펭귄이 춤추며 "완벽해요!" 메시지
5. [15s] 점수 0점! 컨페티 터짐
6. [20s] 업적 해제: "완벽주의자"
7. [25s] 배포 히스토리에 기록
```

#### 시나리오 2: 위험 감지 & 복구 (60초)
```
1. [0s] 정상 상태 (점수 15점)
2. [10s] "시뮬레이션" 버튼 클릭
3. [12s] 경고음 + 펭귄 표정 변화
4. [15s] 점수 급상승 → 85점 (위험)
5. [18s] 화면 흔들림 + "🚨 위험!" 메시지
6. [25s] 긴급 액션 버튼 표시
7. [35s] 시뮬레이션 종료
8. [40s] 점수 하락 → 20점 (정상)
9. [45s] 펭귄 다시 웃음
10. [50s] "위기에서 복구!" 업적 해제
11. [55s] 리더보드 업데이트
```

---

## 7. 시스템 아키텍처

### 7.1 전체 데이터 흐름

```
[EC2 Application]
     ↓ (메트릭 발생)
[CloudWatch Metrics]
     ↓ (1분 간격 수집)
[Anomaly Detection Model]
     ↓ (이상 감지)
[CloudWatch Alarm]
     ↓ (알람 발생)
[SNS Topic]
     ↓ (알림 전송)
[Lambda Function] (선택적)
     ↓ (데이터 가공)
[Spring Boot Backend API]
     ↓ (점수 계산 + DB 저장)
[Next.js Frontend]
     ↓ (실시간 폴링)
[사용자 대시보드]
     ↓ (펭귄 애니메이션)
```

### 7.2 컴포넌트 역할

#### (1) CloudWatch
- **역할**: 메트릭 수집 및 이상 감지
- **설정**: Anomaly Detection + Alarm
- **출력**: SNS 메시지

#### (2) SNS Topic
- **역할**: 알람 메시지 라우팅
- **구독자**: Lambda 또는 Backend Webhook

#### (3) Lambda (선택적)
- **역할**: SNS 메시지 파싱 및 가공
- **기능**:
  - JSON 변환
  - 중복 알람 필터링
  - 메트릭 값 추출
- **출력**: Backend API 호출

#### (4) Spring Boot Backend
- **역할**: 비즈니스 로직 처리
- **기능**:
  - 점수 계산 (Python 로직 이식)
  - 상태 분류
  - 코칭 메시지 생성
  - DynamoDB 저장
  - WebSocket으로 Frontend에 실시간 전송

#### (5) Python Score Engine (참조용)
- **역할**: 점수 계산 로직 원본
- **용도**: Java 이식의 기준
- **위치**: `/score_engine/`

#### (6) Next.js Frontend
- **역할**: 사용자 인터페이스
- **기능**:
  - 실시간 폴링 (3~5초)
  - 펭귄 애니메이션 렌더링
  - 게이미피케이션 연출
  - 배포 히스토리 표시

### 7.3 대안 아키텍처: Lambda 없이 직접 연결

```
[CloudWatch Alarm]
     ↓
[SNS Topic]
     ↓ (HTTP/HTTPS Subscription)
[Spring Boot Webhook Endpoint]
     ↓
[나머지 동일]
```

**장점**: 구조 단순, 레이턴시 감소
**단점**: SNS 메시지 형식을 Backend에서 직접 파싱 필요

**추천**: 해커톤 시간이 부족하면 이 방식 사용!

---

## 8. API 인터페이스 설계

### 8.1 SNS → Backend Webhook

#### SNS 메시지 형식
```json
{
  "Type": "Notification",
  "MessageId": "abc123",
  "TopicArn": "arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms",
  "Subject": "ALARM: penguin-land-latency-anomaly",
  "Message": "{\"AlarmName\":\"penguin-land-latency-anomaly\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint [850.0 (20/11/25 14:30:00)] was greater than the threshold (ANOMALY_DETECTION_BAND).\",\"StateChangeTime\":\"2025-11-20T14:30:00.000+0000\",\"Trigger\":{\"MetricName\":\"TargetResponseTime\",\"Namespace\":\"AWS/ApplicationELB\",\"StatisticType\":\"Statistic\",\"Statistic\":\"p90\",\"Period\":300,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"LessThanLowerOrGreaterThanUpperThreshold\",\"Threshold\":null,\"TreatMissingData\":\"notBreaching\",\"Dimensions\":[{\"value\":\"app/penguin-land-alb/abc123\",\"name\":\"LoadBalancer\"}]}}",
  "Timestamp": "2025-11-20T14:30:00.000Z"
}
```

#### Backend Webhook 엔드포인트
```java
POST /api/cloudwatch/alarm
Content-Type: application/json

// SNS 메시지를 그대로 수신
```

### 8.2 Backend 내부 데이터 모델

#### MetricSnapshot (메트릭 스냅샷)
```json
{
  "timestamp": "2025-11-20T14:30:00Z",
  "session_id": "session-abc123",
  "metrics": {
    "error_rate": {
      "value": 2.5,
      "unit": "percent",
      "band_upper": 3.0,
      "band_lower": 0.5,
      "state": "warning"
    },
    "latency": {
      "value": 450,
      "unit": "milliseconds",
      "band_upper": 600,
      "band_lower": 200,
      "state": "healthy"
    },
    "cpu": {
      "value": 65,
      "unit": "percent",
      "band_upper": 80,
      "band_lower": 30,
      "state": "warning"
    }
  },
  "overall_score": 45,
  "overall_state": "warning",
  "coach_message": "⚠️ 에러율과 CPU가 약간 높아지고 있어요. 모니터링을 계속 지켜봐주세요!"
}
```

### 8.3 Backend → Frontend API

#### (1) 현재 상태 조회
```http
GET /api/deployment/status?session_id=session-abc123

Response:
{
  "session_id": "session-abc123",
  "deployment_status": "COMPLETE",  // INIT, PLANNING, APPLYING, COMPLETE, FAILED
  "health_score": 45,
  "health_state": "warning",  // healthy, warning, danger
  "coach_message": "⚠️ 에러율과 CPU가 약간 높아지고 있어요.",
  "penguin_animation": "worried",  // happy, worried, crying
  "metrics": {
    "error_rate": {...},
    "latency": {...},
    "cpu": {...}
  },
  "last_updated": "2025-11-20T14:30:00Z"
}
```

#### (2) 시뮬레이션 트리거
```http
POST /api/cloudwatch/simulate

Request:
{
  "metric": "latency",  // error_rate, latency, cpu
  "severity": "danger",  // warning, danger
  "duration_seconds": 30
}

Response:
{
  "success": true,
  "simulation_id": "sim-123",
  "message": "시뮬레이션이 시작되었습니다. 30초 후 자동 종료됩니다."
}
```

#### (3) 배포 히스토리 조회
```http
GET /api/deployment/history?user_id=user123&limit=10

Response:
{
  "user_id": "user123",
  "total_deployments": 47,
  "deployments": [
    {
      "session_id": "session-abc123",
      "timestamp": "2025-11-20T14:30:00Z",
      "final_score": 15,
      "final_state": "healthy",
      "duration": "2m 30s",
      "achievement_unlocked": ["perfect-deployer"]
    },
    // ...
  ],
  "stats": {
    "success_rate": 0.94,
    "average_score": 23,
    "best_score": 5,
    "current_streak": 8
  }
}
```

#### (4) WebSocket 실시간 업데이트 (선택적)
```javascript
// Frontend에서 WebSocket 연결
const ws = new WebSocket('ws://backend/ws/deployment');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // {
  //   "type": "health_update",
  //   "score": 55,
  //   "state": "warning",
  //   "message": "⚠️ 주의 필요!",
  //   "timestamp": "2025-11-20T14:30:05Z"
  // }

  updateDashboard(data);
};
```

### 8.4 DynamoDB 테이블 스키마

#### Table: penguin-land-deployments
```
PK: session_id (String)
SK: timestamp (String, ISO 8601)

Attributes:
- user_id: String
- deployment_status: String
- health_score: Number
- health_state: String
- metrics: Map
- coach_message: String
- created_at: String
- updated_at: String
```

#### Table: penguin-land-alarms
```
PK: alarm_id (String)
SK: timestamp (String)

Attributes:
- session_id: String
- alarm_name: String
- metric_name: String
- new_state: String (ALARM, OK)
- metric_value: Number
- band_upper: Number
- band_lower: Number
- raw_message: String
```

---

## 9. 구현 우선순위

### Phase 1: 핵심 기능 (11월 20일)

#### 오늘 반드시 완료해야 하는 것 ✅

1. **설계 문서 완성** ✅ (이 문서!)
2. **Python 점수 엔진 구현**
3. **Fallback 임계값 시스템 구현**
4. **SNS 메시지 파싱 로직 설계**
5. **API 스펙 확정 및 팀 공유**

#### 오늘의 산출물
- ✅ 이 설계 문서 (Markdown)
- ✅ `/score_engine/score.py` (점수 계산 로직)
- ✅ `/score_engine/test_score.py` (테스트 코드)
- ✅ `API_SPEC.md` (Backend 팀 공유용)
- ✅ `QUESTIONS_FOR_TEAM.md` (전준배님께 질문 목록)

### Phase 2: 통합 & 테스트 (11월 21일)

1. CloudWatch Anomaly Detection 설정
2. SNS → Lambda/Backend 연동
3. Backend API 구현 (Java로 이식)
4. DynamoDB 테이블 생성
5. 통합 테스트

### Phase 3: 프론트엔드 & 재미 요소 (11월 22일)

1. 펭귄 애니메이션 구현
2. 실시간 폴링 연동
3. 게이미피케이션 효과 추가
4. 시뮬레이션 모드 구현
5. 배포 히스토리 화면

### Phase 4: 시연 준비 (11월 22일 오후)

1. 데모 시나리오 리허설
2. 버그 수정 및 안정화
3. 발표 자료 준비
4. 백업 플랜 준비

---

## 10. 팀원 질문 답변

### 전준배님 질문 답변

#### Q1: "파이썬 프레임워크 쪽 뭐 쓰시는지 말씀부탁드립니다!"

**답변**:
```
Python 프레임워크는 사용하지 않습니다!

이유:
1. 점수 계산 로직은 순수 Python 함수로 구현 (Flask/FastAPI 불필요)
2. 이 Python 코드는 "참조용"이며, 실제로는 Java로 이식할 예정
3. 테스트만 pytest로 진행

파일 구조:
/score_engine/
  ├── score.py           # 점수 계산 로직 (순수 함수)
  ├── test_score.py      # pytest 테스트 코드
  ├── requirements.txt   # boto3, pytest만
  └── README.md          # Java 팀이 참고할 문서

의존성:
- boto3: CloudWatch 메트릭 테스트용
- pytest: 유닛 테스트
- python-dotenv: AWS 자격증명 관리

설치:
pip install boto3 pytest python-dotenv
```

#### Q2: CloudWatch 구성 관련

**질문 목록 (전준배님께 확인 필요)**:

1. **모니터링 대상 애플리케이션**
   - ALB를 사용하나요? (추천: ALB 메트릭이 가장 정확)
   - EC2에서 직접 메트릭을 수집하나요?
   - 애플리케이션 타입: Spring Boot / Node.js / Nginx?

2. **CloudWatch Logs**
   - 애플리케이션 로그를 CloudWatch Logs에 전송하나요?
   - Metric Filter를 통한 커스텀 메트릭 필요한가요?

3. **SNS Webhook**
   - Backend Webhook URL: `/api/cloudwatch/alarm` 이걸로 할까요?
   - Lambda를 거쳐야 하나요, SNS에서 직접 오나요?
   - 추천: **SNS → Backend 직접 연결** (Lambda 생략하면 단순함!)

4. **테스트 환경**
   - 실제 트래픽을 받는 애플리케이션이 있나요?
   - 아니면 더미 데이터를 주입해야 하나요?
   - 시뮬레이션 모드로 충분한가요?

### 강종연님께 전달 사항

#### 프론트엔드 구현을 위한 요구사항

**1. API 폴링**
```javascript
// 3~5초마다 상태 체크
useEffect(() => {
  const interval = setInterval(async () => {
    const response = await fetch(`/api/deployment/status?session_id=${sessionId}`);
    const data = await response.json();

    setHealthScore(data.health_score);
    setHealthState(data.health_state);
    setCoachMessage(data.coach_message);
    setPenguinAnimation(data.penguin_animation);
  }, 3000);

  return () => clearInterval(interval);
}, [sessionId]);
```

**2. 펭귄 애니메이션 라이브러리**
```bash
npm install lottie-react
```

**3. 컨페티 효과**
```bash
npm install canvas-confetti
```

**4. 사운드 효과**
```bash
npm install use-sound
```

**5. 차트 (선택적)**
```bash
npm install recharts
```

#### 디자인 가이드

**색상 팔레트**:
```css
:root {
  --healthy-primary: #10b981;    /* 초록 */
  --healthy-bg: #d1fae5;

  --warning-primary: #f59e0b;    /* 노랑 */
  --warning-bg: #fef3c7;

  --danger-primary: #ef4444;     /* 빨강 */
  --danger-bg: #fee2e2;

  --penguin-primary: #667eea;    /* 보라 */
  --text-primary: #1f2937;
}
```

**펭귄 캐릭터 에셋 필요**:
- `penguin-happy.json` (Lottie)
- `penguin-worried.json` (Lottie)
- `penguin-crying.json` (Lottie)

**사운드 에셋 필요**:
- `success-fanfare.mp3`
- `warning-beep.mp3`
- `alarm-urgent.mp3`

---

## 부록: 빠른 시작 가이드

### A. 로컬 개발 환경 세팅 (5분)

```bash
# 1. 프로젝트 폴더로 이동
cd "C:\Users\electrozone\Desktop\소뱅 해커톤\CloudWatch-Metric"

# 2. 가상환경 활성화
.\venv\Scripts\activate

# 3. 패키지 설치
pip install boto3 pytest python-dotenv

# 4. AWS 자격증명 설정 (팀 공용 계정)
# .env 파일 생성
echo "AWS_ACCESS_KEY_ID=your_key" > .env
echo "AWS_SECRET_ACCESS_KEY=your_secret" >> .env
echo "AWS_REGION=ap-northeast-2" >> .env

# 5. 폴더 구조 생성
mkdir score_engine
cd score_engine
```

### B. 첫 번째 테스트 실행

```bash
# score_engine 폴더에서
pytest test_score.py -v
```

### C. 팀원과 공유할 파일

1. **설계 문서** (이 파일)
   - 전체 팀원이 읽어야 함

2. **API_SPEC.md**
   - Backend 팀 (Spring Boot)
   - Frontend 팀 (Next.js)

3. **score.py**
   - Backend 팀이 Java로 이식

4. **QUESTIONS_FOR_TEAM.md**
   - 전준배님께 확인 요청

---

## 결론

이 설계 문서는 **CloudWatch Anomaly Detection + 점수 시스템 + 게이미피케이션**의 완전한 청사진입니다.

### 핵심 성공 요소

1. ✅ **기술적 완성도**: Anomaly Detection + Fallback 시스템
2. ✅ **사용자 경험**: 펭귄 + 게이미피케이션
3. ✅ **팀 협업**: 명확한 API 스펙 + 역할 분담
4. ✅ **시연 완성도**: 데모 시나리오 + 시뮬레이션 모드

### 승규님이 오늘 해야 할 일 (우선순위)

1. ✅ 이 문서를 팀에 공유
2. ✅ Python 점수 엔진 구현 (`score.py`)
3. ✅ 테스트 코드 작성 (`test_score.py`)
4. ✅ API 스펙 문서 작성
5. ✅ 전준배님께 질문 목록 전달

---

**화이팅! 해커톤 1등 가자! 🐧🏆**
