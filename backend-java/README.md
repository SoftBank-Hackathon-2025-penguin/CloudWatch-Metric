# Penguin-Land Health Score API - Java Backend

Python FastAPI 백엔드의 Java Spring Boot 버전입니다.

## 🚀 실행 방법

### 1. 환경 설정

환경변수 설정 (선택사항):
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

### 2. 빌드 및 실행

```bash
# Maven 빌드
mvn clean package

# 실행
mvn spring-boot:run

# 또는 JAR 실행
java -jar target/healthscore-1.0.0.jar
```

## 📡 API 엔드포인트

### 메인 모니터링 API
```bash
GET http://localhost:8080/monitoring
```

### 자동 시뮬레이션 (20초마다)
```bash
POST http://localhost:8080/monitoring/simulate/auto
```

### 수동 시뮬레이션
```bash
POST http://localhost:8080/monitoring/simulate/start
Content-Type: application/json

{
  "scenario": "high_latency",
  "duration": 30
}
```

### 시뮬레이션 종료
```bash
POST http://localhost:8080/monitoring/simulate/stop
```

## 🎯 Python vs Java 차이점

| 항목 | Python | Java |
|------|--------|------|
| 포트 | 8000 | 8080 |
| 실행 | `python main.py` | `mvn spring-boot:run` |
| 패키지 관리 | pip | Maven |

## 📂 프로젝트 구조

```
backend-java/
├── src/main/java/com/penguin/healthscore/
│   ├── PenguinLandApplication.java      # Main 클래스
│   ├── config/                          # 설정
│   ├── controller/                      # REST API
│   ├── service/                         # 비즈니스 로직
│   ├── model/                           # 데이터 모델
│   └── dto/                             # DTO
├── src/main/resources/
│   └── application.yml                  # 설정 파일
├── pom.xml                              # Maven 설정
└── README.md
```

## ✅ 필요한 Java 파일 목록

아래 파일들을 `JAVA_IMPLEMENTATION_GUIDE.md`를 참고하여 생성하세요:

### Config
- [ ] AwsConfig.java
- [ ] CorsConfig.java

### Model
- [ ] HealthMetrics.java
- [ ] HealthResult.java
- [ ] Alert.java
- [ ] SimulationState.java

### Service
- [ ] CloudWatchService.java
- [ ] HealthScoreService.java
- [ ] SimulationService.java
- [ ] SlackService.java (optional)

### Controller
- [ ] MonitoringController.java

### DTO
- [ ] MonitoringResponse.java
- [ ] SimulateRequest.java

## 🎓 학습 가이드

1. **JAVA_IMPLEMENTATION_GUIDE.md** - 전체 구현 가이드
2. **JAVA_SLACK_GUIDE.md** - Slack 연동 가이드

각 가이드에서 코드를 복사하여 해당 위치에 생성하세요!
