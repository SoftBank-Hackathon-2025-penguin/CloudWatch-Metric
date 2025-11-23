# 📨 Java에서 Slack 메시지 보내기 - 완벽 가이드

Python 백엔드의 Slack 알림 기능을 Java로 구현하는 방법입니다.

---

## 🎯 SlackService.java 구현

### 1. Slack 서비스 클래스

```java
package com.penguin.healthscore.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;

@Slf4j
@Service
public class SlackService {

    @Value("${slack.webhook-url}")
    private String slackWebhookUrl;

    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    private static final DateTimeFormatter FORMATTER =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
            .withZone(ZoneId.of("UTC"));

    public SlackService() {
        this.webClient = WebClient.builder()
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Slack으로 건강 점수 경보 전송 (70점 이상일 때만)
     */
    public void sendHealthAlert(int healthScore, String healthState,
                               String coachMessage, Map<String, Double> metrics) {

        // 🔕 Slack 알림 비활성화 (필요시 이 return 제거)
        // return;

        // 70점 미만이면 전송 안 함
        if (healthScore < 70) {
            return;
        }

        // Webhook URL이 없으면 전송 안 함
        if (slackWebhookUrl == null || slackWebhookUrl.isEmpty()) {
            log.warn("⚠️ Slack Webhook URL이 설정되지 않았습니다!");
            return;
        }

        // 상태별 이모지
        String emoji = getEmojiForState(healthState);

        // Slack Block Kit 메시지 생성
        Map<String, Object> message = createSlackMessage(
            emoji, healthScore, healthState, coachMessage, metrics
        );

        try {
            // HTTP POST 요청
            webClient.post()
                .uri(slackWebhookUrl)
                .bodyValue(message)
                .retrieve()
                .bodyToMono(String.class)
                .subscribe(
                    response -> log.info("✅ Slack 알림 전송! (점수: {}점)", healthScore),
                    error -> log.error("❌ Slack 알림 실패: {}", error.getMessage())
                );

        } catch (Exception e) {
            log.error("❌ Slack 오류: {}", e.getMessage());
        }
    }

    /**
     * Slack Block Kit 메시지 생성
     */
    private Map<String, Object> createSlackMessage(String emoji, int healthScore,
                                                   String healthState, String coachMessage,
                                                   Map<String, Double> metrics) {
        List<Map<String, Object>> blocks = new ArrayList<>();

        // 헤더 블록
        blocks.add(Map.of(
            "type", "header",
            "text", Map.of(
                "type", "plain_text",
                "text", emoji + " Penguin-Land 배포 경보!"
            )
        ));

        // 점수 및 상태 블록
        blocks.add(Map.of(
            "type", "section",
            "fields", Arrays.asList(
                Map.of("type", "mrkdwn", "text", "*점수:*\n" + healthScore + "/100점"),
                Map.of("type", "mrkdwn", "text", "*상태:*\n" + healthState.toUpperCase())
            )
        ));

        // 메시지 블록
        blocks.add(Map.of(
            "type", "section",
            "text", Map.of(
                "type", "mrkdwn",
                "text", "*메시지:*\n" + coachMessage
            )
        ));

        // 구분선
        blocks.add(Map.of("type", "divider"));

        // 메트릭 상세 정보
        blocks.add(Map.of(
            "type", "section",
            "fields", Arrays.asList(
                Map.of("type", "mrkdwn",
                       "text", "*에러율:*\n" + String.format("%.2f%%", metrics.get("errorRate"))),
                Map.of("type", "mrkdwn",
                       "text", "*응답시간:*\n" + String.format("%.0fms", metrics.get("latency"))),
                Map.of("type", "mrkdwn",
                       "text", "*CPU:*\n" + String.format("%.0f%%", metrics.get("cpu")))
            )
        ));

        // 타임스탬프
        blocks.add(Map.of(
            "type", "context",
            "elements", Collections.singletonList(
                Map.of("type", "mrkdwn",
                       "text", "🕐 " + FORMATTER.format(Instant.now()) + " UTC")
            )
        ));

        return Map.of("blocks", blocks);
    }

    /**
     * 상태별 이모지 반환
     */
    private String getEmojiForState(String healthState) {
        return switch (healthState.toLowerCase()) {
            case "healthy" -> "✅";
            case "warning" -> "⚠️";
            case "danger" -> "🚨";
            default -> "⚠️";
        };
    }
}
```

---

## 📝 의존성 추가

### Maven (`pom.xml`)

```xml
<!-- WebFlux (HTTP Client용) -->
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-webflux</artifactId>
</dependency>

<!-- Jackson (JSON 처리) -->
<dependency>
    <groupId>com.fasterxml.jackson.core</groupId>
    <artifactId>jackson-databind</artifactId>
</dependency>
```

### Gradle (`build.gradle`)

```gradle
implementation 'org.springframework.boot:spring-boot-starter-webflux'
implementation 'com.fasterxml.jackson.core:jackson-databind'
```

---

## 🔧 Controller에서 사용하기

### MonitoringController.java 수정

```java
@RestController
@RequiredArgsConstructor
public class MonitoringController {

    private final SlackService slackService;  // 추가!
    // ... 기존 코드

    @GetMapping("/monitoring")
    public ResponseEntity<MonitoringResponse> getMonitoring() {
        // ... 메트릭 가져오기

        // 점수 계산
        HealthResult result = healthScoreService.analyzeDeploymentHealth(metrics);

        // 🚨 Slack 알림 전송!
        slackService.sendHealthAlert(
            result.getHealthScore(),
            result.getHealthState(),
            result.getCoachMessage(),
            Map.of(
                "errorRate", metrics.getErrorRate(),
                "latency", metrics.getLatency(),
                "cpu", metrics.getCpu()
            )
        );

        // ... 응답 반환
    }
}
```

---

## 🎭 시나리오별 테스트

### 테스트 컨트롤러 추가

```java
package com.penguin.healthscore.controller;

import com.penguin.healthscore.model.HealthMetrics;
import com.penguin.healthscore.model.HealthResult;
import com.penguin.healthscore.service.HealthScoreService;
import com.penguin.healthscore.service.SlackService;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/test")
@RequiredArgsConstructor
public class TestController {

    private final HealthScoreService healthScoreService;
    private final SlackService slackService;

    /**
     * 시나리오 1: Healthy - 정상 배포
     */
    @PostMapping("/scenario/1")
    public Map<String, Object> testScenario1() {
        HealthMetrics metrics = new HealthMetrics(2.0, 850.0, 60.0);
        HealthResult result = healthScoreService.analyzeDeploymentHealth(metrics);

        slackService.sendHealthAlert(
            result.getHealthScore(),
            result.getHealthState(),
            result.getCoachMessage(),
            Map.of("errorRate", 2.0, "latency", 850.0, "cpu", 60.0)
        );

        return Map.of(
            "scenario", "Healthy - 정상 배포",
            "score", result.getHealthScore(),
            "state", result.getHealthState(),
            "message", result.getCoachMessage()
        );
    }

    /**
     * 시나리오 2: Warning - 주의 필요
     */
    @PostMapping("/scenario/2")
    public Map<String, Object> testScenario2() {
        HealthMetrics metrics = new HealthMetrics(5.0, 1200.0, 82.0);
        HealthResult result = healthScoreService.analyzeDeploymentHealth(metrics);

        slackService.sendHealthAlert(
            result.getHealthScore(),
            result.getHealthState(),
            result.getCoachMessage(),
            Map.of("errorRate", 5.0, "latency", 1200.0, "cpu", 82.0)
        );

        return Map.of(
            "scenario", "Warning - 주의 필요",
            "score", result.getHealthScore(),
            "state", result.getHealthState(),
            "message", result.getCoachMessage()
        );
    }

    /**
     * 시나리오 3: Danger - 위험!
     */
    @PostMapping("/scenario/3")
    public Map<String, Object> testScenario3() {
        HealthMetrics metrics = new HealthMetrics(10.0, 2500.0, 95.0);
        HealthResult result = healthScoreService.analyzeDeploymentHealth(metrics);

        slackService.sendHealthAlert(
            result.getHealthScore(),
            result.getHealthState(),
            result.getCoachMessage(),
            Map.of("errorRate", 10.0, "latency", 2500.0, "cpu", 95.0)
        );

        return Map.of(
            "scenario", "Danger - 위험 상태!",
            "score", result.getHealthScore(),
            "state", result.getHealthState(),
            "message", result.getCoachMessage()
        );
    }

    /**
     * 시나리오 5: 에러율만 문제
     */
    @PostMapping("/scenario/5")
    public Map<String, Object> testScenario5() {
        HealthMetrics metrics = new HealthMetrics(8.0, 250.0, 40.0);
        HealthResult result = healthScoreService.analyzeDeploymentHealth(metrics);

        slackService.sendHealthAlert(
            result.getHealthScore(),
            result.getHealthState(),
            result.getCoachMessage(),
            Map.of("errorRate", 8.0, "latency", 250.0, "cpu", 40.0)
        );

        return Map.of(
            "scenario", "에러율만 높은 경우",
            "score", result.getHealthScore(),
            "state", result.getHealthState(),
            "message", result.getCoachMessage()
        );
    }

    /**
     * 모든 시나리오 테스트
     */
    @PostMapping("/scenarios/all")
    public Map<String, Object> testAllScenarios() {
        testScenario1();
        try { Thread.sleep(1000); } catch (InterruptedException e) {}

        testScenario2();
        try { Thread.sleep(1000); } catch (InterruptedException e) {}

        testScenario3();
        try { Thread.sleep(1000); } catch (InterruptedException e) {}

        testScenario5();

        return Map.of(
            "message", "✅ 모든 시나리오 테스트 완료!",
            "scenarios_tested", 4
        );
    }
}
```

---

## 🧪 테스트 방법

### 1. Slack Webhook URL 설정

`application.yml`:
```yaml
slack:
  webhook-url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

또는 환경변수:
```bash
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 2. 서버 실행

```bash
mvn spring-boot:run
```

### 3. 시나리오 테스트

```bash
# 시나리오 1: Healthy
curl -X POST http://localhost:8080/test/scenario/1

# 시나리오 2: Warning
curl -X POST http://localhost:8080/test/scenario/2

# 시나리오 3: Danger (Slack 알림 전송됨!)
curl -X POST http://localhost:8080/test/scenario/3

# 시나리오 5: 에러율만 문제 (Slack 알림 전송됨!)
curl -X POST http://localhost:8080/test/scenario/5

# 모든 시나리오 한번에 테스트
curl -X POST http://localhost:8080/test/scenarios/all
```

---

## 📊 Slack 메시지 예시

### Danger 상태 (점수 85점):

```
🚨 Penguin-Land 배포 경보!

점수                  상태
85/100점             DANGER

메시지:
🔥 위험! 여러 지표가 임계치를 초과했어요!

━━━━━━━━━━━━━━━━━━━━━━

에러율              응답시간              CPU
10.00%              2500ms               95%

🕐 2025-11-23 01:30:45 UTC
```

---

## 🔧 Java vs Python 비교

| 기능 | Python | Java |
|------|--------|------|
| **HTTP Client** | `requests.post()` | `WebClient.post()` |
| **JSON 생성** | `dict` | `Map<String, Object>` |
| **비동기** | `async/await` 불필요 | `subscribe()` (Reactive) |
| **타입** | 동적 | 정적 (컴파일 타임 체크) |
| **로깅** | `print()` | `log.info()` (SLF4J) |

---

## ✅ 체크리스트

- [ ] `SlackService.java` 생성
- [ ] `TestController.java` 추가
- [ ] WebFlux 의존성 추가
- [ ] Slack Webhook URL 설정
- [ ] 시나리오 3 테스트 (Slack 알림 확인)
- [ ] 점수 70점 이상일 때만 알림 확인

---

## 💡 추가 팁

1. **비동기 처리**: `WebClient`는 비동기로 동작하므로 서버 성능에 영향 없음
2. **에러 핸들링**: `.subscribe()`의 두 번째 파라미터로 에러 처리
3. **Slack Block Kit**: [공식 Block Kit Builder](https://app.slack.com/block-kit-builder)에서 미리보기 가능
4. **로깅**: `@Slf4j` 어노테이션으로 로그 자동 생성

---

**🎉 이제 Java에서도 Slack 알림을 완벽하게 보낼 수 있습니다!**
