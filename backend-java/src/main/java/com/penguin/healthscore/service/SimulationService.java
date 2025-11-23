package com.penguin.healthscore.service;

import com.penguin.healthscore.model.HealthMetrics;
import com.penguin.healthscore.model.SimulationState;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.Random;

@Service
@RequiredArgsConstructor
public class SimulationService {

    private final SimulationState simulationState;
    private final Random random = new Random();

    /**
     * 시뮬레이션 메트릭 생성
     */
    public HealthMetrics getSimulatedMetrics() {
        if (!simulationState.isActive()) {
            return null;
        }

        long elapsed = (System.currentTimeMillis() - simulationState.getStartTime()) / 1000;

        // 사인파 + 랜덤 노이즈
        double wave = Math.sin(elapsed * 0.5) * 0.3;
        double noise = (random.nextDouble() - 0.5) * 0.2;

        HealthMetrics metrics;

        switch (simulationState.getScenario()) {
            case "high_latency":
                metrics = new HealthMetrics(
                    Math.max(0, 1.5 + noise),
                    Math.max(800, 1200 + wave * 400 + noise * 200),
                    Math.max(30, 55 + wave * 15 + noise * 10)
                );
                break;

            case "error_burst":
                metrics = new HealthMetrics(
                    Math.max(2, 8 + wave * 4 + noise * 2),
                    Math.max(200, 450 + wave * 150 + noise * 80),
                    Math.max(40, 65 + wave * 15 + noise * 10)
                );
                break;

            case "cpu_spike":
                metrics = new HealthMetrics(
                    Math.max(0, 0.5 + noise),
                    Math.max(100, 250 + wave * 100 + noise * 50),
                    Math.max(75, 90 + wave * 5 + noise * 3)
                );
                break;

            default: // "normal"
                metrics = new HealthMetrics(
                    Math.max(0, 0.3 + wave + noise),
                    Math.max(50, 180 + wave * 50 + noise * 30),
                    Math.max(20, 35 + wave * 10 + noise * 5)
                );
        }

        System.out.println("\n" + "=".repeat(70));
        System.out.println("🎭 시뮬레이션 모드: " + simulationState.getScenario().toUpperCase());
        System.out.println("=".repeat(70));
        System.out.println("1️⃣ 에러율: " + String.format("%.2f", metrics.getErrorRate()) + "%");
        System.out.println("2️⃣ 응답시간: " + Math.round(metrics.getLatency()) + "ms");
        System.out.println("3️⃣ CPU 사용률: " + String.format("%.1f", metrics.getCpu()) + "%");
        System.out.println("=".repeat(70) + "\n");

        return metrics;
    }
}
