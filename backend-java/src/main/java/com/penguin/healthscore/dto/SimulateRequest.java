package com.penguin.healthscore.dto;

import lombok.Data;

@Data
public class SimulateRequest {
    private String scenario;    // "normal", "high_latency", "error_burst", "cpu_spike"
    private Integer duration;   // 지속 시간 (초)
}
