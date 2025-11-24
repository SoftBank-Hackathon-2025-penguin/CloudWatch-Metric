# 🐧 CloudWatch Anomaly Detection 구현 워크플로우

**담당자**: 이승규
**프로젝트**: Penguin-Land
**목표**: 해커톤 1등! 🏆

---

## 📅 전체 일정 (11월 20일 ~ 11월 22일)

```
11/20 (D-2) ─── 설계 & 기초 구현
11/21 (D-1) ─── 통합 & 테스트
11/22 (D-Day) ─ 마무리 & 시연
```

---

## 🎯 Day 1: 11월 20일 (오늘) - 설계 & 기초 구현

### ⏰ 오전 (09:00 - 12:00)

#### [09:00 - 09:30] 환경 세팅 ✅
```bash
# 1. 가상환경 활성화
cd "C:\Users\electrozone\Desktop\소뱅 해커톤\CloudWatch-Metric"
.\venv\Scripts\activate

# 2. 패키지 설치
pip install boto3 pytest python-dotenv

# 3. 폴더 구조 생성
mkdir score_engine
mkdir tests
mkdir docs
mkdir api_specs
```

#### [09:30 - 10:30] 설계 문서 작성 ✅
- [x] `DESIGN_DOC_승규님_CloudWatch_Anomaly_Detection.md` 작성
- [x] 메트릭 정의
- [x] 점수 계산 알고리즘 설계
- [x] 게이미피케이션 아이디어 정리
- [x] 팀원들과 공유

#### [10:30 - 12:00] Python 점수 엔진 구현 Part 1
**파일**: `score_engine/score.py`

```python
# 구현할 함수 목록:
# 1. calculate_severity()      - 개별 메트릭 심각도 계산
# 2. calculate_health_score()  - 전체 건강 점수 계산
# 3. classify_state()          - 상태 분류 (healthy/warning/danger)
# 4. identify_problem_metrics() - 문제 메트릭 식별
```

**체크리스트**:
- [ ] Fallback 임계값 상수 정의
- [ ] `calculate_severity()` 함수 구현
- [ ] `calculate_health_score()` 함수 구현
- [ ] 기본 테스트 실행

---

### 🍱 점심 (12:00 - 13:00)

---

### ⏰ 오후 (13:00 - 18:00)

#### [13:00 - 14:30] Python 점수 엔진 구현 Part 2
**파일**: `score_engine/score.py`

```python
# 구현할 함수 목록:
# 5. generate_coach_message()     - 코칭 메시지 생성
# 6. generate_warning_message()   - 주의 메시지
# 7. generate_danger_message()    - 위험 메시지
```

**체크리스트**:
- [ ] 메시지 템플릿 작성 (HEALTHY_MESSAGES, WARNING_MESSAGES 등)
- [ ] `identify_problem_metrics()` 함수 구현
- [ ] `generate_coach_message()` 함수 구현
- [ ] 메트릭별 맞춤 메시지 로직

#### [14:30 - 15:30] 테스트 코드 작성
**파일**: `score_engine/test_score.py`

```python
# 테스트 케이스:
# 1. test_calculate_severity_with_band()    - 밴드 있을 때
# 2. test_calculate_severity_fallback()     - Fallback 임계값
# 3. test_calculate_health_score_healthy()  - 정상 상태
# 4. test_calculate_health_score_warning()  - 주의 상태
# 5. test_calculate_health_score_danger()   - 위험 상태
# 6. test_classify_state()                  - 상태 분류
# 7. test_generate_coach_message()          - 메시지 생성
```

**실행**:
```bash
cd score_engine
pytest test_score.py -v
```

#### [15:30 - 16:00] 휴식 ☕

#### [16:00 - 17:00] API 스펙 문서 작성
**파일**: `api_specs/API_SPEC.md`

**내용**:
1. SNS 메시지 형식
2. Backend Webhook 엔드포인트
3. Backend → Frontend API
4. JSON 요청/응답 예시
5. DynamoDB 테이블 스키마

**체크리스트**:
- [ ] SNS 메시지 파싱 예제 작성
- [ ] API 엔드포인트 정의
- [ ] 요청/응답 JSON 스키마
- [ ] 에러 케이스 정의

#### [17:00 - 18:00] 팀원 질문 목록 & 협의
**파일**: `docs/QUESTIONS_FOR_TEAM.md`

**전준배님께 확인할 것**:
1. 모니터링 대상 애플리케이션 타입
2. ALB vs EC2 메트릭 선택
3. SNS Webhook URL 경로
4. Lambda 사용 여부
5. CloudWatch Logs 사용 여부

**강종연님께 전달할 것**:
1. 프론트엔드 API 폴링 로직
2. 펭귄 애니메이션 에셋 요청
3. 사운드 에셋 요청
4. 디자인 가이드라인

**장윤호님께 확인할 것**:
1. Terraform으로 CloudWatch Alarm 자동 생성 가능한지
2. SNS Topic ARN
3. DynamoDB 테이블 생성

---

### 🌙 저녁 이후 (선택적)

#### [18:00 - 20:00] Python 코드 최적화 & 문서화
- [ ] Docstring 추가
- [ ] Type Hints 추가
- [ ] README.md 작성 (Java 팀 참고용)
- [ ] 엣지 케이스 처리

#### [20:00 - 21:00] 팀 회의
- 오늘 진행 상황 공유
- 내일 작업 계획 조율
- 막힌 부분 논의

---

## 🎯 Day 2: 11월 21일 - 통합 & 테스트

### ⏰ 오전 (09:00 - 12:00)

#### [09:00 - 10:30] CloudWatch 설정 (전준배님과 협업)
**작업**:
1. CloudWatch Anomaly Detection 생성
2. Alarm 설정 (3개: error_rate, latency, cpu)
3. SNS Topic 생성 및 구독 설정

**CloudWatch Alarm 설정 체크리스트**:
- [ ] `penguin-land-error-rate-anomaly` 생성
- [ ] `penguin-land-latency-anomaly` 생성
- [ ] `penguin-land-cpu-anomaly` 생성
- [ ] SNS Topic ARN 확인
- [ ] SNS → Backend Webhook 연결

#### [10:30 - 12:00] SNS 메시지 파싱 테스트
**작업**:
1. SNS 테스트 메시지 전송
2. Backend Webhook에서 수신 확인
3. 메시지 파싱 로직 검증

**테스트 시나리오**:
```bash
# AWS CLI로 테스트 메시지 전송
aws sns publish \
  --topic-arn arn:aws:sns:ap-northeast-2:123456789:penguin-land-alarms \
  --message file://test_alarm_message.json
```

---

### 🍱 점심 (12:00 - 13:00)

---

### ⏰ 오후 (13:00 - 18:00)

#### [13:00 - 15:00] Backend API 구현 지원 (Java 팀 지원)
**작업**:
1. Python 로직을 Java로 이식하는 작업 지원
2. 알고리즘 설명
3. 엣지 케이스 공유

**Java 팀에게 전달할 것**:
- [ ] `score.py` 로직 설명
- [ ] 테스트 케이스 공유
- [ ] Fallback 임계값 상수
- [ ] 예상되는 버그 케이스

#### [15:00 - 16:00] DynamoDB 스키마 검증
**작업**:
1. DynamoDB 테이블 생성 확인
2. 샘플 데이터 Insert 테스트
3. Query/Scan 테스트

**테이블**:
- `penguin-land-deployments`
- `penguin-land-alarms`

#### [16:00 - 17:00] 통합 테스트 Part 1
**시나리오 1: 정상 배포**
```
1. 애플리케이션 배포
2. CloudWatch 메트릭 정상 수집 확인
3. Anomaly Detection 작동 확인
4. Frontend에서 "건강" 상태 표시 확인
```

#### [17:00 - 18:00] 통합 테스트 Part 2
**시나리오 2: 이상 감지**
```
1. 부하 테스트 도구로 에러 발생
2. CloudWatch Alarm 발생 확인
3. SNS → Backend 전달 확인
4. 점수 계산 및 상태 변경 확인
5. Frontend에서 "위험" 상태 표시 확인
```

---

### 🌙 저녁 이후

#### [18:00 - 20:00] 시뮬레이션 모드 구현
**작업**:
1. Backend API `/api/cloudwatch/simulate` 구현
2. Frontend "시뮬레이션" 버튼 연결
3. 데모 시나리오 테스트

**데모 시나리오**:
```javascript
// 버튼 클릭 → 3초 후 위험 상태 → 30초 후 정상 복귀
const demoScenario = async () => {
  await sleep(3000);
  simulateDanger();
  await sleep(30000);
  simulateRecovery();
}
```

#### [20:00 - 21:00] 팀 회의
- 통합 테스트 결과 공유
- 버그 리스트 작성
- 내일 마무리 작업 계획

---

## 🎯 Day 3: 11월 22일 (D-Day) - 마무리 & 시연

### ⏰ 오전 (09:00 - 12:00)

#### [09:00 - 10:00] 버그 수정
- [ ] 전날 발견된 버그 수정
- [ ] 엣지 케이스 처리
- [ ] 에러 핸들링 강화

#### [10:00 - 11:30] 게이미피케이션 완성도 높이기
**프론트엔드 작업 (강종연님과 협업)**:
- [ ] 펭귄 애니메이션 최종 점검
- [ ] 사운드 효과 추가
- [ ] 컨페티 효과 테스트
- [ ] 배경색 전환 애니메이션

**백엔드 작업**:
- [ ] 코칭 메시지 다양화
- [ ] 응답 속도 최적화
- [ ] 로깅 추가

#### [11:30 - 12:00] 데모 시나리오 리허설 1차
```
시나리오 1: 완벽한 배포 (30초)
1. 배포 시작
2. 로딩 화면
3. 배포 완료 + 빵빠레
4. 점수 0점 + 컨페티
5. 펭귄 춤

시나리오 2: 위험 감지 & 복구 (60초)
1. 정상 상태 (15점)
2. 시뮬레이션 버튼 클릭
3. 경고음 + 펭귄 표정 변화
4. 점수 85점 (위험)
5. 화면 흔들림
6. 긴급 액션 버튼
7. 시뮬레이션 종료
8. 정상 복구 (20점)
```

---

### 🍱 점심 (12:00 - 13:00)

---

### ⏰ 오후 (13:00 - 18:00)

#### [13:00 - 14:00] 안정화 & 성능 최적화
- [ ] API 응답 속도 확인 (< 500ms 목표)
- [ ] Frontend 폴링 간격 최적화
- [ ] 메모리 누수 체크
- [ ] 에러 로깅 확인

#### [14:00 - 15:00] 발표 자료 준비
**발표 구조**:
1. 문제 제기 (30초)
   - "배포는 불안한 경험입니다"
2. 솔루션 소개 (1분)
   - "펭귄이 코치해주는 배포 경험"
3. 라이브 데모 (2분)
   - 시나리오 1 + 시나리오 2
4. 기술 스택 & 아키텍처 (1분)
5. 차별화 포인트 (30초)
   - "게이미피케이션 + ML 기반 이상 감지"

#### [15:00 - 16:00] 데모 시나리오 리허설 2차
- [ ] 타이밍 체크
- [ ] 음향 체크
- [ ] 화면 전환 체크
- [ ] 백업 플랜 확인

#### [16:00 - 17:00] 최종 점검
- [ ] 모든 기능 작동 확인
- [ ] 시연 환경 세팅
- [ ] 네트워크 안정성 확인
- [ ] 백업 데이터 준비

#### [17:00 - 18:00] 발표 연습
- 전체 팀원과 발표 리허설
- 질의응답 예상 질문 준비

---

### 🌙 해커톤 시연

#### [18:00 - 20:00] 본선 발표
- 라이브 데모
- 심사위원 질의응답
- 네트워킹

#### [20:00 - 21:00] 시상식
- 🏆 **1등 목표!**

---

## 📋 체크리스트 요약

### Phase 1: 설계 & 기초 구현 (11/20)
- [x] 설계 문서 작성
- [ ] Python 점수 엔진 구현
- [ ] 테스트 코드 작성
- [ ] API 스펙 문서 작성
- [ ] 팀원 질문 목록 정리

### Phase 2: 통합 & 테스트 (11/21)
- [ ] CloudWatch 설정
- [ ] SNS 연동
- [ ] Backend API 구현
- [ ] DynamoDB 테이블 생성
- [ ] 통합 테스트
- [ ] 시뮬레이션 모드 구현

### Phase 3: 마무리 & 시연 (11/22)
- [ ] 버그 수정
- [ ] 게이미피케이션 완성
- [ ] 데모 시나리오 리허설
- [ ] 발표 자료 준비
- [ ] 최종 점검

---

## 🚨 위험 요소 & 대응 방안

### 위험 1: CloudWatch Anomaly Detection 데이터 부족
**문제**: 초기 데이터가 없으면 Anomaly Detection이 작동하지 않음

**대응**:
- ✅ Fallback 임계값 시스템 구현 (완료)
- 시연 시 Fallback 모드로 작동
- "실제 운영에서는 2주 후 ML 모델 학습 완료" 설명

### 위험 2: SNS → Backend 연동 실패
**문제**: 네트워크 이슈로 알람이 전달되지 않을 수 있음

**대응**:
- 시뮬레이션 모드 사용
- Frontend에서 Mock 데이터 주입
- 백업: WebSocket 대신 Polling으로 대체

### 위험 3: 시연 중 네트워크 끊김
**문제**: AWS 연결이 끊기면 데모 불가

**대응**:
- 녹화 영상 준비
- 로컬 Mock 서버 준비
- 시연 직전 인터넷 연결 확인

### 위험 4: 시간 부족
**문제**: 게이미피케이션 완성도가 낮을 수 있음

**대응**:
- 우선순위: 핵심 기능 > 재미 요소
- MVP: 펭귄 표정 변화 + 점수 표시만 구현
- Nice-to-have: 애니메이션, 사운드, 컨페티

---

## 💡 성공 포인트

### 기술적 완성도
- ✅ Anomaly Detection (ML 기반)
- ✅ Fallback 시스템 (안정성)
- ✅ 실시간 점수 계산
- ✅ 확장 가능한 아키텍처

### 사용자 경험
- ✅ 펭귄 캐릭터 (감정적 연결)
- ✅ 게이미피케이션 (재미)
- ✅ 직관적인 메시지 (초보자 친화)
- ✅ 실시간 피드백 (즉각성)

### 발표 전략
- ✅ 문제 공감 (배포는 불안함)
- ✅ 라이브 데모 (WOW 효과)
- ✅ 차별화 포인트 (ML + 게임)
- ✅ 실제 사용 가능 (프로덕션 레벨)

---

## 📞 긴급 연락망

### 팀원
- 강종연님: Frontend + Terraform
- 전준배님: CloudWatch + 인프라
- 장윤호님: Terraform
- 이승규: CloudWatch Anomaly Detection + 점수 시스템

### 역할 분담 (긴급 시)
- **승규 → 준배님**: CloudWatch 설정 이슈
- **승규 → 종연님**: API 연동 이슈
- **승규 → 윤호님**: Terraform 설정 이슈

---

## 🎉 최종 목표

> "누군가가 '이거 꼭 써보고 싶다!'라고 생각할 만큼 매력적인 배포 경험"

### 심사위원 반응 목표
- 😲 "오!" (기술 데모 시)
- 😊 "귀엽다!" (펭귄 등장 시)
- 👏 "실제로 쓰고 싶다!" (발표 마무리)

### 해커톤 1등 조건
1. ✅ 기술적 완성도: Anomaly Detection + 점수 시스템
2. ✅ 사용자 경험: 게이미피케이션 + 펭귄
3. ✅ 실용성: 실제 사용 가능한 수준
4. ✅ 발표력: 라이브 데모 + 명확한 메시지

---

**화이팅! 해커톤 1등 가자! 🐧🏆**

**승규님, 당신은 할 수 있어요! 💪**
