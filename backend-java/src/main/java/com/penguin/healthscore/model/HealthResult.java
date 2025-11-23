package com.penguin.healthscore.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class HealthResult {
    private int healthScore;
    private String healthState;      // "healthy", "warning", "danger"
    private String penguinAnimation;  // "happy", "worried", "crying"
    private String coachMessage;
    private List<ProblemMetric> problemMetrics = new ArrayList<>();  // 문제 메트릭 목록

    /**
     * 문제 메트릭 정보
     */
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ProblemMetric {
        private String metricName;    // "error_rate", "latency", "cpu"
        private double severity;      // 0.0 ~ 1.0 (심각도)
        private String displayName;   // "에러율", "응답시간", "CPU"
    }
}
