package com.penguinland.monitoring;

import java.util.*;
import java.util.stream.Collectors;

/**
 * Penguin-Land CloudWatch Health Score Engine
 *
 * 배포 상태를 0~100점으로 점수화하고, 펭귄 코치 메시지를 생성하는 엔진
 *
 * 담당: 이승규
 * Java 변환: 2025-11-22
 */
public class HealthScoreEngine {

    // ============================================================================
    // 상수 정의
    // ============================================================================

    // 메트릭별 가중치 (합계 100%)
    private static final Map<String, Double> METRIC_WEIGHTS = Map.of(
        "error_rate", 0.50,  // 에러율이 가장 중요 (50%)
        "latency", 0.35,     // 레이턴시 (35%)
        "cpu", 0.15          // CPU (15%)
    );

    // 상태별 점수 범위
    private static final Map<String, int[]> STATE_SCORE_RANGES = Map.of(
        "healthy", new int[]{0, 30},
        "warning", new int[]{31, 70},
        "danger", new int[]{71, 100}
    );

    // 건강 상태 메시지 템플릿
    private static final List<String> HEALTHY_MESSAGES = Arrays.asList(
        "🎉 완벽해요! 모든 지표가 정상이에요!",
        "👍 아주 안정적이에요! 지금 상태로도 충분해요!",
        "✨ 훌륭한 배포에요! 펭귄이 춤추고 있어요!",
        "🌟 최고의 상태에요! 이대로 유지해주세요!",
        "🏆 완벽한 점수! 축하드려요!",
        "💯 모든 지표가 녹색이에요! 대단해요!",
        "🎊 배포 성공! 펭귄들이 축하하고 있어요!"
    );

    // ============================================================================
    // 내부 클래스: ThresholdConfig
    // ============================================================================

    public static class ThresholdConfig {
        private final double normal;   // 정상 상한값
        private final double warning;  // 주의 상한값
        private final double danger;   // 위험 시작값

        public ThresholdConfig(double normal, double warning, double danger) {
            this.normal = normal;
            this.warning = warning;
            this.danger = danger;
        }

        public double getNormal() { return normal; }
        public double getWarning() { return warning; }
        public double getDanger() { return danger; }
    }

    // Fallback 임계값 (Anomaly Detection 밴드가 없을 때 사용)
    private static final Map<String, ThresholdConfig> FALLBACK_THRESHOLDS = Map.of(
        "error_rate", new ThresholdConfig(1.0, 5.0, 10.0),   // 1%, 5%, 10%
        "latency", new ThresholdConfig(300, 700, 1500),      // 300ms, 700ms, 1500ms
        "cpu", new ThresholdConfig(50, 80, 95)                // 50%, 80%, 95%
    );

    // ============================================================================
    // DTO 클래스
    // ============================================================================

    /**
     * 메트릭 데이터
     */
    public static class MetricData {
        private double value;
        private Double bandUpper;  // Anomaly Detection 상한 밴드 (nullable)
        private Double bandLower;  // Anomaly Detection 하한 밴드 (nullable)

        public MetricData() {}

        public MetricData(double value) {
            this.value = value;
        }

        public MetricData(double value, Double bandUpper, Double bandLower) {
            this.value = value;
            this.bandUpper = bandUpper;
            this.bandLower = bandLower;
        }

        // Getters & Setters
        public double getValue() { return value; }
        public void setValue(double value) { this.value = value; }

        public Double getBandUpper() { return bandUpper; }
        public void setBandUpper(Double bandUpper) { this.bandUpper = bandUpper; }

        public Double getBandLower() { return bandLower; }
        public void setBandLower(Double bandLower) { this.bandLower = bandLower; }
    }

    /**
     * 문제 메트릭 정보
     */
    public static class ProblemMetric {
        private String metricName;
        private double severity;

        public ProblemMetric(String metricName, double severity) {
            this.metricName = metricName;
            this.severity = severity;
        }

        public String getMetricName() { return metricName; }
        public double getSeverity() { return severity; }
    }

    /**
     * 건강 분석 결과
     */
    public static class HealthAnalysisResult {
        private int healthScore;
        private String healthState;
        private String coachMessage;
        private String penguinAnimation;
        private List<ProblemMetric> problemMetrics;

        public HealthAnalysisResult() {}

        // Getters & Setters
        public int getHealthScore() { return healthScore; }
        public void setHealthScore(int healthScore) { this.healthScore = healthScore; }

        public String getHealthState() { return healthState; }
        public void setHealthState(String healthState) { this.healthState = healthState; }

        public String getCoachMessage() { return coachMessage; }
        public void setCoachMessage(String coachMessage) { this.coachMessage = coachMessage; }

        public String getPenguinAnimation() { return penguinAnimation; }
        public void setPenguinAnimation(String penguinAnimation) { this.penguinAnimation = penguinAnimation; }

        public List<ProblemMetric> getProblemMetrics() { return problemMetrics; }
        public void setProblemMetrics(List<ProblemMetric> problemMetrics) { this.problemMetrics = problemMetrics; }
    }

    // ============================================================================
    // 핵심 점수 계산 함수
    // ============================================================================

    /**
     * 개별 메트릭의 심각도를 0.0~1.0 사이의 값으로 계산
     *
     * @param value 현재 메트릭 값
     * @param bandUpper Anomaly Detection 상한 밴드 (있으면 우선 사용)
     * @param bandLower Anomaly Detection 하한 밴드
     * @param metricType 메트릭 타입 ('error_rate', 'latency', 'cpu')
     * @return 심각도 (0.0 = 완전 정상, 1.0 = 매우 위험)
     */
    public static double calculateSeverity(double value, Double bandUpper, Double bandLower, String metricType) {
        // 1. Anomaly Detection Band가 있는 경우 (우선순위)
        if (bandUpper != null && bandLower != null) {
            // 밴드 안에 있으면 정상
            if (value >= bandLower && value <= bandUpper) {
                return 0.0;
            }

            // 밴드 밖으로 벗어난 정도 계산
            double deviation;
            if (value > bandUpper) {
                // 상한 초과: 얼마나 많이 벗어났는지
                deviation = (value - bandUpper) / bandUpper;
            } else {
                // 하한 미만: 얼마나 많이 벗어났는지
                deviation = (bandLower - value) / bandLower;
            }

            // 50% 이상 벗어나면 최대 위험으로 간주
            double severity = Math.min(1.0, deviation * 2.0);
            return severity;
        }

        // 2. Fallback 임계값 사용
        ThresholdConfig threshold = FALLBACK_THRESHOLDS.get(metricType);
        if (threshold == null) {
            // 알 수 없는 메트릭 타입: 중간 값 반환
            return 0.5;
        }

        if (value <= threshold.getNormal()) {
            // 정상 범위
            return 0.0;
        } else if (value <= threshold.getWarning()) {
            // 정상~주의 구간: 선형 보간 (0.0 → 0.5)
            double ratio = (value - threshold.getNormal()) / (threshold.getWarning() - threshold.getNormal());
            return ratio * 0.5;
        } else if (value <= threshold.getDanger()) {
            // 주의~위험 구간: 선형 보간 (0.5 → 0.8)
            double ratio = (value - threshold.getWarning()) / (threshold.getDanger() - threshold.getWarning());
            return 0.5 + (ratio * 0.3);
        } else {
            // 위험 초과: 선형 증가 (0.8 → 1.0)
            double ratio = Math.min(1.0, (value - threshold.getDanger()) / threshold.getDanger());
            return 0.8 + (ratio * 0.2);
        }
    }

    /**
     * 여러 메트릭의 심각도를 종합하여 0~100점의 건강 점수 계산
     *
     * @param metrics 메트릭 데이터 Map<String, MetricData>
     * @return 건강 점수 (0 = 완벽, 100 = 매우 위험)
     */
    public static int calculateHealthScore(Map<String, MetricData> metrics) {
        double totalScore = 0.0;
        double totalWeight = 0.0;

        for (Map.Entry<String, Double> entry : METRIC_WEIGHTS.entrySet()) {
            String metricName = entry.getKey();
            double weight = entry.getValue();

            MetricData metricData = metrics.get(metricName);

            // 메트릭 데이터가 없으면 건너뛰기
            if (metricData == null) {
                continue;
            }

            // 개별 메트릭 심각도 계산
            double severity = calculateSeverity(
                metricData.getValue(),
                metricData.getBandUpper(),
                metricData.getBandLower(),
                metricName
            );

            // 가중치 적용
            totalScore += severity * weight * 100;
            totalWeight += weight;
        }

        // 가중 평균 계산
        double finalScore;
        if (totalWeight > 0) {
            finalScore = totalScore / totalWeight;
        } else {
            // 메트릭이 하나도 없으면 중간 점수
            finalScore = 50;
        }

        // 0~100 범위로 클리핑
        return (int) Math.max(0, Math.min(100, finalScore));
    }

    /**
     * 점수를 3단계 상태로 분류
     *
     * @param score 건강 점수 (0~100)
     * @return 'healthy' | 'warning' | 'danger'
     */
    public static String classifyState(int score) {
        if (score <= STATE_SCORE_RANGES.get("healthy")[1]) {
            return "healthy";
        } else if (score <= STATE_SCORE_RANGES.get("warning")[1]) {
            return "warning";
        } else {
            return "danger";
        }
    }

    // ============================================================================
    // 문제 메트릭 식별
    // ============================================================================

    /**
     * 문제가 있는 메트릭을 식별하고 심각도 순으로 정렬
     *
     * @param metrics 메트릭 데이터
     * @return 문제 메트릭 리스트 (심각도 높은 순)
     */
    public static List<ProblemMetric> identifyProblemMetrics(Map<String, MetricData> metrics) {
        List<ProblemMetric> problems = new ArrayList<>();

        for (Map.Entry<String, MetricData> entry : metrics.entrySet()) {
            String metricName = entry.getKey();
            MetricData metricData = entry.getValue();

            if (metricData == null) {
                continue;
            }

            double severity = calculateSeverity(
                metricData.getValue(),
                metricData.getBandUpper(),
                metricData.getBandLower(),
                metricName
            );

            // 심각도가 0.3 이상이면 문제로 간주
            if (severity >= 0.3) {
                problems.add(new ProblemMetric(metricName, severity));
            }
        }

        // 심각도 높은 순으로 정렬
        problems.sort((a, b) -> Double.compare(b.getSeverity(), a.getSeverity()));

        return problems;
    }

    // ============================================================================
    // 코칭 메시지 생성
    // ============================================================================

    /**
     * 주의 상태에 대한 코칭 메시지 생성
     */
    private static String generateWarningMessage(List<ProblemMetric> problemMetrics) {
        if (problemMetrics.isEmpty()) {
            return "⚠️ 조금 불안정해 보여요. 모니터링을 계속 지켜봐주세요!";
        }

        // 가장 심각한 문제 메트릭
        String worstMetric = problemMetrics.get(0).getMetricName();

        Map<String, String> messageMap = Map.of(
            "latency", "⚠️ 응답 속도가 약간 느려지고 있어요. DB 쿼리나 외부 API를 확인해보면 좋아요!",
            "cpu", "⚠️ CPU 사용률이 높아지고 있어요. 트래픽이 증가했거나 무거운 작업이 실행 중일 수 있어요!",
            "error_rate", "⚠️ 에러가 조금씩 발생하고 있어요. 로그를 확인해서 원인을 파악해보세요!"
        );

        return messageMap.getOrDefault(worstMetric, "⚠️ 일부 지표가 평소와 다릅니다. 주의 깊게 모니터링해주세요!");
    }

    /**
     * 위험 상태에 대한 코칭 메시지 생성
     */
    private static String generateDangerMessage(List<ProblemMetric> problemMetrics) {
        if (problemMetrics.isEmpty()) {
            return "🚨 위험한 상태에요! 즉시 점검이 필요해요!";
        }

        List<String> messages = new ArrayList<>();

        // 심각한 문제들을 모두 언급
        for (ProblemMetric problem : problemMetrics) {
            if (problem.getSeverity() < 0.7) {  // 위험 상태에서는 심각도 0.7 이상만
                continue;
            }

            switch (problem.getMetricName()) {
                case "error_rate":
                    messages.add("에러율이 급증했어요!");
                    break;
                case "latency":
                    messages.add("응답이 매우 느려요!");
                    break;
                case "cpu":
                    messages.add("CPU가 과부하 상태에요!");
                    break;
            }
        }

        if (messages.isEmpty()) {
            return "🚨 서비스 상태가 불안정해요! 즉시 확인이 필요합니다!";
        }

        // 첫 문제에 대한 구체적 조언
        String worstMetric = problemMetrics.get(0).getMetricName();

        Map<String, String> adviceMap = Map.of(
            "error_rate", "최근 배포 내역을 확인하고, 에러 로그를 점검하세요!",
            "latency", "DB 연결 상태와 외부 API 응답 시간을 점검하세요!",
            "cpu", "오토스케일링을 고려하거나, 불필요한 프로세스를 종료하세요!"
        );

        String mainMessage = String.join(" ", messages);
        String advice = adviceMap.getOrDefault(worstMetric, "시스템 리소스와 최근 변경사항을 확인하세요!");

        return String.format("🚨 %s %s", mainMessage, advice);
    }

    /**
     * 상황에 맞는 펭귄 코치 메시지 생성
     */
    public static String generateCoachMessage(String state, Map<String, MetricData> metrics) {
        if ("healthy".equals(state)) {
            Random random = new Random();
            return HEALTHY_MESSAGES.get(random.nextInt(HEALTHY_MESSAGES.size()));
        }

        // 문제가 있는 메트릭 식별
        List<ProblemMetric> problemMetrics = identifyProblemMetrics(metrics);

        if ("warning".equals(state)) {
            return generateWarningMessage(problemMetrics);
        }

        if ("danger".equals(state)) {
            return generateDangerMessage(problemMetrics);
        }

        // 알 수 없는 상태 (방어 코드)
        return "펭귄이 상태를 분석하고 있어요...";
    }

    // ============================================================================
    // 통합 분석 함수 (메인 API)
    // ============================================================================

    /**
     * 배포 상태를 종합 분석하여 점수, 상태, 메시지를 반환
     *
     * 이것이 메인 API 함수입니다. Backend에서 이 함수를 호출하면 됩니다.
     *
     * @param metrics 메트릭 데이터 Map<String, MetricData>
     * @return HealthAnalysisResult 분석 결과
     */
    public static HealthAnalysisResult analyzeDeploymentHealth(Map<String, MetricData> metrics) {
        HealthAnalysisResult result = new HealthAnalysisResult();

        // 1. 건강 점수 계산
        int healthScore = calculateHealthScore(metrics);
        result.setHealthScore(healthScore);

        // 2. 상태 분류
        String healthState = classifyState(healthScore);
        result.setHealthState(healthState);

        // 3. 코칭 메시지 생성
        String coachMessage = generateCoachMessage(healthState, metrics);
        result.setCoachMessage(coachMessage);

        // 4. 펭귄 애니메이션 선택
        Map<String, String> animationMap = Map.of(
            "healthy", "happy",
            "warning", "worried",
            "danger", "crying"
        );
        String penguinAnimation = animationMap.get(healthState);
        result.setPenguinAnimation(penguinAnimation);

        // 5. 문제 메트릭 식별
        List<ProblemMetric> problemMetrics = identifyProblemMetrics(metrics);
        result.setProblemMetrics(problemMetrics);

        return result;
    }

    // ============================================================================
    // 테스트용 메인 함수
    // ============================================================================

    public static void main(String[] args) {
        System.out.println("=".repeat(70));
        System.out.println("Penguin-Land Score Engine 테스트");
        System.out.println("=".repeat(70));

        // 테스트 케이스 1: 완벽한 상태
        System.out.println("\n[테스트 1] 완벽한 배포 상태");
        Map<String, MetricData> metricsPerfect = new HashMap<>();
        metricsPerfect.put("error_rate", new MetricData(0.2, 2.0, 0.1));
        metricsPerfect.put("latency", new MetricData(180, 600.0, 100.0));
        metricsPerfect.put("cpu", new MetricData(35));

        HealthAnalysisResult result1 = analyzeDeploymentHealth(metricsPerfect);
        System.out.println("점수: " + result1.getHealthScore() + "점");
        System.out.println("상태: " + result1.getHealthState());
        System.out.println("메시지: " + result1.getCoachMessage());
        System.out.println("펭귄: " + result1.getPenguinAnimation());

        // 테스트 케이스 2: 주의 상태
        System.out.println("\n[테스트 2] 주의가 필요한 상태");
        Map<String, MetricData> metricsWarning = new HashMap<>();
        metricsWarning.put("error_rate", new MetricData(3.5));
        metricsWarning.put("latency", new MetricData(550, 600.0, 200.0));
        metricsWarning.put("cpu", new MetricData(72));

        HealthAnalysisResult result2 = analyzeDeploymentHealth(metricsWarning);
        System.out.println("점수: " + result2.getHealthScore() + "점");
        System.out.println("상태: " + result2.getHealthState());
        System.out.println("메시지: " + result2.getCoachMessage());
        System.out.println("펭귄: " + result2.getPenguinAnimation());

        // 테스트 케이스 3: 위험 상태
        System.out.println("\n[테스트 3] 위험한 상태");
        Map<String, MetricData> metricsDanger = new HashMap<>();
        metricsDanger.put("error_rate", new MetricData(8.5));
        metricsDanger.put("latency", new MetricData(1800));
        metricsDanger.put("cpu", new MetricData(92));

        HealthAnalysisResult result3 = analyzeDeploymentHealth(metricsDanger);
        System.out.println("점수: " + result3.getHealthScore() + "점");
        System.out.println("상태: " + result3.getHealthState());
        System.out.println("메시지: " + result3.getCoachMessage());
        System.out.println("펭귄: " + result3.getPenguinAnimation());
        System.out.println("문제 메트릭: " + result3.getProblemMetrics().size() + "개");

        System.out.println("\n" + "=".repeat(70));
        System.out.println("테스트 완료!");
        System.out.println("=".repeat(70));
    }
}
