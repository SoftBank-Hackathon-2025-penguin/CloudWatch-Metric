# 🐧 Penguin-Land API 스펙 문서

**버전**: 1.0
**최종 수정**: 2025-11-20
**담당**: 이승규

---

## 📋 목차

1. [SNS → Backend Webhook](#1-sns--backend-webhook)
2. [Backend → Frontend API](#2-backend--frontend-api)
3. [데이터 모델](#3-데이터-모델)
4. [에러 처리](#4-에러-처리)
5. [시뮬레이션 API](#5-시뮬레이션-api)

---

## 1. SNS → Backend Webhook

### 1.1 개요

CloudWatch Alarm이 발생하면 SNS가 Backend Webhook으로 알림을 전송합니다.

### 1.2 Endpoint

```http
POST /api/cloudwatch/alarm
Content-Type: application/json
```

### 1.3 SNS 메시지 형식

#### HTTP Headers
```http
x-amz-sns-message-type: Notification
x-amz-sns-topic-arn: arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms
```

#### Request Body
```json
{
  "Type": "Notification",
  "MessageId": "abc-123-def-456",
  "TopicArn": "arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms",
  "Subject": "ALARM: penguin-land-latency-anomaly in Asia Pacific (Seoul)",
  "Message": "{\"AlarmName\":\"penguin-land-latency-anomaly\",\"AlarmDescription\":\"Latency exceeded anomaly detection band\",\"AWSAccountId\":\"123456789\",\"AlarmConfigurationUpdatedTimestamp\":\"2025-11-20T14:25:00.000+0000\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint [850.0 (20/11/25 14:30:00)] was greater than the upper threshold (ANOMALY_DETECTION_BAND).\",\"StateChangeTime\":\"2025-11-20T14:30:00.000+0000\",\"Region\":\"Asia Pacific (Seoul)\",\"AlarmArn\":\"arn:aws:cloudwatch:ap-northeast-2:123456789:alarm:penguin-land-latency-anomaly\",\"OldStateValue\":\"OK\",\"OKActions\":[],\"AlarmActions\":[\"arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms\"],\"InsufficientDataActions\":[],\"Trigger\":{\"MetricName\":\"TargetResponseTime\",\"Namespace\":\"AWS/ApplicationELB\",\"StatisticType\":\"Statistic\",\"Statistic\":\"p90\",\"Unit\":null,\"Dimensions\":[{\"value\":\"app/penguin-land-alb/abc123def456\",\"name\":\"LoadBalancer\"}],\"Period\":300,\"EvaluationPeriods\":1,\"DatapointsToAlarm\":1,\"ComparisonOperator\":\"LessThanLowerOrGreaterThanUpperThreshold\",\"Threshold\":null,\"TreatMissingData\":\"notBreaching\",\"EvaluateLowSampleCountPercentile\":\"\"}}",
  "Timestamp": "2025-11-20T14:30:00.000Z",
  "SignatureVersion": "1",
  "Signature": "...",
  "SigningCertURL": "...",
  "UnsubscribeURL": "..."
}
```

### 1.4 Message 필드 파싱

`Message` 필드는 JSON 문자열이므로 파싱 필요:

```json
{
  "AlarmName": "penguin-land-latency-anomaly",
  "AlarmDescription": "Latency exceeded anomaly detection band",
  "NewStateValue": "ALARM",
  "NewStateReason": "Threshold Crossed: 1 datapoint [850.0] was greater than upper threshold",
  "StateChangeTime": "2025-11-20T14:30:00.000+0000",
  "OldStateValue": "OK",
  "Trigger": {
    "MetricName": "TargetResponseTime",
    "Namespace": "AWS/ApplicationELB",
    "Statistic": "p90",
    "Period": 300,
    "Dimensions": [
      {
        "name": "LoadBalancer",
        "value": "app/penguin-land-alb/abc123"
      }
    ]
  }
}
```

### 1.5 메트릭 값 추출

#### NewStateReason에서 값 추출
```
"Threshold Crossed: 1 datapoint [850.0 (20/11/25 14:30:00)] was greater than..."
```

정규표현식:
```java
Pattern pattern = Pattern.compile("\\[(\\d+\\.?\\d*)");
Matcher matcher = pattern.matcher(newStateReason);
if (matcher.find()) {
    double value = Double.parseDouble(matcher.group(1));  // 850.0
}
```

### 1.6 Backend 응답

```http
200 OK
Content-Type: application/json

{
  "success": true,
  "message": "Alarm processed successfully",
  "alarm_id": "alarm-abc-123"
}
```

---

## 2. Backend → Frontend API

### 2.1 배포 상태 조회

#### Endpoint
```http
GET /api/deployment/status?session_id={session_id}
```

#### Query Parameters
| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| session_id | string | Y | 배포 세션 ID |

#### Response (200 OK)
```json
{
  "session_id": "session-abc-123",
  "deployment_status": "COMPLETE",
  "health_score": 45,
  "health_state": "warning",
  "coach_message": "⚠️ 에러율과 CPU가 약간 높아지고 있어요!",
  "penguin_animation": "worried",
  "metrics": {
    "error_rate": {
      "value": 2.5,
      "unit": "percent",
      "band_upper": 3.0,
      "band_lower": 0.5,
      "state": "warning",
      "severity": 0.6
    },
    "latency": {
      "value": 450,
      "unit": "milliseconds",
      "band_upper": 600,
      "band_lower": 200,
      "state": "healthy",
      "severity": 0.0
    },
    "cpu": {
      "value": 65,
      "unit": "percent",
      "band_upper": null,
      "band_lower": null,
      "state": "warning",
      "severity": 0.5
    }
  },
  "problem_metrics": [
    {
      "metric": "error_rate",
      "severity": 0.6
    },
    {
      "metric": "cpu",
      "severity": 0.5
    }
  ],
  "last_updated": "2025-11-20T14:30:00Z",
  "timestamp": "2025-11-20T14:30:00Z"
}
```

#### 필드 설명

| 필드 | 타입 | 설명 |
|------|------|------|
| deployment_status | string | `INIT`, `PLANNING`, `APPLYING`, `COMPLETE`, `FAILED`, `DESTROYING` |
| health_score | integer | 0~100 점수 (0=완벽, 100=위험) |
| health_state | string | `healthy`, `warning`, `danger` |
| penguin_animation | string | `happy`, `worried`, `crying` |

### 2.2 배포 히스토리 조회

#### Endpoint
```http
GET /api/deployment/history?user_id={user_id}&limit={limit}
```

#### Query Parameters
| 파라미터 | 타입 | 필수 | 기본값 | 설명 |
|---------|------|------|--------|------|
| user_id | string | Y | - | 사용자 ID |
| limit | integer | N | 10 | 조회 개수 |

#### Response (200 OK)
```json
{
  "user_id": "user-123",
  "total_deployments": 47,
  "deployments": [
    {
      "session_id": "session-abc-123",
      "timestamp": "2025-11-20T14:30:00Z",
      "final_score": 15,
      "final_state": "healthy",
      "duration": "2m 30s",
      "terraform_status": "COMPLETE"
    },
    {
      "session_id": "session-abc-122",
      "timestamp": "2025-11-20T12:00:00Z",
      "final_score": 55,
      "final_state": "warning",
      "duration": "3m 15s",
      "terraform_status": "COMPLETE"
    }
  ],
  "stats": {
    "success_rate": 0.94,
    "average_score": 23,
    "best_score": 5,
    "worst_score": 85,
    "current_streak": 8
  }
}
```

---

## 3. 데이터 모델

### 3.1 MetricSnapshot

```json
{
  "timestamp": "2025-11-20T14:30:00Z",
  "session_id": "session-abc-123",
  "user_id": "user-123",
  "metrics": {
    "error_rate": {
      "value": 2.5,
      "unit": "percent",
      "band_upper": 3.0,
      "band_lower": 0.5,
      "state": "warning",
      "severity": 0.6
    },
    "latency": {
      "value": 450,
      "unit": "milliseconds",
      "band_upper": 600,
      "band_lower": 200,
      "state": "healthy",
      "severity": 0.0
    },
    "cpu": {
      "value": 65,
      "unit": "percent",
      "band_upper": null,
      "band_lower": null,
      "state": "warning",
      "severity": 0.5
    }
  },
  "overall_score": 45,
  "overall_state": "warning",
  "coach_message": "⚠️ 에러율과 CPU가 약간 높아지고 있어요!"
}
```

### 3.2 AlarmRecord

```json
{
  "alarm_id": "alarm-abc-123",
  "session_id": "session-abc-123",
  "alarm_name": "penguin-land-latency-anomaly",
  "metric_name": "TargetResponseTime",
  "namespace": "AWS/ApplicationELB",
  "new_state": "ALARM",
  "old_state": "OK",
  "metric_value": 850.0,
  "band_upper": 600.0,
  "band_lower": 200.0,
  "state_change_time": "2025-11-20T14:30:00Z",
  "raw_message": "{...}",
  "created_at": "2025-11-20T14:30:01Z"
}
```

### 3.3 DeploymentRecord

```json
{
  "session_id": "session-abc-123",
  "user_id": "user-123",
  "deployment_status": "COMPLETE",
  "terraform_status": "COMPLETE",
  "health_score": 15,
  "health_state": "healthy",
  "start_time": "2025-11-20T14:25:00Z",
  "end_time": "2025-11-20T14:27:30Z",
  "duration": "2m 30s",
  "created_at": "2025-11-20T14:25:00Z",
  "updated_at": "2025-11-20T14:30:00Z"
}
```

---

## 4. 에러 처리

### 4.1 에러 응답 형식

```json
{
  "success": false,
  "error": {
    "code": "INVALID_SESSION_ID",
    "message": "The provided session ID is invalid or not found",
    "details": "session_id: session-xyz-999 does not exist",
    "timestamp": "2025-11-20T14:30:00Z"
  }
}
```

### 4.2 에러 코드

| 코드 | HTTP Status | 설명 |
|------|-------------|------|
| `INVALID_SESSION_ID` | 404 | 세션 ID를 찾을 수 없음 |
| `INVALID_REQUEST` | 400 | 잘못된 요청 형식 |
| `ALARM_PARSE_ERROR` | 400 | SNS 메시지 파싱 실패 |
| `METRIC_NOT_FOUND` | 404 | 메트릭 데이터 없음 |
| `INTERNAL_ERROR` | 500 | 서버 내부 오류 |
| `DYNAMODB_ERROR` | 500 | DynamoDB 작업 실패 |

---

## 5. 시뮬레이션 API

### 5.1 시뮬레이션 트리거

데모 시연을 위한 API

#### Endpoint
```http
POST /api/cloudwatch/simulate
Content-Type: application/json
```

#### Request Body
```json
{
  "session_id": "session-abc-123",
  "metric": "latency",
  "severity": "danger",
  "duration_seconds": 30
}
```

#### Parameters
| 필드 | 타입 | 필수 | 값 | 설명 |
|------|------|------|-----|------|
| session_id | string | Y | - | 세션 ID |
| metric | string | Y | `error_rate`, `latency`, `cpu`, `all` | 시뮬레이션할 메트릭 |
| severity | string | Y | `warning`, `danger` | 심각도 |
| duration_seconds | integer | N | 30 (기본값) | 지속 시간 |

#### Response (200 OK)
```json
{
  "success": true,
  "simulation_id": "sim-123",
  "session_id": "session-abc-123",
  "message": "시뮬레이션이 시작되었습니다. 30초 후 자동 종료됩니다.",
  "simulated_values": {
    "latency": {
      "original_value": 350,
      "simulated_value": 2500
    }
  },
  "estimated_score": 85,
  "estimated_state": "danger",
  "auto_recover_at": "2025-11-20T14:30:30Z"
}
```

### 5.2 시뮬레이션 종료

자동으로 종료되지만 수동 종료도 가능

#### Endpoint
```http
POST /api/cloudwatch/simulate/stop
Content-Type: application/json
```

#### Request Body
```json
{
  "simulation_id": "sim-123"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "message": "시뮬레이션이 종료되었습니다.",
  "simulation_id": "sim-123",
  "actual_duration": "15s"
}
```

---

## 6. DynamoDB 테이블 스키마

### 6.1 penguin-land-deployments

| 속성 | 타입 | 키 | 설명 |
|------|------|-----|------|
| session_id | String | PK | 세션 ID |
| timestamp | String | SK | ISO 8601 타임스탬프 |
| user_id | String | - | 사용자 ID |
| deployment_status | String | - | 배포 상태 |
| health_score | Number | - | 건강 점수 |
| health_state | String | - | 건강 상태 |
| metrics | Map | - | 메트릭 데이터 |
| coach_message | String | - | 코칭 메시지 |
| created_at | String | - | 생성 시간 |
| updated_at | String | - | 수정 시간 |

#### GSI: user-index
- PK: `user_id`
- SK: `timestamp`

### 6.2 penguin-land-alarms

| 속성 | 타입 | 키 | 설명 |
|------|------|-----|------|
| alarm_id | String | PK | 알람 ID (UUID) |
| timestamp | String | SK | 발생 시간 |
| session_id | String | - | 세션 ID |
| alarm_name | String | - | 알람 이름 |
| metric_name | String | - | 메트릭 이름 |
| new_state | String | - | 새 상태 (ALARM/OK) |
| metric_value | Number | - | 메트릭 값 |
| band_upper | Number | - | 상한 밴드 |
| band_lower | Number | - | 하한 밴드 |
| raw_message | String | - | 원본 SNS 메시지 |

#### GSI: session-index
- PK: `session_id`
- SK: `timestamp`

---

## 7. WebSocket (선택적)

실시간 업데이트를 위한 WebSocket 연결

### 7.1 연결
```javascript
const ws = new WebSocket('ws://your-backend.com/ws/deployment');
```

### 7.2 메시지 형식

#### Server → Client
```json
{
  "type": "health_update",
  "session_id": "session-abc-123",
  "score": 55,
  "state": "warning",
  "message": "⚠️ 주의 필요!",
  "timestamp": "2025-11-20T14:30:05Z"
}
```

#### Client → Server (Ping)
```json
{
  "type": "ping",
  "session_id": "session-abc-123"
}
```

---

## 8. 구현 예시 (Java Spring Boot)

### 8.1 SNS Webhook Controller

```java
@RestController
@RequestMapping("/api/cloudwatch")
public class CloudWatchController {

    @PostMapping("/alarm")
    public ResponseEntity<Map<String, Object>> handleAlarm(@RequestBody String snsMessage) {
        try {
            // SNS 메시지 파싱
            ObjectMapper mapper = new ObjectMapper();
            JsonNode rootNode = mapper.readTree(snsMessage);

            String messageType = rootNode.path("Type").asText();

            // 구독 확인 처리
            if ("SubscriptionConfirmation".equals(messageType)) {
                String subscribeURL = rootNode.path("SubscribeURL").asText();
                // 구독 확인 URL 호출
                confirmSubscription(subscribeURL);
                return ResponseEntity.ok(Map.of("success", true));
            }

            // 알람 메시지 파싱
            String message = rootNode.path("Message").asText();
            JsonNode alarmData = mapper.readTree(message);

            String alarmName = alarmData.path("AlarmName").asText();
            String newState = alarmData.path("NewStateValue").asText();

            // 메트릭 값 추출
            String reason = alarmData.path("NewStateReason").asText();
            double metricValue = extractMetricValue(reason);

            // Python 로직 적용 (점수 계산)
            int healthScore = calculateHealthScore(metricValue, alarmName);

            // DynamoDB 저장
            saveAlarmRecord(alarmData, healthScore);

            return ResponseEntity.ok(Map.of(
                "success", true,
                "alarm_id", UUID.randomUUID().toString()
            ));

        } catch (Exception e) {
            return ResponseEntity.status(500).body(Map.of(
                "success", false,
                "error", e.getMessage()
            ));
        }
    }

    private double extractMetricValue(String reason) {
        Pattern pattern = Pattern.compile("\\[(\\d+\\.?\\d*)");
        Matcher matcher = pattern.matcher(reason);
        if (matcher.find()) {
            return Double.parseDouble(matcher.group(1));
        }
        return 0.0;
    }
}
```

### 8.2 점수 계산 서비스 (Python 로직 이식)

```java
@Service
public class HealthScoreService {

    // Fallback 임계값
    private static final Map<String, ThresholdConfig> FALLBACK_THRESHOLDS = Map.of(
        "error_rate", new ThresholdConfig(1.0, 5.0, 10.0),
        "latency", new ThresholdConfig(300.0, 700.0, 1500.0),
        "cpu", new ThresholdConfig(50.0, 80.0, 95.0)
    );

    // 메트릭 가중치
    private static final Map<String, Double> METRIC_WEIGHTS = Map.of(
        "error_rate", 0.50,
        "latency", 0.35,
        "cpu", 0.15
    );

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

    private double calculateSeverity(double value, Double bandUpper,
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
}
```

---

## 9. 테스트

### 9.1 SNS 메시지 테스트

```bash
# 테스트 메시지 전송
curl -X POST http://localhost:8080/api/cloudwatch/alarm \
  -H "Content-Type: application/json" \
  -d @test_sns_message.json
```

### 9.2 상태 조회 테스트

```bash
# 배포 상태 조회
curl http://localhost:8080/api/deployment/status?session_id=session-123
```

### 9.3 시뮬레이션 테스트

```bash
# 위험 상태 시뮬레이션
curl -X POST http://localhost:8080/api/cloudwatch/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "session-123",
    "metric": "all",
    "severity": "danger",
    "duration_seconds": 30
  }'
```

---

## 부록: 메트릭 매핑

| Python 이름 | CloudWatch 메트릭 | Namespace |
|-------------|-------------------|-----------|
| error_rate | HTTPCode_Target_5XX_Count | AWS/ApplicationELB |
| latency | TargetResponseTime (p90) | AWS/ApplicationELB |
| cpu | CPUUtilization | AWS/EC2 |

---

**문서 작성**: 이승규
**검토 필요**: Backend 팀 (Spring Boot), Frontend 팀 (Next.js)
