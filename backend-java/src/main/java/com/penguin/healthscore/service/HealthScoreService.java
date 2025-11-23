package com.penguin.healthscore.service;

import com.penguin.healthscore.model.HealthMetrics;
import com.penguin.healthscore.model.HealthResult;
import com.penguin.healthscore.model.HealthResult.ProblemMetric;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

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

        // 각 메트릭의 심각도 계산 (0.0 ~ 1.0)
        double errorSeverity = calculateSeverity(
            metrics.getErrorRate(),
            errorThresholdWarning,
            errorThresholdDanger
        );

        double latencySeverity = calculateSeverity(
            metrics.getLatency(),
            latencyThresholdWarning,
            latencyThresholdDanger
        );

        double cpuSeverity = calculateSeverity(
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

        // 문제 메트릭 식별 (심각도 0.3 이상)
        List<ProblemMetric> problemMetrics = new ArrayList<>();

        if (errorSeverity >= 0.3) {
            problemMetrics.add(new ProblemMetric("error_rate", errorSeverity, "에러율"));
        }
        if (latencySeverity >= 0.3) {
            problemMetrics.add(new ProblemMetric("latency", latencySeverity, "응답시간"));
        }
        if (cpuSeverity >= 0.3) {
            problemMetrics.add(new ProblemMetric("cpu", cpuSeverity, "CPU"));
        }

        // 심각도 높은 순으로 정렬
        problemMetrics.sort(Comparator.comparingDouble(ProblemMetric::getSeverity).reversed());

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
            coachMessage = generateWarningMessage(problemMetrics);
        } else {
            healthState = "danger";
            penguinAnimation = "crying";
            coachMessage = generateDangerMessage(problemMetrics);
        }

        return new HealthResult(totalScore, healthState, penguinAnimation, coachMessage, problemMetrics);
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

    /**
     * 메트릭 심각도 계산 (0.0 ~ 1.0)
     */
    private double calculateSeverity(double value, double warningThreshold,
                                     double dangerThreshold) {
        if (value <= warningThreshold) {
            return 0.0;  // 정상
        } else if (value <= dangerThreshold) {
            // Warning 구간: 0.3 ~ 0.7
            double ratio = (value - warningThreshold) / (dangerThreshold - warningThreshold);
            return 0.3 + (ratio * 0.4);
        } else {
            // Danger 초과: 0.7 ~ 1.0
            double excess = value - dangerThreshold;
            double excessRatio = Math.min(excess / dangerThreshold, 1.0);
            return 0.7 + (excessRatio * 0.3);
        }
    }

    /**
     * Warning 상태 메시지 생성
     */
    private String generateWarningMessage(List<ProblemMetric> problemMetrics) {
        if (problemMetrics.isEmpty()) {
            return "⚠️ 조금 불안정해 보여요. 모니터링을 계속 지켜봐주세요!";
        }

        // 가장 심각한 문제 메트릭
        String worstMetric = problemMetrics.get(0).getMetricName();

        switch (worstMetric) {
            case "latency":
                return "⚠️ 응답 속도가 약간 느려지고 있어요. DB 쿼리나 외부 API를 확인해보면 좋아요!";
            case "cpu":
                return "⚠️ CPU 사용률이 높아지고 있어요. 트래픽이 증가했거나 무거운 작업이 실행 중일 수 있어요!";
            case "error_rate":
                return "⚠️ 에러가 조금씩 발생하고 있어요. 로그를 확인해서 원인을 파악해보세요!";
            default:
                return "⚠️ 일부 지표가 평소와 다릅니다. 주의 깊게 모니터링해주세요!";
        }
    }

    /**
     * Danger 상태 메시지 생성
     */
    private String generateDangerMessage(List<ProblemMetric> problemMetrics) {
        if (problemMetrics.isEmpty()) {
            return "🚨 위험한 상태에요! 즉시 점검이 필요해요!";
        }

        List<String> messages = new ArrayList<>();

        // 심각한 문제들 (severity >= 0.7)
        for (ProblemMetric metric : problemMetrics) {
            if (metric.getSeverity() < 0.7) continue;

            switch (metric.getMetricName()) {
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

        // 조언 추가
        String worstMetric = problemMetrics.get(0).getMetricName();
        String advice;

        switch (worstMetric) {
            case "error_rate":
                advice = "최근 배포 내역을 확인하고, 에러 로그를 점검하세요!";
                break;
            case "latency":
                advice = "DB 연결 상태와 외부 API 응답 시간을 점검하세요!";
                break;
            case "cpu":
                advice = "오토스케일링을 고려하거나, 불필요한 프로세스를 종료하세요!";
                break;
            default:
                advice = "시스템 리소스와 최근 변경사항을 확인하세요!";
        }

        return "🚨 " + String.join(" ", messages) + " " + advice;
    }
}
