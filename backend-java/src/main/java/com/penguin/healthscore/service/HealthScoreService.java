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
