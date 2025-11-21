# 🐧 CloudWatch Anomaly Detection + 점수 시스템

**해커톤 제출 문서 (승규 파트)**
**담당**: 이승규
**역할**: CloudWatch 메트릭 분석 + Anomaly Detection + 점수 시스템
**기간**: 2025-11-15 ~ 2025-11-20

---

## 📌 나의 역할
<img width="637" height="443" alt="image" src="https://github.com/user-attachments/assets/83db85b2-87ff-4d68-b8bb-ad88d847a366" />


### 맡은 업무
```
CloudWatch 메트릭(에러율·레이턴시)에 Anomaly Detection 적용
+ 점수 시스템 설계 및 구현
+ 게이미피케이션 아이디어 제안
```

### 왜 이 역할을 맡았나?
- CloudWatch + ML에 관심 있음
- "즐거운 배포 경험"이라는 주제가 매력적
- 기술 + UX를 결합하고 싶었음

---

## 🎯 문제 인식

### 내가 본 문제점

**개인 경험**:
```
배포할 때마다 불안했던 기억:
  - "에러율 3%는 높은 건가?"
  - "레이턴시 500ms는 정상인가?"
  - "뭘 봐야 하는지 모르겠어..."
```

**초보 개발자 입장**:
- Grafana 같은 도구는 너무 복잡
- 수치만 봐서는 "좋은지 나쁜지" 판단 어려움
- 배포 후 그냥 불안함

**내가 정의한 문제**:
> "배포는 기술적으로는 성공해도, 심리적으로는 불안한 경험"

---

## 💡 나의 솔루션

### 핵심 아이디어

**1. 수치를 점수로**
```
복잡한 메트릭 → 0~100점
이유: 게임 점수처럼 직관적
```

**2. 펭귄 코치**
```
차가운 알람 → 귀여운 조언
이유: 감정적 연결, 덜 불안함
```

**3. 게이미피케이션**
```
그냥 모니터링 → 재미있는 경험
이유: "즐거운 배포" 주제 구현
```

### 왜 이 방식인가?

**다른 방법들을 생각해봤음**:

| 방법 | 장점 | 단점 | 결정 |
|------|------|------|------|
| 알람만 | 간단 | 재미없음 | ❌ |
| 복잡한 대시보드 | 전문적 | 초보자 어려움 | ❌ |
| 점수+게임 | 직관적, 즐거움 | 구현 복잡 | ✅ |

**최종 선택 이유**:
- 초보자도 즉시 이해 가능
- "즐거운" 경험 제공
- 실제로 유용함

---

## 🔧 기술 설계 과정

### 1단계: 점수 계산 방법 고민

#### 처음 생각 (단순 임계값)
```python
if error_rate > 5%:
    score = 100  # 위험
elif error_rate > 1%:
    score = 50   # 주의
else:
    score = 0    # 정상
```

**문제점**:
- 너무 단순함
- "평소와 다른가?"를 모름
- Anomaly Detection 활용 못함

#### 두 번째 생각 (Anomaly Detection만)
```python
if value > band_upper or value < band_lower:
    score = 100  # 이상
else:
    score = 0    # 정상
```

**문제점**:
- 초기 데이터 없으면 작동 안 함
- 해커톤 시연에서 위험
- "얼마나 벗어났는지" 모름

#### 최종 선택 (Hybrid)
```python
def calculate_severity(value, band_upper, band_lower, metric_type):
    # 1. Anomaly Detection 밴드 있으면 우선 사용
    if band_upper and band_lower:
        if inside_band:
            return 0.0
        else:
            deviation = calculate_deviation()
            return min(1.0, deviation * 2)

    # 2. 없으면 Fallback 임계값 사용
    else:
        threshold = FALLBACK_THRESHOLDS[metric_type]
        return calculate_from_threshold(value, threshold)
```

**선택 이유**:
- 항상 작동 (Fallback)
- ML 활용 (Anomaly Detection)
- 벗어난 "정도" 계산 가능
- 해커톤 시연 안전

---

### 2단계: 메트릭 가중치 결정

#### 고민한 내용

**동등 가중치?**
```
에러율 33% + 레이턴시 33% + CPU 33%

문제: 에러율이 사용자에게 제일 심각한데 무시됨
```

**에러율만?**
```
에러율 100%

문제: 레이턴시, CPU 무시
```

**차등 가중치!**
```
에러율 50% + 레이턴시 35% + CPU 15%

이유:
- 에러율: 사용자 직접 영향 (가장 중요)
- 레이턴시: 사용자 경험 (중요)
- CPU: 간접 지표 (덜 중요)
```

**검증 방법**:
```python
# 테스트 케이스 작성
test_cases = [
    # 에러율만 높음
    {"error": 10%, "latency": 200ms, "cpu": 40%} → 높은 점수 예상

    # CPU만 높음
    {"error": 0.5%, "latency": 200ms, "cpu": 95%} → 낮은 점수 예상
]

# 결과: 에러율 > 레이턴시 > CPU 영향도 확인 ✅
```

---

### 3단계: 상태 분류

#### 검토한 옵션

**2단계**:
```
정상/위험

단점: 중간 상태 표현 불가
예: "조금 주의" 같은 느낌 못 줌
```

**5단계**:
```
매우좋음/좋음/보통/나쁨/매우나쁨

단점:
- 너무 복잡
- 펭귄 표정 5개 필요 (시간 부족)
```

**3단계** ✅:
```
0~30점: 건강 (초록, 웃는 펭귄)
31~70점: 주의 (노랑, 보통 펭귄)
71~100점: 위험 (빨강, 우는 펭귄)

이유:
- 신호등 비유 (누구나 이해)
- 3개 표정만 필요 (제작 가능)
- 적절한 세분화
```

---

### 4단계: Fallback 임계값 설정

#### 참고한 자료

**AWS Best Practices**:
```
- 에러율 1% 이하 권장
- 실제 운영 경험 고려
```

**Google Performance 연구**:
```
- 300ms 이상 시 사용자 이탈률 증가
- 사용자 체감 시작점
```

#### 최종 설정

| 메트릭 | 정상 | 주의 | 위험 |
|--------|------|------|------|
| 에러율 | <1% | 1~5% | >5% |
| 레이턴시 | <300ms | 300~700ms | >700ms |
| CPU | <50% | 50~80% | >80% |

**왜 이 값들?**
```
에러율 1%: AWS 권장 기준
레이턴시 300ms: 사용자 체감 시작
CPU 50%: 버퍼 확보 (급격한 증가 대비)
```

**검증**:
```python
# 실제 값으로 테스트
test_values = [
    {"error": 0.5%, "latency": 250ms, "cpu": 40%},   # 정상 예상
    {"error": 3%, "latency": 500ms, "cpu": 70%},     # 주의 예상
    {"error": 8%, "latency": 1200ms, "cpu": 90%}     # 위험 예상
]

# 결과: 예상과 일치 ✅
```

---

## 💻 구현

### 내가 작성한 코드

**1. 점수 계산 엔진** (`score.py`, 550줄)
```python
def analyze_deployment_health(metrics):
    """
    메인 API 함수
    이것만 호출하면 모든 분석 완료
    """
    score = calculate_health_score(metrics)
    state = classify_state(score)
    message = generate_coach_message(state, metrics)

    return {
        'health_score': score,
        'health_state': state,
        'coach_message': message,
        'penguin_animation': get_animation(state)
    }
```

**2. 테스트 코드** (`test_score.py`, 450줄)
```python
# 50개 이상의 테스트 작성
def test_calculate_severity_with_band():
    """밴드 안에 있을 때 정상"""
    assert calculate_severity(450, 600, 200, 'latency') == 0.0

def test_fallback_warning():
    """Fallback 주의 범위"""
    severity = calculate_severity(500, metric_type='latency')
    assert 0.0 < severity < 0.8
```


### 내가 중요하게 생각한 것

**1. 테스트**
```
왜?
- 알고리즘이 복잡해서 버그 가능성
- 팀원들에게 신뢰 주기 위함
- Java로 이식할 때 검증 기준

결과:
- 50개 테스트 작성
- 100% 통과
- 엣지 케이스까지 커버
```

**2. 문서화**
```
왜?
- 팀원들이 내 코드 이해해야 함
- Java 팀이 이식할 때 참고
- 나중에 내가 봐도 이해 가능

결과:
- 함수마다 Docstring
- 예시 코드 포함
- 왜 이렇게 했는지 설명
```

**3. 실용성**
```
왜?
- 해커톤 끝나도 쓸 수 있어야 함
- "작동하는 것"이 최우선

결과:
- 실제 CloudWatch 연동 가능
- 에러 핸들링 포함
- Edge case 대응
```

---

## 🎨 재미 요소 아이디어 (내가 제안한 것)

### 브레인스토밍 과정

**처음 떠올린 아이디어들**:
```
1. 펭귄 춤
2. 컨페티
3. 화면 흔들림
4. 점수 카운터 애니메이션
5. 배포 스트릭
6. 긴급 액션 버튼
7. 재미있는 로딩 메시지
8. 펭귄 스킨
9. BGM
10. 음성 안내
```

**필터링 기준**:
```
1. 구현 시간 (2일 이내?)
2. WOW 효과 (심사위원 반응)
3. 실용성 (실제로 유용한가?)
```

**최종 우선순위**:
```
Priority 1 (반드시):
  1. 펭귄 춤 + 컨페티 (1.5시간)
  2. 화면 흔들림 (30분)
  3. 점수 카운터 (30분)

Priority 2 (있으면 좋음):
  4. 배포 스트릭 (1시간)
  5. 긴급 버튼 (1시간)

Priority 3 (시간 남으면):
  6. 펭귄 스킨 (2시간)
```

**탈락한 아이디어**:
```
BGM: 너무 시끄러울 수 있음
음성: 다국어 문제
→ 실용성 떨어짐
```

---
