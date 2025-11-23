package com.penguin.healthscore.controller;

import com.penguin.healthscore.dto.MonitoringResponse;
import com.penguin.healthscore.dto.SimulateRequest;
import com.penguin.healthscore.model.*;
import com.penguin.healthscore.service.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.Instant;
import java.util.*;

@RestController
@RequiredArgsConstructor
@RequestMapping
@CrossOrigin(origins = "*")
public class MonitoringController {

    private final SimulationService simulationService;
    private final HealthScoreService healthScoreService;
    private final SimulationState simulationState;

    /**
     * 메인 모니터링 API (프론트엔드가 5초마다 호출)
     */
    @GetMapping("/monitoring")
    public ResponseEntity<MonitoringResponse> getMonitoring() {
        // 시뮬레이션 모드 체크
        HealthMetrics metrics = simulationService.getSimulatedMetrics();

        // 실제 데이터가 필요한 경우 (시뮬레이션이 없을 때)
        if (metrics == null) {
            // Fallback: 기본 정상 메트릭
            metrics = new HealthMetrics(0.5, 200.0, 35.0);
        }

        // 점수 계산
        HealthResult result = healthScoreService.analyzeDeploymentHealth(metrics);

        // 응답 생성
        MonitoringResponse response = new MonitoringResponse();
        response.setMetrics(Map.of(
            "cpuUsage", metrics.getCpu(),
            "latency", metrics.getLatency(),
            "errorRate", metrics.getErrorRate(),
            "timestamp", Instant.now().toString()
        ));

        response.setAnomaly(Map.of(
            "healthScore", result.getHealthScore(),
            "healthState", result.getHealthState(),
            "penguinAnimation", result.getPenguinAnimation(),
            "coachMessage", result.getCoachMessage()
        ));

        response.setAlerts(new ArrayList<>());

        return ResponseEntity.ok(response);
    }

    /**
     * 자동 시뮬레이션 시작 (20초마다 자동 전환)
     */
    @PostMapping("/monitoring/simulate/auto")
    public ResponseEntity<Map<String, Object>> startAutoSimulation(
            @RequestParam(defaultValue = "20") int interval) {

        simulationState.startAutoRotate(interval);

        System.out.println("\n" + "🎬".repeat(35));
        System.out.println("🔄 자동 시나리오 전환 시작!");
        System.out.println("⏱️  전환 간격: " + interval + "초");
        System.out.println("📋 순서: " + String.join(" → ", simulationState.getScenariosCycle()));
        System.out.println("🎬".repeat(35) + "\n");

        return ResponseEntity.ok(Map.of(
            "status", "auto_started",
            "interval", interval,
            "scenarios", simulationState.getScenariosCycle(),
            "message", interval + "초마다 자동으로 시나리오가 전환됩니다"
        ));
    }

    /**
     * 수동 시뮬레이션 시작
     */
    @PostMapping("/monitoring/simulate/start")
    public ResponseEntity<Map<String, Object>> startSimulation(
            @RequestBody SimulateRequest request) {

        simulationState.start(request.getScenario(), request.getDuration());

        System.out.println("\n" + "🎬".repeat(35));
        System.out.println("🎭 시뮬레이션 시작: " + request.getScenario().toUpperCase());
        if (request.getDuration() != null) {
            System.out.println("⏱️  지속 시간: " + request.getDuration() + "초");
        }
        System.out.println("🎬".repeat(35) + "\n");

        return ResponseEntity.ok(Map.of(
            "status", "started",
            "scenario", request.getScenario(),
            "message", "시뮬레이션 '" + request.getScenario() + "' 시작됨"
        ));
    }

    /**
     * 시뮬레이션 종료
     */
    @PostMapping("/monitoring/simulate/stop")
    public ResponseEntity<Map<String, Object>> stopSimulation() {
        boolean wasActive = simulationState.isActive();
        simulationState.stop();

        if (wasActive) {
            System.out.println("\n" + "🛑".repeat(35));
            System.out.println("🎭 시뮬레이션 종료");
            System.out.println("🛑".repeat(35) + "\n");
        }

        return ResponseEntity.ok(Map.of(
            "status", "stopped",
            "message", wasActive ? "시뮬레이션 종료됨" : "시뮬레이션이 실행 중이 아닙니다"
        ));
    }

    /**
     * 헬스 체크
     */
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> healthCheck() {
        return ResponseEntity.ok(Map.of(
            "status", "UP",
            "service", "Penguin-Land Health Score API",
            "version", "1.0.0"
        ));
    }
}
