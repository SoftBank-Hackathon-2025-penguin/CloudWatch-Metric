# CloudWatch-Metric


# CloudWatch 메트릭 + Anomaly Detection 설계 (담당: 이승규)

## 1. 목표

- 배포 직후 서비스 상태(에러율, 레이턴시)가
  평소와 얼마나 다른지 자동으로 감지하고,
  이를 0~100점 점수 + 정상/주의/위험 상태 + 배포 코치 메시지로 변환한다.
- 프론트에서는 해당 정보를 펭귄 아이콘, 컨페티, 경고 애니메이션 등
  “재미있는 배포 경험”으로 시각화한다.

## 2. 모니터링 대상 메트릭 (개념 초안)

### 2.1 에러율(error_rate)

- 개념 정의:
  - `에러율(%) = 5xx 응답 수 / 전체 요청 수 * 100`
- 실제 CloudWatch 메트릭:
  - (전준배님 답변 후 채우기)
  - 예: ALB 기준
    - m1 = HTTPCode_ELB_5XX_Count
    - m2 = RequestCount

### 2.2 레이턴시(latency)

- 개념 정의:
  - 평균 혹은 p95 응답 시간(ms)
- 실제 CloudWatch 메트릭:
  - (전준배님 답변 후 채우기)
  - 예: TargetResponseTime, Latency(p95) 등



