package com.penguin.healthscore.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class HealthMetrics {
    private double errorRate;
    private double latency;
    private double cpu;
}
