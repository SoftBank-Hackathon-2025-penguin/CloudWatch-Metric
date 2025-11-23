# 🚀 Java Backend 빠른 시작 가이드

Python 백엔드와 동일한 기능을 제공하는 Java Spring Boot 버전입니다.

---

## 📦 필수 요구사항

- **Java 17+** (OpenJDK 또는 Oracle JDK)
- **Maven 3.6+** (또는 IDE에 내장된 Maven)

---

## ⚡ 빠른 실행 (3단계)

### 1️⃣ 환경 변수 설정

**Windows PowerShell:**
```powershell
$env:AWS_ACCESS_KEY_ID="your-access-key"
$env:AWS_SECRET_ACCESS_KEY="your-secret-key"
$env:SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

**또는 `.env` 파일 생성:**
```bash
# backend-java/.env
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### 2️⃣ 서버 실행

```bash
cd backend-java
mvn spring-boot:run
```

서버가 `http://localhost:8080`에서 실행됩니다!

### 3️⃣ 테스트

브라우저에서:
```
http://localhost:8080/health
```

---

## 🎮 시뮬레이션 사용법

### 자동 시나리오 전환 (20초마다)

```bash
curl -X POST http://localhost:8080/monitoring/simulate/auto
```

### 수동 시나리오 실행

```bash
# Healthy 상태
curl -X POST http://localhost:8080/monitoring/simulate/start ^
  -H "Content-Type: application/json" ^
  -d "{\"scenario\":\"normal\",\"duration\":30}"

# Warning 상태
curl -X POST http://localhost:8080/monitoring/simulate/start ^
  -H "Content-Type: application/json" ^
  -d "{\"scenario\":\"high_latency\",\"duration\":30}"

# Danger 상태
curl -X POST http://localhost:8080/monitoring/simulate/start ^
  -H "Content-Type: application/json" ^
  -d "{\"scenario\":\"error_burst\",\"duration\":30}"
```

### 시뮬레이션 중지

```bash
curl -X POST http://localhost:8080/monitoring/simulate/stop
```

---

## 📡 주요 API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| `GET` | `/monitoring` | 현재 건강 점수 및 메트릭 조회 |
| `POST` | `/monitoring/simulate/auto` | 자동 시나리오 전환 시작 (20초 간격) |
| `POST` | `/monitoring/simulate/start` | 수동 시나리오 시작 |
| `POST` | `/monitoring/simulate/stop` | 시뮬레이션 중지 |
| `GET` | `/health` | 서버 헬스 체크 |

---

## 🗂️ 프로젝트 구조

```
backend-java/
├── src/main/java/com/penguin/healthscore/
│   ├── PenguinLandApplication.java      # 메인 클래스
│   ├── controller/
│   │   └── MonitoringController.java    # REST API 컨트롤러
│   ├── service/
│   │   ├── HealthScoreService.java      # 점수 계산 로직
│   │   ├── SimulationService.java       # 시뮬레이션 메트릭 생성
│   │   ├── CloudWatchService.java       # AWS CloudWatch 연동
│   │   └── SlackService.java            # Slack 알림
│   ├── model/
│   │   ├── HealthMetrics.java           # 메트릭 모델
│   │   ├── HealthResult.java            # 점수 결과 모델
│   │   └── SimulationState.java         # 시뮬레이션 상태 관리
│   ├── dto/
│   │   ├── MonitoringResponse.java      # API 응답 DTO
│   │   └── SimulateRequest.java         # 시뮬레이션 요청 DTO
│   └── config/
│       ├── AwsConfig.java               # AWS 설정
│       └── CorsConfig.java              # CORS 설정
└── src/main/resources/
    └── application.yml                   # 애플리케이션 설정
```

---

## 🔧 IDE에서 실행하기

### IntelliJ IDEA

1. **프로젝트 열기**: `backend-java` 폴더를 Open
2. **Maven 동기화**: 우측의 "Maven" 탭 → "Reload All Maven Projects"
3. **실행**: `PenguinLandApplication.java` → 우클릭 → "Run"

### Eclipse

1. **Import**: File → Import → Existing Maven Projects
2. **Update**: 프로젝트 우클릭 → Maven → Update Project
3. **Run**: Run As → Spring Boot App

### VS Code

1. **Extension 설치**: "Extension Pack for Java", "Spring Boot Extension Pack"
2. **실행**: F5 또는 Run → Start Debugging

---

## 🐛 문제 해결

### 1. Port 8080 already in use

```bash
# Windows에서 포트 사용 중인 프로세스 종료
netstat -ano | findstr :8080
taskkill /PID <PID번호> /F
```

### 2. AWS 자격 증명 오류

환경 변수가 제대로 설정되었는지 확인:
```powershell
echo $env:AWS_ACCESS_KEY_ID
echo $env:AWS_SECRET_ACCESS_KEY
```

### 3. Maven 빌드 실패

```bash
mvn clean install -U
```

### 4. Lombok이 작동하지 않음

IntelliJ: File → Settings → Plugins → "Lombok" 설치 후 재시작

---

## 🎯 Python vs Java 포트 비교

| 항목 | Python | Java |
|------|--------|------|
| **포트** | 8000 | 8080 |
| **프레임워크** | FastAPI | Spring Boot |
| **실행 명령** | `python main.py` | `mvn spring-boot:run` |
| **API 엔드포인트** | 동일 | 동일 |
| **기능** | 100% 호환 | 100% 호환 |

---

## 📊 시연 시나리오 예시

```bash
# 1. 자동 전환 시작 (20초마다 상태 변경)
curl -X POST http://localhost:8080/monitoring/simulate/auto

# 2. 프론트엔드 열기
start http://localhost:8080/monitoring

# 3. 3분 동안 자동으로 상태가 변경되는 것을 시연!
# normal → high_latency → error_burst → normal → ...
```

---

## ✅ 개발 완료 체크리스트

- [x] 건강 점수 계산 엔진
- [x] CloudWatch 메트릭 연동
- [x] 시뮬레이션 시스템
- [x] 자동 시나리오 전환 (20초)
- [x] Slack 알림 (70점 이상)
- [x] CORS 설정 (프론트엔드 연동)
- [x] REST API 엔드포인트
- [x] 헬스 체크

---

**🎉 이제 Java 백엔드를 사용할 준비가 완료되었습니다!**

**다음 단계:** 프론트엔드의 API URL을 `http://localhost:8080`으로 변경하면 바로 연동됩니다.
