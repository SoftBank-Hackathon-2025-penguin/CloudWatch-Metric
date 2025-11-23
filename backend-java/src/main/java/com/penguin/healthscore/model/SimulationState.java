package com.penguin.healthscore.model;

import lombok.Data;
import org.springframework.stereotype.Component;

@Data
@Component
public class SimulationState {

    private boolean active = false;
    private String scenario = "normal";
    private Long startTime = null;
    private Integer duration = null;
    private boolean autoRotate = false;
    private int rotateInterval = 20; // 20초마다 전환
    private String[] scenariosCycle = {"normal", "high_latency", "error_burst"};
    private int currentCycleIndex = 0;

    public void start(String scenario, Integer duration) {
        this.active = true;
        this.scenario = scenario;
        this.startTime = System.currentTimeMillis();
        this.duration = duration;
        this.autoRotate = false;
    }

    public void startAutoRotate(int interval) {
        this.active = true;
        this.autoRotate = true;
        this.rotateInterval = interval;
        this.startTime = System.currentTimeMillis();
        this.currentCycleIndex = 0;
        this.scenario = scenariosCycle[0];
        this.duration = null; // 무한 반복
    }

    public void stop() {
        this.active = false;
        this.scenario = "normal";
        this.startTime = null;
        this.duration = null;
        this.autoRotate = false;
    }

    public boolean isActive() {
        if (!active) {
            return false;
        }

        // 자동 전환 모드
        if (autoRotate && startTime != null) {
            long elapsed = (System.currentTimeMillis() - startTime) / 1000;
            int newIndex = (int) ((elapsed / rotateInterval) % scenariosCycle.length);

            if (newIndex != currentCycleIndex) {
                currentCycleIndex = newIndex;
                scenario = scenariosCycle[newIndex];
                System.out.println("\n🔄 자동 전환: " + scenario.toUpperCase() +
                                 " (경과: " + elapsed + "초)\n");
            }
            return true;
        }

        // 일반 모드
        if (duration != null && startTime != null) {
            long elapsed = (System.currentTimeMillis() - startTime) / 1000;
            if (elapsed > duration) {
                stop();
                return false;
            }
        }

        return true;
    }
}
