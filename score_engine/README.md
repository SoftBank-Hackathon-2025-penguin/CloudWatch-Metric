# 🐧 Penguin-Land Score Engine

CloudWatch 메트릭을 분석하여 배포 상태를 0~100점으로 점수화하고, 펭귄 코치 메시지를 생성하는 엔진입니다.

---

## 📋 목차

1. [개요](#개요)
2. [설치](#설치)
3. [사용법](#사용법)
4. [함수 설명](#함수-설명)
5. [Java로 이식하기](#java로-이식하기)
6. [테스트](#테스트)

---

## 개요

### 핵심 기능

- ✅ **점수 계산**: 0~100점 (0=완벽, 100=위험)
- ✅ **상태 분류**: healthy / warning / danger
- ✅ **코칭 메시지**: 상황에 맞는 조언 자동 생성
- ✅ **Anomaly Detection**: ML 밴드 기반 이상 감지
- ✅ **Fallback 시스템**: 데이터 부족 시 하드코딩 임계값 사용

### 아키텍처

```
MetricData → calculate_severity() → calculate_health_score()
                                  ↓
                            classify_state()
                                  ↓
                          generate_coach_message()
                                  ↓
                         analyze_deployment_health()
```

---

## 설치

### 1. 가상환경 생성 (선택적)
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Mac/Linux
```

### 2. 패키지 설치
```bash
pip install -r requirements.txt
```

### 3. 환경변수 설정 (AWS 테스트용)
```bash
# .env 파일 생성
echo "AWS_ACCESS_KEY_ID=your_key" > .env
echo "AWS_SECRET_ACCESS_KEY=your_secret" >> .env
echo "AWS_REGION=ap-northeast-2" >> .env
```

---

## 사용법

### 기본 사용 예시

```python
from score import analyze_deployment_health

# 메트릭 데이터 준비
metrics = {
    'error_rate': {
        'value': 2.5,
        'band_upper': 3.0,
        'band_lower': 0.5
    },
    'latency': {
        'value': 450,
        'band_upper': 600,
        'band_lower': 200
    },
    'cpu': {
        'value': 65
    }
}

# 분석 실행
result = analyze_deployment_health(metrics)

# 결과 출력
print(f"점수: {result['health_score']}점")
print(f"상태: {result['health_state']}")
print(f"메시지: {result['coach_message']}")
print(f"펭귄: {result['penguin_animation']}")
```

### 출력 예시
```
점수: 45점
상태: warning
메시지: ⚠️ 에러율과 CPU가 약간 높아지고 있어요!
펭귄: worried
```

### CLI 테스트
```bash
python score.py
```

---

## 함수 설명

### 1. analyze_deployment_health() - 메인 API

**가장 중요한 함수입니다.** Backend에서 이 함수만 호출하면 됩니다.

```python
def analyze_deployment_health(metrics: Dict[str, Dict]) -> Dict:
    """
    배포 상태를 종합 분석

    Args:
        metrics: {
            'error_rate': {'value': 2.5, 'band_upper': 3.0, 'band_lower': 0.5},
            'latency': {'value': 450, 'band_upper': 600, 'band_lower': 200},
            'cpu': {'value': 65}
        }

    Returns:
        {
            'health_score': 45,
            'health_state': 'warning',
            'coach_message': '⚠️ 에러율이...',
            'penguin_animation': 'worried',
            'problem_metrics': [('error_rate', 0.7), ...]
        }
    """
```

### 2. calculate_severity() - 개별 메트릭 심각도 계산

```python
def calculate_severity(
    value: float,
    band_upper: Optional[float] = None,
    band_lower: Optional[float] = None,
    metric_type: str = 'latency'
) -> float:
    """
    메트릭 심각도를 0.0~1.0으로 계산

    Returns:
        0.0 = 완전 정상
        1.0 = 매우 위험
    """
```

### 3. calculate_health_score() - 전체 건강 점수 계산

```python
def calculate_health_score(metrics: Dict[str, Dict]) -> int:
    """
    여러 메트릭을 종합하여 0~100점 계산

    가중치:
    - 에러율: 50%
    - 레이턴시: 35%
    - CPU: 15%
    """
```

### 4. classify_state() - 상태 분류

```python
def classify_state(score: int) -> str:
    """
    점수를 3단계 상태로 분류

    Returns:
        'healthy' (0-30점)
        'warning' (31-70점)
        'danger' (71-100점)
    """
```

### 5. generate_coach_message() - 코칭 메시지 생성

```python
def generate_coach_message(state: str, metrics: Dict) -> str:
    """
    상황에 맞는 펭귄 코치 메시지 생성

    Examples:
        healthy: "🎉 완벽해요!"
        warning: "⚠️ 에러가 조금씩 발생하고 있어요..."
        danger: "🚨 위험! 에러율이 급증했어요!"
    """
```

---

## Java로 이식하기

### 1. 데이터 클래스

```java
// ThresholdConfig.java
public class ThresholdConfig {
    private double normal;
    private double warning;
    private double danger;

    // Constructor, Getters, Setters
}

// MetricData.java
public class MetricData {
    private double value;
    private Double bandUpper;  // nullable
    private Double bandLower;  // nullable

    // Constructor, Getters, Setters
}
```

### 2. 서비스 클래스

```java
@Service
public class HealthScoreService {

    // Fallback 임계값 (Python의 FALLBACK_THRESHOLDS)
    private static final Map<String, ThresholdConfig> FALLBACK_THRESHOLDS = Map.of(
        "error_rate", new ThresholdConfig(1.0, 5.0, 10.0),
        "latency", new ThresholdConfig(300.0, 700.0, 1500.0),
        "cpu", new ThresholdConfig(50.0, 80.0, 95.0)
    );

    // 메트릭 가중치 (Python의 METRIC_WEIGHTS)
    private static final Map<String, Double> METRIC_WEIGHTS = Map.of(
        "error_rate", 0.50,
        "latency", 0.35,
        "cpu", 0.15
    );

    // Python의 calculate_severity() 이식
    public double calculateSeverity(double value, Double bandUpper,
                                   Double bandLower, String metricType) {
        // Anomaly Detection Band가 있는 경우
        if (bandUpper != null && bandLower != null) {
            if (value >= bandLower && value <= bandUpper) {
                return 0.0;
            }

            double deviation = value > bandUpper
                ? (value - bandUpper) / bandUpper
                : (bandLower - value) / bandLower;

            return Math.min(1.0, deviation * 2.0);
        }

        // Fallback 임계값 사용
        ThresholdConfig threshold = FALLBACK_THRESHOLDS.get(metricType);
        if (threshold == null) return 0.5;

        if (value <= threshold.getNormal()) {
            return 0.0;
        } else if (value <= threshold.getWarning()) {
            double ratio = (value - threshold.getNormal()) /
                          (threshold.getWarning() - threshold.getNormal());
            return ratio * 0.5;
        } else if (value <= threshold.getDanger()) {
            double ratio = (value - threshold.getWarning()) /
                          (threshold.getDanger() - threshold.getWarning());
            return 0.5 + (ratio * 0.3);
        } else {
            double ratio = Math.min(1.0,
                (value - threshold.getDanger()) / threshold.getDanger());
            return 0.8 + (ratio * 0.2);
        }
    }

    // Python의 calculate_health_score() 이식
    public int calculateHealthScore(Map<String, MetricData> metrics) {
        double totalScore = 0.0;
        double totalWeight = 0.0;

        for (Map.Entry<String, Double> entry : METRIC_WEIGHTS.entrySet()) {
            String metricName = entry.getKey();
            double weight = entry.getValue();

            MetricData metricData = metrics.get(metricName);
            if (metricData == null) continue;

            double severity = calculateSeverity(
                metricData.getValue(),
                metricData.getBandUpper(),
                metricData.getBandLower(),
                metricName
            );

            totalScore += severity * weight * 100;
            totalWeight += weight;
        }

        int finalScore = totalWeight > 0
            ? (int) (totalScore / totalWeight)
            : 50;

        return Math.max(0, Math.min(100, finalScore));
    }

    // Python의 classify_state() 이식
    public String classifyState(int score) {
        if (score <= 30) {
            return "healthy";
        } else if (score <= 70) {
            return "warning";
        } else {
            return "danger";
        }
    }

    // Python의 generate_coach_message() 이식
    public String generateCoachMessage(String state,
                                      Map<String, MetricData> metrics) {
        if ("healthy".equals(state)) {
            List<String> messages = List.of(
                "🎉 완벽해요! 모든 지표가 정상이에요!",
                "👍 아주 안정적이에요! 지금 상태로도 충분해요!",
                "✨ 훌륭한 배포에요! 펭귄이 춤추고 있어요!"
            );
            return messages.get(new Random().nextInt(messages.size()));
        }

        // 문제 메트릭 식별
        List<ProblemMetric> problems = identifyProblemMetrics(metrics);

        if ("warning".equals(state)) {
            return generateWarningMessage(problems);
        }

        if ("danger".equals(state)) {
            return generateDangerMessage(problems);
        }

        return "펭귄이 상태를 분석하고 있어요...";
    }
}
```

### 3. 메시지 생성

```java
private String generateWarningMessage(List<ProblemMetric> problems) {
    if (problems.isEmpty()) {
        return "⚠️ 조금 불안정해 보여요. 모니터링을 계속 지켜봐주세요!";
    }

    String worstMetric = problems.get(0).getMetricName();

    Map<String, String> messages = Map.of(
        "latency", "⚠️ 응답 속도가 약간 느려지고 있어요. DB 쿼리나 외부 API를 확인해보면 좋아요!",
        "cpu", "⚠️ CPU 사용률이 높아지고 있어요. 트래픽이 증가했거나 무거운 작업이 실행 중일 수 있어요!",
        "error_rate", "⚠️ 에러가 조금씩 발생하고 있어요. 로그를 확인해서 원인을 파악해보세요!"
    );

    return messages.getOrDefault(worstMetric,
        "⚠️ 일부 지표가 평소와 다릅니다. 주의 깊게 모니터링해주세요!");
}

private String generateDangerMessage(List<ProblemMetric> problems) {
    if (problems.isEmpty()) {
        return "🚨 위험한 상태에요! 즉시 점검이 필요해요!";
    }

    List<String> messages = new ArrayList<>();

    for (ProblemMetric problem : problems) {
        if (problem.getSeverity() < 0.7) continue;

        switch (problem.getMetricName()) {
            case "error_rate":
                messages.add("에러율이 급증했어요!");
                break;
            case "latency":
                messages.add("응답이 매우 느려요!");
                break;
            case "cpu":
                messages.add("CPU가 과부하 상태에요!");
                break;
        }
    }

    if (messages.isEmpty()) {
        return "🚨 서비스 상태가 불안정해요! 즉시 확인이 필요합니다!";
    }

    String worstMetric = problems.get(0).getMetricName();
    String mainMessage = String.join(" ", messages);

    Map<String, String> advice = Map.of(
        "error_rate", "최근 배포 내역을 확인하고, 에러 로그를 점검하세요!",
        "latency", "DB 연결 상태와 외부 API 응답 시간을 점검하세요!",
        "cpu", "오토스케일링을 고려하거나, 불필요한 프로세스를 종료하세요!"
    );

    return String.format("🚨 %s %s",
        mainMessage,
        advice.getOrDefault(worstMetric, "시스템 리소스와 최근 변경사항을 확인하세요!"));
}
```

---

## 테스트

### 1. 단위 테스트 실행

```bash
pytest test_score.py -v
```

### 2. 테스트 커버리지

```bash
pytest test_score.py --cov=score --cov-report=html
```

### 3. 개별 함수 테스트

```python
# test_manual.py
from score import calculate_severity, calculate_health_score

# Severity 테스트
severity = calculate_severity(
    value=850,
    band_upper=600,
    band_lower=200,
    metric_type='latency'
)
print(f"Severity: {severity}")  # 0.833...

# Health Score 테스트
metrics = {
    'error_rate': {'value': 3.5},
    'latency': {'value': 550, 'band_upper': 600, 'band_lower': 200},
    'cpu': {'value': 72}
}
score = calculate_health_score(metrics)
print(f"Score: {score}")  # 40~60 사이
```

---

## Fallback 임계값 커스터마이징

임계값을 조정하고 싶다면 `score.py`의 상수를 수정하세요:

```python
FALLBACK_THRESHOLDS = {
    'error_rate': ThresholdConfig(
        normal=1.0,    # 1% 이하 정상 → 2.0으로 변경?
        warning=5.0,   # 5% 이하 주의
        danger=10.0    # 10% 초과 위험
    ),
    'latency': ThresholdConfig(
        normal=300,    # 300ms 이하 정상 → 500으로 변경?
        warning=700,   # 700ms 이하 주의
        danger=1500    # 1500ms 초과 위험
    ),
    'cpu': ThresholdConfig(
        normal=50,     # 50% 이하 정상
        warning=80,    # 80% 이하 주의
        danger=95      # 95% 초과 위험
    )
}
```

---

## 문제 해결

### Q: `ModuleNotFoundError: No module named 'boto3'`
```bash
pip install boto3
```

### Q: 테스트가 실패합니다
```bash
# pytest 설치 확인
pip install pytest

# 테스트 재실행
pytest test_score.py -v
```

### Q: Java로 이식할 때 결과가 다릅니다
- 부동소수점 정밀도 확인
- Python의 `min(1.0, ...)` → Java의 `Math.min(1.0, ...)`
- 정수 나눗셈 주의: Java는 `(int)/(int)` = int, Python은 float

---

## 라이센스

MIT License

---

## 작성자

이승규 (Penguin-Land 프로젝트)

해커톤 화이팅! 🐧🏆
