package com.penguin.healthscore.model;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class HealthResult {
    private int healthScore;
    private String healthState;      // "healthy", "warning", "danger"
    private String penguinAnimation;  // "happy", "worried", "crying"
    private String coachMessage;
}
