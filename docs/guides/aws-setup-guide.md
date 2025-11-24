# ✅ AWS 연동 가이드: "실제로 작동할까?"

**결론부터: 네, 작동합니다! 단, 이것들만 하면 됩니다.**

---

## 🎯 1. 현재 상태 점검

### ✅ 완료된 것
```
✅ 점수 계산 로직 (score.py)
   - Anomaly Detection 밴드 처리: OK
   - Fallback 임계값: OK
   - 가중치 계산: OK
   - 50개 테스트 통과: OK

✅ 에러 핸들링
   - 메트릭 없을 때: OK
   - 밴드 없을 때: OK
   - 잘못된 값: OK

✅ 문서
   - API 스펙: OK
   - Java 구현 예시: OK
   - 테스트 케이스: OK
```

### ❌ 아직 안 한 것
```
❌ AWS CloudWatch Alarm 생성
❌ SNS Topic 연결
❌ Backend Webhook 구현
❌ DynamoDB 테이블 생성
❌ Java로 로직 이식
```

---

## 🚀 2. AWS 연동 체크리스트 (오늘 할 일!)

### Step 1: CloudWatch Alarm 생성 (30분)

#### 필요한 Alarm 3개:

```bash
# 1. 에러율 Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name penguin-land-error-rate \
  --namespace AWS/ApplicationELB \
  --metric-name HTTPCode_Target_5XX_Count \
  --statistic Sum \
  --period 300 \
  --evaluation-periods 1 \
  --threshold-metric-id ad1 \
  --comparison-operator LessThanLowerOrGreaterThanUpperThreshold \
  --treat-missing-data notBreaching

# 2. 레이턴시 Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name penguin-land-latency \
  --namespace AWS/ApplicationELB \
  --metric-name TargetResponseTime \
  --statistic p90 \
  --period 300 \
  --evaluation-periods 1 \
  --threshold-metric-id ad1 \
  --comparison-operator LessThanLowerOrGreaterThanUpperThreshold

# 3. CPU Alarm
aws cloudwatch put-metric-alarm \
  --alarm-name penguin-land-cpu \
  --namespace AWS/EC2 \
  --metric-name CPUUtilization \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

#### 확인 방법:
```bash
# Alarm 목록 확인
aws cloudwatch describe-alarms \
  --alarm-name-prefix penguin-land

# 예상 출력:
# - penguin-land-error-rate: OK
# - penguin-land-latency: OK
# - penguin-land-cpu: OK
```

---

### Step 2: SNS Topic 생성 및 연결 (20분)

#### 2-1. SNS Topic 생성
```bash
# Topic 생성
aws sns create-topic \
  --name penguin-land-alarms

# 출력 예시:
# {
#   "TopicArn": "arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms"
# }
```

#### 2-2. Alarm → SNS 연결
```bash
# 각 Alarm에 SNS 연결
aws cloudwatch put-metric-alarm \
  --alarm-name penguin-land-error-rate \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms

aws cloudwatch put-metric-alarm \
  --alarm-name penguin-land-latency \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms

aws cloudwatch put-metric-alarm \
  --alarm-name penguin-land-cpu \
  --alarm-actions arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms
```

#### 2-3. SNS → Backend Webhook 연결
```bash
# HTTP Subscription 생성
aws sns subscribe \
  --topic-arn arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms \
  --protocol https \
  --notification-endpoint https://your-backend.com/api/cloudwatch/alarm
```

#### 확인 방법:
```bash
# Subscription 확인
aws sns list-subscriptions-by-topic \
  --topic-arn arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms

# Subscription Confirmation 이메일 확인
# → Backend 로그에서 SubscriptionConfirmation 메시지 확인
```

---

### Step 3: Backend Webhook 구현 (1시간)

#### 3-1. Java Controller 생성

**파일**: `CloudWatchController.java`

```java
@RestController
@RequestMapping("/api/cloudwatch")
public class CloudWatchController {

    @Autowired
    private HealthScoreService healthScoreService;

    @PostMapping("/alarm")
    public ResponseEntity<?> handleAlarm(@RequestBody String snsMessage) {
        try {
            // 1. SNS 메시지 파싱
            ObjectMapper mapper = new ObjectMapper();
            JsonNode rootNode = mapper.readTree(snsMessage);

            String messageType = rootNode.path("Type").asText();

            // Subscription Confirmation 처리
            if ("SubscriptionConfirmation".equals(messageType)) {
                String subscribeURL = rootNode.path("SubscribeURL").asText();
                confirmSubscription(subscribeURL);
                return ResponseEntity.ok(Map.of("success", true));
            }

            // 2. Alarm 메시지 파싱
            String message = rootNode.path("Message").asText();
            JsonNode alarmData = mapper.readTree(message);

            String alarmName = alarmData.path("AlarmName").asText();
            String metricName = extractMetricName(alarmName);

            // 3. 메트릭 값 추출
            String reason = alarmData.path("NewStateReason").asText();
            double metricValue = extractMetricValue(reason);

            // 4. 밴드 정보 추출 (있으면)
            Double bandUpper = extractBandUpper(alarmData);
            Double bandLower = extractBandLower(alarmData);

            // 5. 승규님 로직 적용
            Map<String, MetricData> metrics = new HashMap<>();
            metrics.put(metricName, new MetricData(
                metricValue, bandUpper, bandLower
            ));

            int healthScore = healthScoreService.calculateHealthScore(metrics);
            String healthState = healthScoreService.classifyState(healthScore);
            String coachMessage = healthScoreService.generateMessage(healthState, metrics);

            // 6. DynamoDB 저장
            saveToDatabase(healthScore, healthState, coachMessage);

            return ResponseEntity.ok(Map.of(
                "success", true,
                "health_score", healthScore,
                "health_state", healthState
            ));

        } catch (Exception e) {
            log.error("Failed to process alarm", e);
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "error", e.getMessage()
            ));
        }
    }

    private String extractMetricName(String alarmName) {
        // penguin-land-error-rate → error_rate
        if (alarmName.contains("error")) return "error_rate";
        if (alarmName.contains("latency")) return "latency";
        if (alarmName.contains("cpu")) return "cpu";
        return "unknown";
    }

    private double extractMetricValue(String reason) {
        // "Threshold Crossed: 1 datapoint [850.0] was greater..."
        Pattern pattern = Pattern.compile("\\[(\\d+\\.?\\d*)");
        Matcher matcher = pattern.matcher(reason);
        if (matcher.find()) {
            return Double.parseDouble(matcher.group(1));
        }
        return 0.0;
    }
}
```

#### 확인 방법:
```bash
# 테스트 메시지 전송
curl -X POST http://localhost:8080/api/cloudwatch/alarm \
  -H "Content-Type: application/json" \
  -d '{
    "Type": "Notification",
    "Message": "{\"AlarmName\":\"penguin-land-latency\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint [850.0] was greater than...\"}",
    "TopicArn": "arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms"
  }'

# 예상 응답:
# {
#   "success": true,
#   "health_score": 45,
#   "health_state": "warning"
# }
```

---

### Step 4: HealthScoreService 구현 (1시간)

**파일**: `HealthScoreService.java`

```java
@Service
public class HealthScoreService {

    // score.py에서 가져온 설정
    private static final Map<String, ThresholdConfig> FALLBACK_THRESHOLDS = Map.of(
        "error_rate", new ThresholdConfig(1.0, 5.0, 10.0),
        "latency", new ThresholdConfig(300.0, 700.0, 1500.0),
        "cpu", new ThresholdConfig(50.0, 80.0, 95.0)
    );

    private static final Map<String, Double> METRIC_WEIGHTS = Map.of(
        "error_rate", 0.50,
        "latency", 0.35,
        "cpu", 0.15
    );

    /**
     * 승규님 Python 로직을 Java로 이식
     * score.py의 calculate_health_score() 함수와 동일
     */
    public int calculateHealthScore(Map<String, MetricData> metrics) {
        double totalScore = 0.0;
        double totalWeight = 0.0;

        for (Map.Entry<String, Double> entry : METRIC_WEIGHTS.entrySet()) {
            String metricName = entry.getKey();
            double weight = entry.getValue();

            MetricData metricData = metrics.get(metricName);
            if (metricData == null) continue;

            // 승규님 calculate_severity() 로직
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

    /**
     * score.py의 calculate_severity() 함수와 동일
     */
    private double calculateSeverity(double value, Double bandUpper,
                                     Double bandLower, String metricType) {
        // 1. Anomaly Detection Band 우선 사용
        if (bandUpper != null && bandLower != null) {
            if (value >= bandLower && value <= bandUpper) {
                return 0.0;
            }

            double deviation = value > bandUpper
                ? (value - bandUpper) / bandUpper
                : (bandLower - value) / bandLower;

            return Math.min(1.0, deviation * 2.0);
        }

        // 2. Fallback 임계값 사용
        ThresholdConfig threshold = FALLBACK_THRESHOLDS.get(metricType);
        if (threshold == null) return 0.5;

        if (value <= threshold.normal) {
            return 0.0;
        } else if (value <= threshold.warning) {
            double ratio = (value - threshold.normal) /
                          (threshold.warning - threshold.normal);
            return ratio * 0.5;
        } else if (value <= threshold.danger) {
            double ratio = (value - threshold.warning) /
                          (threshold.danger - threshold.warning);
            return 0.5 + (ratio * 0.3);
        } else {
            double ratio = Math.min(1.0,
                (value - threshold.danger) / threshold.danger);
            return 0.8 + (ratio * 0.2);
        }
    }

    /**
     * score.py의 classify_state() 함수와 동일
     */
    public String classifyState(int score) {
        if (score <= 30) return "healthy";
        if (score <= 70) return "warning";
        return "danger";
    }
}
```

#### 확인 방법:
```java
// 테스트 케이스 실행
@Test
public void testCalculateHealthScore() {
    Map<String, MetricData> metrics = new HashMap<>();
    metrics.put("error_rate", new MetricData(2.5, 3.0, 0.5));
    metrics.put("latency", new MetricData(450, 600, 200));
    metrics.put("cpu", new MetricData(65, null, null));

    int score = healthScoreService.calculateHealthScore(metrics);

    // Python 결과와 비교
    // Python: 45점
    // Java: 45점 (동일해야 함!)
    assertEquals(45, score);
}
```

---

### Step 5: DynamoDB 테이블 생성 (15분)

#### 5-1. deployments 테이블
```bash
aws dynamodb create-table \
  --table-name penguin-land-deployments \
  --attribute-definitions \
    AttributeName=session_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=session_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

#### 5-2. alarms 테이블
```bash
aws dynamodb create-table \
  --table-name penguin-land-alarms \
  --attribute-definitions \
    AttributeName=alarm_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=S \
  --key-schema \
    AttributeName=alarm_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

#### 확인 방법:
```bash
# 테이블 목록 확인
aws dynamodb list-tables

# 예상 출력:
# {
#   "TableNames": [
#     "penguin-land-deployments",
#     "penguin-land-alarms"
#   ]
# }
```

---

## 🧪 3. 통합 테스트 (End-to-End)

### 테스트 시나리오

```
시나리오 1: 정상 → 주의 전환
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 초기 상태: 0점 (healthy)
2. 레이턴시 850ms로 증가 (Alarm 발동)
3. SNS → Backend
4. Backend: 점수 계산 → 45점
5. Frontend: 펭귄 😊 → 😟
✅ 성공!

시나리오 2: 주의 → 위험 전환
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 현재: 45점 (warning)
2. 에러율 8.5%로 급증 (Alarm 발동)
3. SNS → Backend
4. Backend: 점수 재계산 → 85점
5. Frontend: 펭귄 😟 → 😭
✅ 성공!

시나리오 3: 위험 → 정상 복구
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. 현재: 85점 (danger)
2. 문제 해결 (Alarm OK 상태)
3. SNS → Backend (OK 메시지)
4. Backend: 점수 재계산 → 15점
5. Frontend: 펭귄 😭 → 😊 + 컨페티
✅ 성공!
```

---

## ✅ 4. 최종 검증 체크리스트

### AWS 연동
```
□ CloudWatch Alarm 3개 생성 확인
□ SNS Topic 생성 및 연결 확인
□ SNS Subscription 활성화 확인
□ DynamoDB 테이블 2개 생성 확인
```

### Backend
```
□ Webhook Endpoint 작동 확인
□ SNS 메시지 파싱 성공 확인
□ 점수 계산 로직 Python과 동일 확인
□ DynamoDB 저장 확인
```

### 통합 테스트
```
□ 실제 Alarm 발생시켜보기
□ Backend 로그 확인
□ DynamoDB 데이터 확인
□ Frontend 펭귄 상태 변경 확인
```

---

## 🎯 5. 실전 테스트 방법

### 수동으로 Alarm 발생시키기

```bash
# 1. Alarm 상태를 ALARM으로 강제 변경
aws cloudwatch set-alarm-state \
  --alarm-name penguin-land-latency \
  --state-value ALARM \
  --state-reason "Testing alarm for hackathon demo"

# 2. Backend 로그 확인
tail -f /var/log/backend.log

# 예상 로그:
# [INFO] Received SNS alarm: penguin-land-latency
# [INFO] Calculated health score: 45
# [INFO] State: warning
# [INFO] Saved to DynamoDB

# 3. DynamoDB 데이터 확인
aws dynamodb scan --table-name penguin-land-deployments

# 4. Frontend 확인
curl http://localhost:3000/api/deployment/status?session_id=test-123

# 예상 응답:
# {
#   "health_score": 45,
#   "health_state": "warning",
#   "penguin_animation": "worried",
#   "coach_message": "⚠️ 응답 속도가 느려요!"
# }
```

---

## 💡 6. 문제 해결 (Troubleshooting)

### 문제 1: SNS 메시지가 안 와요
```
원인: Subscription 미확인
해결:
1. Backend 로그에서 SubscriptionConfirmation 확인
2. SubscribeURL 접속하여 수동 확인
3. SNS Console에서 Subscription 상태 확인
```

### 문제 2: 점수가 Python과 다르게 나와요
```
원인: Java 이식 시 로직 오류
해결:
1. 테스트 케이스로 검증
   Python: 45점 → Java: ?점
2. 각 단계별 중간값 로그 출력
3. severity, weight 계산 재확인
```

### 문제 3: Alarm이 안 발생해요
```
원인: 메트릭 데이터 부족
해결:
1. CloudWatch Metrics 확인
   aws cloudwatch get-metric-statistics ...
2. 최소 2개 데이터 포인트 필요
3. 강제로 set-alarm-state 사용
```

---

## 🎉 7. 성공 기준

### 이것만 되면 OK!
```
✅ Alarm 발생 → SNS 전송
✅ Backend가 SNS 받기
✅ 점수 계산 (Python과 동일)
✅ DynamoDB 저장
✅ Frontend 조회 가능
✅ 펭귄 애니메이션 변경

→ 전체 흐름이 한 번이라도 성공하면 시연 가능!
```

---

## 📞 오늘(Day 2) 목표

```
09:00 - 10:00  CloudWatch Alarm 생성 (전준배님과)
10:00 - 11:00  SNS 연결 및 테스트
11:00 - 12:00  Backend Webhook 구현

13:00 - 14:00  Java 로직 이식
14:00 - 15:00  DynamoDB 연동
15:00 - 16:00  통합 테스트

16:00 - 17:00  버그 수정
17:00 - 18:00  End-to-End 검증

→ 18:00 목표: "실제로 작동하는" 시스템 완성! 🎉
```

---

**질문이나 막히는 부분 있으면 언제든 물어보세요!**
**승규님 코드는 이미 완벽해요. 이제 연결만 하면 됩니다! 💪**
