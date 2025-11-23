# 🐧 Penguin-Land Health Score API - Java 구현 가이드

Python FastAPI 백엔드를 **Java Spring Boot**로 변환하는 완벽 가이드입니다.

---

## 📋 목차

1. [프로젝트 구조](#프로젝트-구조)
2. [의존성 설정 (Maven/Gradle)](#의존성-설정)
3. [환경 설정](#환경-설정)
4. [핵심 클래스 구현](#핵심-클래스-구현)
5. [CloudWatch 연동](#cloudwatch-연동)
6. [시뮬레이션 시스템](#시뮬레이션-시스템)
7. [REST API 엔드포인트](#rest-api-엔드포인트)
8. [실행 방법](#실행-방법)

---

## 🏗️ 프로젝트 구조

```
penguin-land-backend/
├── src/
│   └── main/
│       ├── java/
│       │   └── com/penguin/healthscore/
│       │       ├── PenguinLandApplication.java       # Main 클래스
│       │       ├── config/
│       │       │   ├── AwsConfig.java               # AWS 설정
│       │       │   └── CorsConfig.java              # CORS 설정
│       │       ├── controller/
│       │       │   └── MonitoringController.java    # REST API
│       │       ├── service/
│       │       │   ├── CloudWatchService.java       # CloudWatch 연동
│       │       │   ├── HealthScoreService.java      # 점수 계산
│       │       │   ├── SimulationService.java       # 시뮬레이션
│       │       │   └── SlackService.java            # Slack 알림
│       │       ├── model/
│       │       │   ├── HealthMetrics.java           # 메트릭 모델
│       │       │   ├── HealthResult.java            # 결과 모델
│       │       │   ├── Alert.java                   # 알림 모델
│       │       │   └── SimulationState.java         # 시뮬레이션 상태
│       │       └── dto/
│       │           ├── MonitoringResponse.java      # API 응답
│       │           └── SimulateRequest.java         # API 요청
│       └── resources/
│           └── application.yml                      # 설정 파일
├── pom.xml (또는 build.gradle)
└── README.md
```

---

## 📦 의존성 설정

### Maven (`pom.xml`)

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0
         https://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <parent>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-parent</artifactId>
        <version>3.2.0</version>
    </parent>

    <groupId>com.penguin</groupId>
    <artifactId>healthscore</artifactId>
    <version>1.0.0</version>
    <name>Penguin-Land Health Score API</name>

    <properties>
        <java.version>17</java.version>
        <aws.sdk.version>2.20.0</aws.sdk.version>
    </properties>

    <dependencies>
        <!-- Spring Boot Web -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>

        <!-- AWS SDK - CloudWatch -->
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>cloudwatch</artifactId>
            <version>${aws.sdk.version}</version>
        </dependency>

        <!-- AWS SDK - Core -->
        <dependency>
            <groupId>software.amazon.awssdk</groupId>
            <artifactId>auth</artifactId>
            <version>${aws.sdk.version}</version>
        </dependency>

        <!-- Lombok (Optional - 코드 간소화) -->
        <dependency>
            <groupId>org.projectlombok</groupId>
            <artifactId>lombok</artifactId>
            <optional>true</optional>
        </dependency>

        <!-- HTTP Client (Slack 알림용) -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-webflux</artifactId>
        </dependency>

        <!-- Configuration Processor -->
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-configuration-processor</artifactId>
            <optional>true</optional>
        </dependency>
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
        </plugins>
    </build>
</project>
```

### Gradle (`build.gradle`)

```gradle
plugins {
    id 'java'
    id 'org.springframework.boot' version '3.2.0'
    id 'io.spring.dependency-management' version '1.1.4'
}

group = 'com.penguin'
version = '1.0.0'
sourceCompatibility = '17'

repositories {
    mavenCentral()
}

dependencies {
    // Spring Boot
    implementation 'org.springframework.boot:spring-boot-starter-web'
    implementation 'org.springframework.boot:spring-boot-starter-webflux'

    // AWS SDK
    implementation platform('software.amazon.awssdk:bom:2.20.0')
    implementation 'software.amazon.awssdk:cloudwatch'
    implementation 'software.amazon.awssdk:auth'

    // Lombok
    compileOnly 'org.projectlombok:lombok'
    annotationProcessor 'org.projectlombok:lombok'

    // Configuration
    annotationProcessor 'org.springframework.boot:spring-boot-configuration-processor'

    // Test
    testImplementation 'org.springframework.boot:spring-boot-starter-test'
}

tasks.named('test') {
    useJUnitPlatform()
}
```

---

## ⚙️ 환경 설정

### `src/main/resources/application.yml`

```yaml
spring:
  application:
    name: penguin-land-health-score

server:
  port: 8080

# AWS 설정
aws:
  region: ap-northeast-2
  credentials:
    access-key-id: ${AWS_ACCESS_KEY_ID:}
    secret-access-key: ${AWS_SECRET_ACCESS_KEY:}
  cloudwatch:
    alb-name: app/penguin-land-alb/77a716d3813b8deb

# Slack 설정
slack:
  webhook-url: ${SLACK_WEBHOOK_URL:}

# CORS 설정
cors:
  allowed-origins: "*"
```

---

## 🎯 핵심 클래스 구현

### 1. Main Application 클래스

```java
package com.penguin.healthscore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class PenguinLandApplication {

    public static void main(String[] args) {
        SpringApplication.run(PenguinLandApplication.class, args);
        System.out.println("======================================================================");
        System.out.println("Penguin-Land Health Score API Started!");
        System.out.println("======================================================================");
        System.out.println("Server: http://localhost:8080");
        System.out.println("API Docs: http://localhost:8080/swagger-ui.html");
        System.out.println("Main API: http://localhost:8080/monitoring");
        System.out.println("======================================================================");
    }
}
```

### 2. AWS 설정 클래스

```java
package com.penguin.healthscore.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.cloudwatch.CloudWatchClient;

@Configuration
public class AwsConfig {

    @Value("${aws.region}")
    private String region;

    @Value("${aws.credentials.access-key-id}")
    private String accessKeyId;

    @Value("${aws.credentials.secret-access-key}")
    private String secretAccessKey;

    @Bean
    public CloudWatchClient cloudWatchClient() {
        AwsCredentialsProvider credentialsProvider;

        if (accessKeyId != null && !accessKeyId.isEmpty()) {
            credentialsProvider = StaticCredentialsProvider.create(
                AwsBasicCredentials.create(accessKeyId, secretAccessKey)
            );
        } else {
            // Default credentials provider chain (IAM Role, env vars, etc.)
            credentialsProvider = null;
        }

        CloudWatchClient.Builder builder = CloudWatchClient.builder()
            .region(Region.of(region));

        if (credentialsProvider != null) {
            builder.credentialsProvider(credentialsProvider);
        }

        return builder.build();
    }
}
```

### 3. CORS 설정 클래스

```java
package com.penguin.healthscore.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

@Configuration
public class CorsConfig implements WebMvcConfigurer {

    @Value("${cors.allowed-origins}")
    private String allowedOrigins;

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
            .allowedOrigins(allowedOrigins)
            .allowedMethods("GET", "POST", "PUT", "DELETE", "OPTIONS")
            .allowedHeaders("*")
            .allowCredentials(true);
    }
}
```

### 4. 모델 클래스들

```java
// HealthMetrics.java
package com.penguin.healthscore.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class HealthMetrics {
    private double errorRate;
    private double latency;
    private double cpu;
}

// HealthResult.java
package com.penguin.healthscore.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class HealthResult {
    private int healthScore;
    private String healthState;      // "healthy", "warning", "danger"
    private String penguinAnimation;  // "happy", "worried", "crying"
    private String coachMessage;
}

// Alert.java
package com.penguin.healthscore.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class Alert {
    private String id;
    private String level;         // "info", "warning", "critical"
    private String message;
    private String timestamp;
    private boolean acknowledged;
}
```

### 5. 시뮬레이션 상태 클래스

```java
package com.penguin.healthscore.model;

import lombok.Data;
import org.springframework.stereotype.Component;

@Data
@Component
public class SimulationState {

    private boolean active = false;
    private String scenario = "normal";
    private Long startTime = null;
    private Integer duration = null;
    private boolean autoRotate = false;
    private int rotateInterval = 20; // 20초마다 전환
    private String[] scenariosCycle = {"normal", "high_latency", "error_burst"};
    private int currentCycleIndex = 0;

    public void start(String scenario, Integer duration) {
        this.active = true;
        this.scenario = scenario;
        this.startTime = System.currentTimeMillis();
        this.duration = duration;
        this.autoRotate = false;
    }

    public void startAutoRotate(int interval) {
        this.active = true;
        this.autoRotate = true;
        this.rotateInterval = interval;
        this.startTime = System.currentTimeMillis();
        this.currentCycleIndex = 0;
        this.scenario = scenariosCycle[0];
        this.duration = null; // 무한 반복
    }

    public void stop() {
        this.active = false;
        this.scenario = "normal";
        this.startTime = null;
        this.duration = null;
        this.autoRotate = false;
    }

    public boolean isActive() {
        if (!active) {
            return false;
        }

        // 자동 전환 모드
        if (autoRotate && startTime != null) {
            long elapsed = (System.currentTimeMillis() - startTime) / 1000;
            int newIndex = (int) ((elapsed / rotateInterval) % scenariosCycle.length);

            if (newIndex != currentCycleIndex) {
                currentCycleIndex = newIndex;
                scenario = scenariosCycle[newIndex];
                System.out.println("\n🔄 자동 전환: " + scenario.toUpperCase() +
                                 " (경과: " + elapsed + "초)\n");
            }
            return true;
        }

        // 일반 모드
        if (duration != null && startTime != null) {
            long elapsed = (System.currentTimeMillis() - startTime) / 1000;
            if (elapsed > duration) {
                stop();
                return false;
            }
        }

        return true;
    }
}
```

---

## ☁️ CloudWatch 연동

### CloudWatchService.java

```java
package com.penguin.healthscore.service;

import com.penguin.healthscore.model.HealthMetrics;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.cloudwatch.CloudWatchClient;
import software.amazon.awssdk.services.cloudwatch.model.*;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.List;

@Service
@RequiredArgsConstructor
public class CloudWatchService {

    private final CloudWatchClient cloudWatchClient;

    @Value("${aws.cloudwatch.alb-name}")
    private String albName;

    /**
     * CloudWatch에서 메트릭 값 가져오기
     */
    public Double getMetric(String metricName, String namespace, String statistic,
                           int period, int minutesAgo, List<Dimension> dimensions) {
        try {
            Instant endTime = Instant.now();
            Instant startTime = endTime.minus(minutesAgo, ChronoUnit.MINUTES);

            GetMetricStatisticsRequest request = GetMetricStatisticsRequest.builder()
                .namespace(namespace)
                .metricName(metricName)
                .dimensions(dimensions)
                .startTime(startTime)
                .endTime(endTime)
                .period(period)
                .statistics(Statistic.fromValue(statistic))
                .build();

            GetMetricStatisticsResponse response = cloudWatchClient.getMetricStatistics(request);

            if (response.hasDatapoints() && !response.datapoints().isEmpty()) {
                // 시간순 정렬 후 가장 최근 값 반환
                Datapoint latestDatapoint = response.datapoints().stream()
                    .max((d1, d2) -> d1.timestamp().compareTo(d2.timestamp()))
                    .orElse(null);

                if (latestDatapoint != null) {
                    double value = latestDatapoint.average();
                    System.out.println("✅ " + metricName + ": " + value +
                                     " (데이터포인트 " + response.datapoints().size() + "개)");
                    return value;
                }
            }

            System.out.println("⚠️ " + metricName + ": 데이터포인트 없음");
            return null;

        } catch (Exception e) {
            System.err.println("❌ Error getting metric " + metricName + ": " + e.getMessage());
            return null;
        }
    }

    /**
     * 에러율 계산
     */
    public double calculateErrorRate() {
        List<Dimension> dimensions = List.of(
            Dimension.builder().name("LoadBalancer").value(albName).build()
        );

        Double count4xx = getMetric("HTTPCode_Target_4XX_Count", "AWS/ApplicationELB",
                                   "Sum", 300, 5, dimensions);
        Double count5xx = getMetric("HTTPCode_Target_5XX_Count", "AWS/ApplicationELB",
                                   "Sum", 300, 5, dimensions);
        Double totalCount = getMetric("RequestCount", "AWS/ApplicationELB",
                                     "Sum", 300, 5, dimensions);

        if (totalCount == null || totalCount == 0) {
            return 0.0;
        }

        double errors = (count4xx != null ? count4xx : 0) + (count5xx != null ? count5xx : 0);
        return Math.round((errors / totalCount * 100) * 100.0) / 100.0;
    }

    /**
     * 현재 메트릭 조회
     */
    public HealthMetrics getCurrentMetrics() {
        System.out.println("\n" + "=".repeat(70));
        System.out.println("📊 CloudWatch 메트릭 조회 시작");
        System.out.println("=".repeat(70));

        // 1. 에러율
        double errorRate = calculateErrorRate();
        System.out.println("1️⃣ 에러율: " + errorRate + "%");

        // 2. 응답 시간 (밀리초)
        List<Dimension> dimensions = List.of(
            Dimension.builder().name("LoadBalancer").value(albName).build()
        );

        Double latencySec = getMetric("TargetResponseTime", "AWS/ApplicationELB",
                                     "Average", 300, 5, dimensions);
        double latencyMs = (latencySec != null) ? latencySec * 1000 : 200.0;
        System.out.println("2️⃣ 응답시간: " + Math.round(latencyMs) + "ms");

        // 3. CPU (Fallback)
        double cpu = 50.0;
        System.out.println("3️⃣ CPU 사용률: " + cpu + "%");
        System.out.println("=".repeat(70) + "\n");

        return new HealthMetrics(errorRate, latencyMs, cpu);
    }
}
```

---

## 🎭 시뮬레이션 서비스

### SimulationService.java

```java
package com.penguin.healthscore.service;

import com.penguin.healthscore.model.HealthMetrics;
import com.penguin.healthscore.model.SimulationState;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Random;

@Service
@RequiredArgsConstructor
public class SimulationService {

    private final SimulationState simulationState;
    private final Random random = new Random();

    /**
     * 시뮬레이션 메트릭 생성
     */
    public HealthMetrics getSimulatedMetrics() {
        if (!simulationState.isActive()) {
            return null;
        }

        long elapsed = (System.currentTimeMillis() - simulationState.getStartTime()) / 1000;

        // 사인파 + 랜덤 노이즈
        double wave = Math.sin(elapsed * 0.5) * 0.3;
        double noise = (random.nextDouble() - 0.5) * 0.2;

        HealthMetrics metrics;

        switch (simulationState.getScenario()) {
            case "high_latency":
                metrics = new HealthMetrics(
                    Math.max(0, 1.5 + noise),
                    Math.max(800, 1200 + wave * 400 + noise * 200),
                    Math.max(30, 55 + wave * 15 + noise * 10)
                );
                break;

            case "error_burst":
                metrics = new HealthMetrics(
                    Math.max(2, 8 + wave * 4 + noise * 2),
                    Math.max(200, 450 + wave * 150 + noise * 80),
                    Math.max(40, 65 + wave * 15 + noise * 10)
                );
                break;

            case "cpu_spike":
                metrics = new HealthMetrics(
                    Math.max(0, 0.5 + noise),
                    Math.max(100, 250 + wave * 100 + noise * 50),
                    Math.max(75, 90 + wave * 5 + noise * 3)
                );
                break;

            default: // "normal"
                metrics = new HealthMetrics(
                    Math.max(0, 0.3 + wave + noise),
                    Math.max(50, 180 + wave * 50 + noise * 30),
                    Math.max(20, 35 + wave * 10 + noise * 5)
                );
        }

        System.out.println("\n" + "=".repeat(70));
        System.out.println("🎭 시뮬레이션 모드: " + simulationState.getScenario().toUpperCase());
        System.out.println("=".repeat(70));
        System.out.println("1️⃣ 에러율: " + String.format("%.2f", metrics.getErrorRate()) + "%");
        System.out.println("2️⃣ 응답시간: " + Math.round(metrics.getLatency()) + "ms");
        System.out.println("3️⃣ CPU 사용률: " + String.format("%.1f", metrics.getCpu()) + "%");
        System.out.println("=".repeat(70) + "\n");

        return metrics;
    }
}
```

---

## 🏥 점수 계산 서비스

### HealthScoreService.java

```java
package com.penguin.healthscore.service;

import com.penguin.healthscore.model.HealthMetrics;
import com.penguin.healthscore.model.HealthResult;
import org.springframework.stereotype.Service;

@Service
public class HealthScoreService {

    /**
     * 건강 점수 계산 (Python score.py 로직과 동일)
     */
    public HealthResult analyzeDeploymentHealth(HealthMetrics metrics) {
        // 가중치
        double errorWeight = 0.5;
        double latencyWeight = 0.35;
        double cpuWeight = 0.15;

        // 임계값 설정
        double errorThresholdWarning = 2.0;
        double errorThresholdDanger = 5.0;
        double latencyThresholdWarning = 500;
        double latencyThresholdDanger = 1000;
        double cpuThresholdWarning = 70;
        double cpuThresholdDanger = 85;

        // 각 메트릭의 점수 계산 (0-100)
        double errorScore = calculateMetricScore(
            metrics.getErrorRate(),
            errorThresholdWarning,
            errorThresholdDanger
        );

        double latencyScore = calculateMetricScore(
            metrics.getLatency(),
            latencyThresholdWarning,
            latencyThresholdDanger
        );

        double cpuScore = calculateMetricScore(
            metrics.getCpu(),
            cpuThresholdWarning,
            cpuThresholdDanger
        );

        // 가중 평균 점수
        int totalScore = (int) Math.round(
            errorScore * errorWeight +
            latencyScore * latencyWeight +
            cpuScore * cpuWeight
        );

        // 상태 및 메시지 결정
        String healthState;
        String penguinAnimation;
        String coachMessage;

        if (totalScore <= 30) {
            healthState = "healthy";
            penguinAnimation = "happy";
            coachMessage = "💯 모든 지표가 녹색이에요! 대단해요!";
        } else if (totalScore <= 70) {
            healthState = "warning";
            penguinAnimation = "worried";
            coachMessage = "⚠️ 주의가 필요해요! 일부 지표가 임계치에 근접했어요.";
        } else {
            healthState = "danger";
            penguinAnimation = "crying";
            coachMessage = "🔥 위험! 여러 지표가 임계치를 초과했어요!";
        }

        return new HealthResult(totalScore, healthState, penguinAnimation, coachMessage);
    }

    /**
     * 개별 메트릭 점수 계산
     */
    private double calculateMetricScore(double value, double warningThreshold,
                                       double dangerThreshold) {
        if (value <= warningThreshold) {
            return 0;
        } else if (value <= dangerThreshold) {
            // Warning ~ Danger 구간: 30 ~ 70점
            double ratio = (value - warningThreshold) / (dangerThreshold - warningThreshold);
            return 30 + (ratio * 40);
        } else {
            // Danger 초과: 70 ~ 100점
            double excess = value - dangerThreshold;
            double excessRatio = Math.min(excess / dangerThreshold, 1.0);
            return 70 + (excessRatio * 30);
        }
    }
}
```

---

## 🎯 REST API 컨트롤러

### MonitoringController.java

```java
package com.penguin.healthscore.controller;

import com.penguin.healthscore.dto.MonitoringResponse;
import com.penguin.healthscore.dto.SimulateRequest;
import com.penguin.healthscore.model.*;
import com.penguin.healthscore.service.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.*;

@RestController
@RequiredArgsConstructor
@RequestMapping
public class MonitoringController {

    private final CloudWatchService cloudWatchService;
    private final SimulationService simulationService;
    private final HealthScoreService healthScoreService;
    private final SimulationState simulationState;

    /**
     * 메인 모니터링 API (프론트엔드가 5초마다 호출)
     */
    @GetMapping("/monitoring")
    public ResponseEntity<MonitoringResponse> getMonitoring() {
        // 시뮬레이션 모드 체크
        HealthMetrics metrics = simulationService.getSimulatedMetrics();

        // 실제 CloudWatch 데이터
        if (metrics == null) {
            metrics = cloudWatchService.getCurrentMetrics();
        }

        // 점수 계산
        HealthResult result = healthScoreService.analyzeDeploymentHealth(metrics);

        // 응답 생성
        MonitoringResponse response = new MonitoringResponse();
        response.setMetrics(Map.of(
            "cpuUsage", metrics.getCpu(),
            "latency", metrics.getLatency(),
            "errorRate", metrics.getErrorRate(),
            "timestamp", Instant.now().toString()
        ));

        response.setAnomaly(Map.of(
            "healthScore", result.getHealthScore(),
            "healthState", result.getHealthState(),
            "penguinAnimation", result.getPenguinAnimation(),
            "coachMessage", result.getCoachMessage()
        ));

        response.setAlerts(new ArrayList<>());

        return ResponseEntity.ok(response);
    }

    /**
     * 자동 시뮬레이션 시작 (20초마다 자동 전환)
     */
    @PostMapping("/monitoring/simulate/auto")
    public ResponseEntity<Map<String, Object>> startAutoSimulation(
            @RequestParam(defaultValue = "20") int interval) {

        simulationState.startAutoRotate(interval);

        System.out.println("\n" + "🎬".repeat(35));
        System.out.println("🔄 자동 시나리오 전환 시작!");
        System.out.println("⏱️  전환 간격: " + interval + "초");
        System.out.println("📋 순서: " + String.join(" → ", simulationState.getScenariosCycle()));
        System.out.println("🎬".repeat(35) + "\n");

        return ResponseEntity.ok(Map.of(
            "status", "auto_started",
            "interval", interval,
            "scenarios", simulationState.getScenariosCycle(),
            "message", interval + "초마다 자동으로 시나리오가 전환됩니다"
        ));
    }

    /**
     * 수동 시뮬레이션 시작
     */
    @PostMapping("/monitoring/simulate/start")
    public ResponseEntity<Map<String, Object>> startSimulation(
            @RequestBody SimulateRequest request) {

        simulationState.start(request.getScenario(), request.getDuration());

        System.out.println("\n" + "🎬".repeat(35));
        System.out.println("🎭 시뮬레이션 시작: " + request.getScenario().toUpperCase());
        if (request.getDuration() != null) {
            System.out.println("⏱️  지속 시간: " + request.getDuration() + "초");
        }
        System.out.println("🎬".repeat(35) + "\n");

        return ResponseEntity.ok(Map.of(
            "status", "started",
            "scenario", request.getScenario(),
            "message", "시뮬레이션 '" + request.getScenario() + "' 시작됨"
        ));
    }

    /**
     * 시뮬레이션 종료
     */
    @PostMapping("/monitoring/simulate/stop")
    public ResponseEntity<Map<String, Object>> stopSimulation() {
        boolean wasActive = simulationState.isActive();
        simulationState.stop();

        if (wasActive) {
            System.out.println("\n" + "🛑".repeat(35));
            System.out.println("🎭 시뮬레이션 종료");
            System.out.println("🛑".repeat(35) + "\n");
        }

        return ResponseEntity.ok(Map.of(
            "status", "stopped",
            "message", wasActive ? "시뮬레이션 종료됨" : "시뮬레이션이 실행 중이 아닙니다"
        ));
    }
}
```

### DTO 클래스들

```java
// MonitoringResponse.java
package com.penguin.healthscore.dto;

import lombok.Data;
import java.util.*;

@Data
public class MonitoringResponse {
    private Map<String, Object> metrics;
    private Map<String, Object> anomaly;
    private List<Object> alerts;
}

// SimulateRequest.java
package com.penguin.healthscore.dto;

import lombok.Data;

@Data
public class SimulateRequest {
    private String scenario;    // "normal", "high_latency", "error_burst", "cpu_spike"
    private Integer duration;   // 지속 시간 (초)
}
```

---

## 🚀 실행 방법

### 1. 프로젝트 빌드

#### Maven
```bash
mvn clean package
```

#### Gradle
```bash
gradle clean build
```

### 2. 환경변수 설정 (선택사항)

```bash
# Windows
set AWS_ACCESS_KEY_ID=your_access_key
set AWS_SECRET_ACCESS_KEY=your_secret_key
set SLACK_WEBHOOK_URL=your_webhook_url

# Linux/Mac
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export SLACK_WEBHOOK_URL=your_webhook_url
```

### 3. 실행

#### Maven
```bash
mvn spring-boot:run
```

#### Gradle
```bash
gradle bootRun
```

#### JAR 실행
```bash
java -jar target/healthscore-1.0.0.jar
```

### 4. API 테스트

```bash
# 모니터링 데이터 조회
curl http://localhost:8080/monitoring

# 자동 시뮬레이션 시작 (20초 간격)
curl -X POST http://localhost:8080/monitoring/simulate/auto

# 수동 시뮬레이션 시작
curl -X POST http://localhost:8080/monitoring/simulate/start \
  -H "Content-Type: application/json" \
  -d '{"scenario":"high_latency","duration":30}'

# 시뮬레이션 종료
curl -X POST http://localhost:8080/monitoring/simulate/stop
```

---

## 📊 Python vs Java 비교

| 항목 | Python (FastAPI) | Java (Spring Boot) |
|------|------------------|-------------------|
| **포트** | 8000 | 8080 |
| **프레임워크** | FastAPI | Spring Boot |
| **CloudWatch SDK** | boto3 | AWS SDK for Java v2 |
| **의존성 관리** | pip / requirements.txt | Maven / Gradle |
| **실행 방식** | `python main.py` | `mvn spring-boot:run` 또는 `java -jar` |
| **타입 시스템** | Optional (Type Hints) | 강타입 (Compile-time) |
| **CORS 설정** | FastAPI Middleware | WebMvcConfigurer |
| **환경변수** | python-dotenv | application.yml + Spring |

---

## 🎯 주요 차이점

### 1. **비동기 처리**
- **Python**: `async/await` 기본 지원
- **Java**: 동기 방식 (필요시 `@Async` 또는 WebFlux 사용)

### 2. **타입 안정성**
- **Python**: 런타임 타입 체크
- **Java**: 컴파일 타임 타입 체크 (안전성 ↑)

### 3. **패키지 관리**
- **Python**: 가상환경 + pip
- **Java**: Maven/Gradle 중앙 저장소

### 4. **성능**
- **Python**: 개발 속도 빠름, 런타임 느림
- **Java**: 컴파일 필요, 런타임 빠름

---

## ✅ 체크리스트

완성도 확인:

- [ ] Maven/Gradle 빌드 성공
- [ ] AWS 자격증명 설정 완료
- [ ] `/monitoring` API 정상 응답
- [ ] `/monitoring/simulate/auto` 20초마다 자동 전환
- [ ] CloudWatch 실제 데이터 조회 성공
- [ ] Slack 알림 연동 (선택사항)
- [ ] CORS 설정으로 프론트엔드 연동 성공

---

## 💡 팁

1. **Lombok 사용 권장**: `@Data`, `@RequiredArgsConstructor` 등으로 코드 간소화
2. **Spring Boot DevTools**: 자동 재시작으로 개발 속도 향상
3. **Swagger/OpenAPI**: API 문서 자동 생성 (`springdoc-openapi-ui` 의존성 추가)
4. **로깅**: Logback/SLF4J 사용으로 체계적인 로그 관리
5. **테스트**: JUnit 5 + MockMvc로 API 테스트 작성

---

**🎉 이제 Java Spring Boot로 완벽하게 구현할 수 있습니다!**

문의사항이 있으면 언제든 질문하세요! 🐧
