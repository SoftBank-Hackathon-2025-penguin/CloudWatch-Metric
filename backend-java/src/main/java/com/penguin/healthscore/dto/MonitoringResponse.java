package com.penguin.healthscore.dto;

import lombok.Data;
import java.util.*;

@Data
public class MonitoringResponse {
    private Map<String, Object> metrics;
    private Map<String, Object> anomaly;
    private List<Object> alerts;
}
