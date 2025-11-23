"""
Penguin-Land CloudWatch Health Score API
FastAPI Backend Server

실시간으로 CloudWatch 메트릭을 가져와서 점수 계산
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime, timedelta
import boto3
import sys
import os
from typing import Dict, Optional, List
from dotenv import load_dotenv
import requests
import random
import math
import time

# .env 파일 로드
load_dotenv()

# score.py 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'score_engine'))
from score import analyze_deployment_health

app = FastAPI(title="Penguin-Land Health Score API")

# ============================================================================
# 시뮬레이션 상태 관리
# ============================================================================

class SimulationState:
    """시뮬레이션 상태를 관리하는 글로벌 싱글톤"""
    def __init__(self):
        self.active = False
        self.scenario = 'normal'
        self.start_time = None
        self.duration = None
        self.auto_rotate = False
        self.rotate_interval = 20  # 20초마다 전환
        self.scenarios_cycle = ['normal', 'high_latency', 'error_burst']
        self.current_cycle_index = 0

    def start(self, scenario: str, duration: Optional[int] = None):
        self.active = True
        self.scenario = scenario
        self.start_time = time.time()
        self.duration = duration
        self.auto_rotate = False

    def start_auto_rotate(self, interval: int = 20):
        """자동 시나리오 전환 시작 (20초마다 normal → warning → danger 순환)"""
        self.active = True
        self.auto_rotate = True
        self.rotate_interval = interval
        self.start_time = time.time()
        self.current_cycle_index = 0
        self.scenario = self.scenarios_cycle[0]
        self.duration = None  # 무한 반복

    def stop(self):
        self.active = False
        self.scenario = 'normal'
        self.start_time = None
        self.duration = None
        self.auto_rotate = False

    def is_active(self) -> bool:
        """시뮬레이션이 활성화되어 있고, 아직 duration이 남았는지 확인"""
        if not self.active:
            return False

        # 자동 전환 모드일 때
        if self.auto_rotate and self.start_time is not None:
            elapsed = time.time() - self.start_time
            # rotate_interval마다 다음 시나리오로 전환
            new_index = int(elapsed // self.rotate_interval) % len(self.scenarios_cycle)
            if new_index != self.current_cycle_index:
                self.current_cycle_index = new_index
                self.scenario = self.scenarios_cycle[new_index]
                print(f"\n🔄 자동 전환: {self.scenario.upper()} (경과: {elapsed:.0f}초)\n")
            return True

        # 일반 모드일 때
        if self.duration is not None and self.start_time is not None:
            elapsed = time.time() - self.start_time
            if elapsed > self.duration:
                self.stop()
                return False

        return True

    def get_simulated_metrics(self) -> Dict:
        """현재 시나리오에 맞는 시뮬레이션 메트릭 생성"""
        if not self.is_active():
            return None

        # 경과 시간 (초)
        elapsed = time.time() - self.start_time if self.start_time else 0

        # 시간에 따라 자연스럽게 변화하는 값 생성 (사인파 + 랜덤)
        wave = math.sin(elapsed * 0.5) * 0.3  # -0.3 ~ 0.3
        noise = random.uniform(-0.1, 0.1)

        scenarios = {
            'normal': {
                'error_rate': max(0, 0.3 + wave + noise),
                'latency': max(50, 180 + wave * 50 + noise * 30),
                'cpu': max(20, 35 + wave * 10 + noise * 5)
            },
            'cpu_spike': {
                'error_rate': max(0, 0.5 + noise),
                'latency': max(100, 250 + wave * 100 + noise * 50),
                'cpu': max(75, 90 + wave * 5 + noise * 3)  # 높은 CPU
            },
            'high_latency': {
                'error_rate': max(0, 1.5 + noise),
                'latency': max(800, 1200 + wave * 400 + noise * 200),  # 높은 latency
                'cpu': max(30, 55 + wave * 15 + noise * 10)
            },
            'error_burst': {
                'error_rate': max(2, 8 + wave * 4 + noise * 2),  # 높은 에러율
                'latency': max(200, 450 + wave * 150 + noise * 80),
                'cpu': max(40, 65 + wave * 15 + noise * 10)
            }
        }

        base_values = scenarios.get(self.scenario, scenarios['normal'])

        return {
            'error_rate': {'value': round(base_values['error_rate'], 2)},
            'latency': {'value': round(base_values['latency'], 1)},
            'cpu': {'value': round(base_values['cpu'], 1)}
        }

# 글로벌 시뮬레이션 상태
simulation = SimulationState()

# ============================================================================
# Pydantic 모델 정의
# ============================================================================

class SimulateRequest(BaseModel):
    scenario: str  # 'cpu_spike' | 'high_latency' | 'error_burst' | 'normal'
    duration: Optional[int] = None  # seconds

class Alert(BaseModel):
    id: str
    level: str  # 'info' | 'warning' | 'critical'
    message: str
    timestamp: str
    acknowledged: bool

# CORS 설정 (React가 호출할 수 있게)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발용: 모든 origin 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CloudWatch 클라이언트
cloudwatch = boto3.client(
    'cloudwatch',
    region_name=os.getenv('AWS_DEFAULT_REGION', 'ap-northeast-2'),
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# ALB 이름 (여기에 실제 ALB 이름 입력)
ALB_NAME = "app/penguin-land-alb/77a716d3813b8deb"

# Slack Webhook URL
SLACK_WEBHOOK_URL = os.getenv('SLACK_WEBHOOK_URL')

def send_slack_alert(health_score: int, health_state: str, coach_message: str, metrics: Dict):
    """Slack으로 경보 전송 (70점 이상일 때만)"""

    # 🔕 Slack 알림 비활성화 (시연용으로만 켜기)
    return  # ← 이 줄 때문에 알림 안 감!

    if health_score < 70:
        return
    
    if not SLACK_WEBHOOK_URL:
        print("⚠️ Slack Webhook URL이 설정되지 않았습니다!")
        return
    
    emoji_map = {
        'healthy': '✅',
        'warning': '⚠️',
        'danger': '🚨'
    }
    emoji = emoji_map.get(health_state, '⚠️')
    
    message = {
        "blocks": [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"{emoji} Penguin-Land 배포 경보!"
                }
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*점수:*\n{health_score}/100점"},
                    {"type": "mrkdwn", "text": f"*상태:*\n{health_state.upper()}"}
                ]
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*메시지:*\n{coach_message}"}
            },
            {"type": "divider"},
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*에러율:*\n{metrics.get('error_rate', 0):.2f}%"},
                    {"type": "mrkdwn", "text": f"*응답시간:*\n{metrics.get('latency', 0):.0f}ms"},
                    {"type": "mrkdwn", "text": f"*CPU:*\n{metrics.get('cpu', 0):.0f}%"}
                ]
            },
            {
                "type": "context",
                "elements": [
                    {"type": "mrkdwn", "text": f"🕐 {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(SLACK_WEBHOOK_URL, json=message)
        if response.status_code == 200:
            print(f"✅ Slack 알림 전송! (점수: {health_score}점)")
        else:
            print(f"❌ Slack 알림 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ Slack 오류: {e}")


def get_cloudwatch_metric(
    metric_name: str,
    namespace: str = "AWS/ApplicationELB",
    statistic: str = "Average",
    period: int = 60,
    minutes_ago: int = 5,
    dimensions: Optional[list] = None
) -> Optional[float]:
    """
    CloudWatch에서 메트릭 값을 가져오는 함수

    Args:
        metric_name: 메트릭 이름 (예: 'TargetResponseTime')
        namespace: 네임스페이스 (기본: AWS/ApplicationELB)
        statistic: 통계 타입 (Average, Sum, Maximum 등)
        period: 기간 (초 단위, 기본 60초)
        minutes_ago: 몇 분 전부터 데이터 가져올지 (기본 5분)
        dimensions: 커스텀 Dimensions (없으면 ALB 기본값 사용)

    Returns:
        float: 메트릭 값 (없으면 None)
    """
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=minutes_ago)

        # Dimensions 설정
        if dimensions is None:
            dimensions = [
                {
                    'Name': 'LoadBalancer',
                    'Value': ALB_NAME
                }
            ]

        response = cloudwatch.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=dimensions,
            StartTime=start_time,
            EndTime=end_time,
            Period=period,
            Statistics=[statistic]
        )

        # 데이터포인트가 있으면 가장 최근 값 반환
        if response['Datapoints']:
            # 시간순 정렬
            datapoints = sorted(response['Datapoints'], key=lambda x: x['Timestamp'], reverse=True)
            print(f"✅ {metric_name}: {datapoints[0][statistic]} (데이터포인트 {len(response['Datapoints'])}개)")
            return datapoints[0][statistic]

        print(f"⚠️ {metric_name}: 데이터포인트 없음 (Namespace: {namespace})")
        return None

    except Exception as e:
        print(f"❌ Error getting metric {metric_name}: {e}")
        return None


def calculate_error_rate() -> float:
    """
    에러율 계산 (4XX + 5XX) / Total Requests * 100

    Returns:
        float: 에러율 (%)
    """
    # 5분 동안의 합계로 계산
    total_requests = get_cloudwatch_metric('RequestCount', statistic='Sum', period=300) or 0
    errors_4xx = get_cloudwatch_metric('HTTPCode_Target_4XX_Count', statistic='Sum', period=300) or 0
    errors_5xx = get_cloudwatch_metric('HTTPCode_Target_5XX_Count', statistic='Sum', period=300) or 0

    if total_requests == 0:
        return 0.0

    error_rate = ((errors_4xx + errors_5xx) / total_requests) * 100
    return round(error_rate, 2)


def get_cpu_utilization() -> float:
    """
    CPU 사용률을 CloudWatch에서 가져오기
    여러 방법을 시도하여 가장 먼저 성공한 값 반환

    Returns:
        float: CPU 사용률 (%) - 실패 시 50.0 반환
    """
    # 방법 1: 환경변수에서 EC2 Instance ID 읽기
    instance_id = os.getenv('EC2_INSTANCE_ID')
    if instance_id:
        print(f"🔍 EC2 Instance ID로 CPU 조회: {instance_id}")
        cpu = get_cloudwatch_metric(
            metric_name='CPUUtilization',
            namespace='AWS/EC2',
            statistic='Average',
            period=300,
            dimensions=[{'Name': 'InstanceId', 'Value': instance_id}]
        )
        if cpu is not None:
            return cpu

    # 방법 2: Auto Scaling Group 이름으로 시도
    asg_name = os.getenv('AUTO_SCALING_GROUP_NAME')
    if asg_name:
        print(f"🔍 Auto Scaling Group으로 CPU 조회: {asg_name}")
        cpu = get_cloudwatch_metric(
            metric_name='CPUUtilization',
            namespace='AWS/EC2',
            statistic='Average',
            period=300,
            dimensions=[{'Name': 'AutoScalingGroupName', 'Value': asg_name}]
        )
        if cpu is not None:
            return cpu

    # 방법 3: ECS/Fargate 서비스인 경우 (선택사항)
    ecs_cluster = os.getenv('ECS_CLUSTER_NAME')
    ecs_service = os.getenv('ECS_SERVICE_NAME')
    if ecs_cluster and ecs_service:
        print(f"🔍 ECS 서비스로 CPU 조회: {ecs_cluster}/{ecs_service}")
        cpu = get_cloudwatch_metric(
            metric_name='CPUUtilization',
            namespace='AWS/ECS',
            statistic='Average',
            period=300,
            dimensions=[
                {'Name': 'ClusterName', 'Value': ecs_cluster},
                {'Name': 'ServiceName', 'Value': ecs_service}
            ]
        )
        if cpu is not None:
            return cpu

    # 모두 실패하면 Fallback 값 반환
    print("⚠️ CPU 메트릭을 가져올 수 없음. Fallback 값(50.0) 사용")
    print("💡 환경변수 설정 방법:")
    print("   - EC2_INSTANCE_ID=i-xxxxxxxxx")
    print("   - AUTO_SCALING_GROUP_NAME=your-asg-name")
    print("   - ECS_CLUSTER_NAME + ECS_SERVICE_NAME")
    return 50.0


def get_current_metrics() -> Dict:
    """
    현재 CloudWatch 메트릭을 모두 가져와서 반환
    시뮬레이션이 활성화되어 있으면 시뮬레이션 데이터 반환

    Returns:
        Dict: score.py에서 사용할 수 있는 형식의 메트릭 데이터
    """
    # 🎭 시뮬레이션 모드 체크
    simulated = simulation.get_simulated_metrics()
    if simulated:
        print("\n" + "="*70)
        print(f"🎭 시뮬레이션 모드: {simulation.scenario.upper()}")
        print("="*70)
        print(f"1️⃣ 에러율: {simulated['error_rate']['value']}%")
        print(f"2️⃣ 응답시간: {simulated['latency']['value']:.0f}ms")
        print(f"3️⃣ CPU 사용률: {simulated['cpu']['value']:.1f}%")
        print("="*70 + "\n")
        return simulated

    # 🔄 실제 CloudWatch 데이터
    print("\n" + "="*70)
    print("📊 CloudWatch 메트릭 조회 시작")
    print("="*70)

    # 1. 에러율 계산
    error_rate = calculate_error_rate()
    print(f"1️⃣ 에러율: {error_rate}%")

    # 2. 응답 시간 (밀리초)
    latency_sec = get_cloudwatch_metric(
        metric_name='TargetResponseTime',
        namespace='AWS/ApplicationELB',
        statistic='Average',
        period=300
    )

    if latency_sec is not None:
        latency_ms = latency_sec * 1000  # 초 → 밀리초 변환
    else:
        # 데이터가 없으면 기본값 사용 (정상 범위)
        latency_ms = 200.0
        print("⚠️ Latency 데이터 없음. 기본값 200ms 사용")

    print(f"2️⃣ 응답시간: {latency_ms:.0f}ms")

    # 3. CPU 사용률
    cpu = get_cpu_utilization()
    print(f"3️⃣ CPU 사용률: {cpu:.1f}%")

    print("="*70 + "\n")

    # Anomaly Detection 밴드 가져오기 (있다면)
    # 지금은 밴드 없이 Fallback 임계값만 사용

    metrics = {
        'error_rate': {
            'value': error_rate
        },
        'latency': {
            'value': latency_ms
        },
        'cpu': {
            'value': cpu
        }
    }

    return metrics


@app.get("/")
async def root():
    """
    API 루트 - 헬스 체크용
    """
    return {
        "message": "Penguin-Land Health Score API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health/test")
async def health_test():
    """
    테스트용 엔드포인트 - Mock 데이터 반환
    """
    mock_metrics = {
        'error_rate': {'value': 2.0},
        'latency': {'value': 850.0},
        'cpu': {'value': 60.0}
    }

    result = analyze_deployment_health(mock_metrics)

    return {
        "health_score": result['health_score'],
        "health_state": result['health_state'],
        "coach_message": result['coach_message'],
        "penguin_animation": result['penguin_animation'],
        "metrics": mock_metrics,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/deployment/{session_id}/health")
async def get_deployment_health(session_id: str, demo: Optional[str] = None):
    """
    배포 상태 점수 조회 (실시간 CloudWatch 데이터)

    Frontend가 5초마다 호출하는 메인 API

    Args:
        session_id: 세션 ID
        demo: 데모 모드 ('healthy', 'warning', 'danger') - 시연용
    """
    try:
        # 🎭 데모 모드: 시연용 Mock 데이터
        if demo in ['healthy', 'warning', 'danger']:
            print(f"\n🎭 데모 모드: {demo.upper()}")

            demo_metrics = {
                'healthy': {
                    'error_rate': {'value': 0.3},
                    'latency': {'value': 180.0},
                    'cpu': {'value': 35.0}
                },
                'warning': {
                    'error_rate': {'value': 3.5},
                    'latency': {'value': 620.0},
                    'cpu': {'value': 76.0}
                },
                'danger': {
                    'error_rate': {'value': 12.0},
                    'latency': {'value': 2400.0},
                    'cpu': {'value': 95.0}
                }
            }

            metrics = demo_metrics[demo]
        else:
            # 🔄 실제 CloudWatch 데이터 사용 모드
            # 실시간으로 ALB 메트릭을 가져와서 점수 계산
            metrics = get_current_metrics()

        # 점수 계산
        result = analyze_deployment_health(metrics)
        
        # 🚨 Slack 경보 전송!
        send_slack_alert(
            health_score=result['health_score'],
            health_state=result['health_state'],
            coach_message=result['coach_message'],
            metrics={
                "error_rate": metrics['error_rate']['value'],
                "latency": metrics['latency']['value'],
                "cpu": metrics['cpu']['value']
            }
        )
        
        # 응답 반환
        return {
            "session_id": session_id,
            "health_score": result['health_score'],
            "health_state": result['health_state'],
            "coach_message": result['coach_message'],
            "penguin_animation": result['penguin_animation'],
            "metrics": {
                "error_rate": metrics['error_rate']['value'],
                "latency": metrics['latency']['value'],
                "cpu": metrics['cpu']['value']
            },
            "timestamp": datetime.utcnow().isoformat(),
            "problem_metrics": result.get('problem_metrics', [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/metrics/raw")
async def get_raw_metrics():
    """
    디버깅용: CloudWatch 원본 메트릭 데이터 조회
    """
    try:
        metrics = get_current_metrics()
        return {
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/api/webhook/cloudwatch-alarm")
async def cloudwatch_alarm_webhook(request: Request):
    """
    CloudWatch SNS 알람을 받는 Webhook

    SNS가 이 엔드포인트로 POST 요청 보냄
    """
    try:
        # SNS 메시지 파싱
        body = await request.json()

        # SNS 구독 확인 메시지 처리
        if body.get('Type') == 'SubscriptionConfirmation':
            # 구독 확인 URL 자동 방문
            subscribe_url = body.get('SubscribeURL')
            if subscribe_url:
                response = requests.get(subscribe_url)
                print(f"✅ SNS 구독 확인 완료! (Status: {response.status_code})")
                return {"message": "Subscription confirmed", "status": "success"}

        # 실제 알람 메시지 처리
        if body.get('Type') == 'Notification':
            message = body.get('Message', '')
            subject = body.get('Subject', 'CloudWatch Alarm')

            print("=" * 70)
            print(f"🚨 CloudWatch 알람 수신!")
            print(f"제목: {subject}")
            print(f"메시지: {message}")
            print("=" * 70)

            # 🔕 Slack 알림 비활성화 (시연용으로만 켜기)
            # Slack으로 전송
            # if SLACK_WEBHOOK_URL:
            #     slack_message = {...}
            #     slack_response = requests.post(SLACK_WEBHOOK_URL, json=slack_message)
            print("📝 로그만 출력 (Slack 전송 안함)")

            return {
                "message": "Alarm processed",
                "status": "success",
                "subject": subject
            }

        return {"message": "Unknown message type", "type": body.get('Type')}

    except Exception as e:
        print(f"❌ Webhook 오류: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============================================================================
# 모니터링 & 시뮬레이션 API
# ============================================================================

def generate_alerts(health_score: int, health_state: str, problem_metrics: List) -> List[Alert]:
    """건강 상태에 따라 Alert 생성"""
    alerts = []

    if health_state == 'danger':
        for metric_name, severity in problem_metrics:
            if severity >= 0.7:
                alerts.append(Alert(
                    id=f"alert-{metric_name}-{int(time.time())}",
                    level='critical',
                    message=f"{metric_name.replace('_', ' ').title()} 위험 수준 (심각도: {severity:.0%})",
                    timestamp=datetime.utcnow().isoformat(),
                    acknowledged=False
                ))
    elif health_state == 'warning':
        for metric_name, severity in problem_metrics:
            if severity >= 0.3:
                alerts.append(Alert(
                    id=f"alert-{metric_name}-{int(time.time())}",
                    level='warning',
                    message=f"{metric_name.replace('_', ' ').title()} 주의 필요 (심각도: {severity:.0%})",
                    timestamp=datetime.utcnow().isoformat(),
                    acknowledged=False
                ))

    return alerts


@app.get("/monitoring")
async def get_monitoring_data():
    """
    모니터링 데이터 조회 (w/ CloudWatch)

    Returns:
        - metrics: 현재 메트릭 데이터 (cpuUsage, latency, errorRate)
        - anomaly: 이상 감지 점수 및 상태
        - alerts: 경보 목록
    """
    try:
        # 현재 메트릭 가져오기
        metrics = get_current_metrics()

        # 점수 계산
        result = analyze_deployment_health(metrics)

        # Alert 생성
        alerts = generate_alerts(
            health_score=result['health_score'],
            health_state=result['health_state'],
            problem_metrics=result.get('problem_metrics', [])
        )

        return {
            "metrics": {
                "cpuUsage": metrics['cpu']['value'],
                "latency": metrics['latency']['value'],
                "errorRate": metrics['error_rate']['value'],
                "timestamp": datetime.utcnow().isoformat()
            },
            "anomaly": {
                "healthScore": result['health_score'],
                "healthState": result['health_state'],
                "penguinAnimation": result['penguin_animation'],
                "coachMessage": result['coach_message']
            },
            "alerts": [alert.dict() for alert in alerts]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/monitoring/simulate/start")
async def start_simulation(request: SimulateRequest):
    """
    임의 장애 시뮬레이션 시작

    Args:
        scenario: 'cpu_spike' | 'high_latency' | 'error_burst' | 'normal'
        duration: 지속 시간 (초, 선택사항)

    Returns:
        시뮬레이션 시작 확인 메시지
    """
    try:
        valid_scenarios = ['cpu_spike', 'high_latency', 'error_burst', 'normal']

        if request.scenario not in valid_scenarios:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid scenario. Must be one of: {', '.join(valid_scenarios)}"
            )

        simulation.start(request.scenario, request.duration)

        print("\n" + "🎬" * 35)
        print(f"🎭 시뮬레이션 시작: {request.scenario.upper()}")
        if request.duration:
            print(f"⏱️  지속 시간: {request.duration}초")
        print("🎬" * 35 + "\n")

        return {
            "status": "started",
            "scenario": request.scenario,
            "duration": request.duration,
            "message": f"시뮬레이션 '{request.scenario}' 시작됨"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/monitoring/simulate/stop")
async def stop_simulation():
    """
    시뮬레이션 종료

    Returns:
        시뮬레이션 종료 확인 메시지
    """
    try:
        was_active = simulation.is_active()
        simulation.stop()

        if was_active:
            print("\n" + "🛑" * 35)
            print("🎭 시뮬레이션 종료")
            print("🛑" * 35 + "\n")

        return {
            "status": "stopped",
            "message": "시뮬레이션 종료됨" if was_active else "시뮬레이션이 실행 중이 아닙니다"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.post("/monitoring/simulate/auto")
async def start_auto_simulation(interval: int = 20):
    """
    자동 시나리오 전환 시작 (시연용 완벽!)

    20초마다 자동으로 시나리오 전환:
    - 0-20초: normal (Healthy 상태)
    - 20-40초: high_latency (Warning 상태)
    - 40-60초: error_burst (Danger 상태)
    - 60초~: normal로 돌아가서 반복

    Args:
        interval: 전환 간격 (초, 기본 20초)

    Returns:
        자동 시뮬레이션 시작 확인
    """
    try:
        simulation.start_auto_rotate(interval)

        print("\n" + "🎬" * 35)
        print("🔄 자동 시나리오 전환 시작!")
        print(f"⏱️  전환 간격: {interval}초")
        print(f"📋 순서: {' → '.join(simulation.scenarios_cycle)} → 반복")
        print("🎬" * 35 + "\n")

        return {
            "status": "auto_started",
            "interval": interval,
            "scenarios": simulation.scenarios_cycle,
            "message": f"{interval}초마다 자동으로 시나리오가 전환됩니다"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    import sys
    import io

    # Windows 인코딩 문제 해결
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    print("=" * 70)
    print("Penguin-Land Health Score API Started!")
    print("=" * 70)
    print(f"Server: http://localhost:8000")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"Test API: http://localhost:8000/api/health/test")
    print(f"Main API: http://localhost:8000/api/deployment/test-123/health")
    print("=" * 70)

    uvicorn.run(app, host="0.0.0.0", port=8000)
