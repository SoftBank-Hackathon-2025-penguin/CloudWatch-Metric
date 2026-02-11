# Penguin-Land Backend API

FastAPI 기반 실시간 CloudWatch 헬스 스코어 API

## 🚀 빠른 시작

### 1. AWS Credentials 설정

**.env 파일 만들기:**
```bash
cp .env.example .env
```

**.env 파일 수정:**
```
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_DEFAULT_REGION=ap-northeast-2
```

**Access Key 만들기:**
1. AWS Console → IAM → 사용자
2. "보안 자격 증명" 탭
3. "액세스 키 만들기" 클릭
4. Access Key ID와 Secret Access Key 복사
5. .env 파일에 붙여넣기

### 2. 서버 실행

```bash
cd backend
python main.py
```


### 3. API 테스트

**브라우저에서:**
- API 문서: http://localhost:8000/docs
- 테스트 API: http://localhost:8000/api/health/test
- 실제 API: http://localhost:8000/api/deployment/test-123/health

**curl로:**
```bash
curl http://localhost:8000/api/health/test
```

## 📡 API 엔드포인트

### GET /api/deployment/{session_id}/health

**설명:** 실시간 CloudWatch 메트릭으로 점수 계산

**응답 예시:**
```json
{
  "session_id": "test-123",
  "health_score": 28,
  "health_state": "healthy",
  "coach_message": "🎉 완벽해요! 모든 지표가 정상이에요!",
  "penguin_animation": "happy",
  "metrics": {
    "error_rate": 2.0,
    "latency": 850.0,
    "cpu": 60.0
  },
  "timestamp": "2025-11-22T03:00:00.000000"
}
```

### GET /api/health/test

**설명:** Mock 데이터로 테스트 (AWS Credentials 없이 작동)

### GET /api/metrics/raw

**설명:** CloudWatch 원본 메트릭 조회 (디버깅용)

## 🔧 문제 해결

### boto3 에러 발생 시

```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

→ .env 파일 확인!

### CORS 에러 발생 시

main.py에서 CORS 설정 확인:
```python
allow_origins=["*"]  # 모든 origin 허용
```

## 📝 참고

- CloudWatch 메트릭은 1분마다 업데이트
- Frontend는 5초마다 이 API를 호출
- Anomaly Detection 밴드는 2주 후 사용 가능
- 현재는 Fallback 임계값으로 작동 중
