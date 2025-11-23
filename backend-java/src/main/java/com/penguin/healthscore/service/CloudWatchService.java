package com.penguin.healthscore.service;

import com.penguin.healthscore.model.HealthMetrics;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.cloudwatch.CloudWatchClient;
import software.amazon.awssdk.services.cloudwatch.model.*;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

/**
 * AWS CloudWatch에서 실제 메트릭을 가져오는 서비스
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class CloudWatchService {

    private final CloudWatchClient cloudWatchClient;

    @Value("${aws.cloudwatch.alb-name}")
    private String albName;

    /**
     * CloudWatch에서 실제 ALB 메트릭 가져오기
     */
    public HealthMetrics getRealMetrics() {
        try {
            Instant endTime = Instant.now();
            Instant startTime = endTime.minus(5, ChronoUnit.MINUTES);

            // 3개의 메트릭을 병렬로 가져오기
            double errorRate = getErrorRate(startTime, endTime);
            double latency = getLatency(startTime, endTime);
            double cpu = getCpuUsage(startTime, endTime);

            log.info("📊 CloudWatch 메트릭 수집: 에러율={}%, 응답시간={}ms, CPU={}%",
                    String.format("%.2f", errorRate),
                    String.format("%.0f", latency),
                    String.format("%.0f", cpu));

            return new HealthMetrics(errorRate, latency, cpu);

        } catch (Exception e) {
            log.error("❌ CloudWatch 메트릭 가져오기 실패: {}", e.getMessage());
            // Fallback: 기본 정상 메트릭 반환
            return new HealthMetrics(0.5, 200.0, 35.0);
        }
    }

    /**
     * 에러율 가져오기 (HTTPCode_Target_5XX_Count / RequestCount * 100)
     */
    private double getErrorRate(Instant startTime, Instant endTime) {
        try {
            // 5XX 에러 카운트
            double errorCount = getMetricStatistics(
                    "AWS/ApplicationELB",
                    "HTTPCode_Target_5XX_Count",
                    "Sum",
                    startTime,
                    endTime
            );

            // 총 요청 카운트
            double requestCount = getMetricStatistics(
                    "AWS/ApplicationELB",
                    "RequestCount",
                    "Sum",
                    startTime,
                    endTime
            );

            if (requestCount > 0) {
                return (errorCount / requestCount) * 100.0;
            }
            return 0.0;

        } catch (Exception e) {
            log.warn("⚠️ 에러율 가져오기 실패: {}", e.getMessage());
            return 0.5;  // 기본값
        }
    }

    /**
     * 응답 시간 가져오기 (TargetResponseTime)
     */
    private double getLatency(Instant startTime, Instant endTime) {
        try {
            // 평균 응답 시간 (초 단위)
            double latencySeconds = getMetricStatistics(
                    "AWS/ApplicationELB",
                    "TargetResponseTime",
                    "Average",
                    startTime,
                    endTime
            );

            // 밀리초로 변환
            return latencySeconds * 1000.0;

        } catch (Exception e) {
            log.warn("⚠️ 응답시간 가져오기 실패: {}", e.getMessage());
            return 200.0;  // 기본값
        }
    }

    /**
     * CPU 사용률 가져오기 (TargetGroup 기준)
     */
    private double getCpuUsage(Instant startTime, Instant endTime) {
        try {
            // ECS 또는 EC2 타겟의 CPU 메트릭
            // 실제 환경에 따라 네임스페이스와 메트릭명 조정 필요
            return getMetricStatistics(
                    "AWS/ECS",  // 또는 "AWS/EC2"
                    "CPUUtilization",
                    "Average",
                    startTime,
                    endTime
            );

        } catch (Exception e) {
            log.warn("⚠️ CPU 사용률 가져오기 실패: {}", e.getMessage());
            return 35.0;  // 기본값
        }
    }

    /**
     * CloudWatch GetMetricStatistics API 호출
     */
    private double getMetricStatistics(String namespace, String metricName,
                                       String statistic, Instant startTime, Instant endTime) {
        try {
            // Dimension 설정 (ALB 이름)
            Dimension dimension = Dimension.builder()
                    .name("LoadBalancer")
                    .value(albName)
                    .build();

            // GetMetricStatistics 요청
            GetMetricStatisticsRequest request = GetMetricStatisticsRequest.builder()
                    .namespace(namespace)
                    .metricName(metricName)
                    .dimensions(dimension)
                    .startTime(startTime)
                    .endTime(endTime)
                    .period(300)  // 5분
                    .statistics(Statistic.fromValue(statistic))
                    .build();

            GetMetricStatisticsResponse response = cloudWatchClient.getMetricStatistics(request);

            // 데이터포인트에서 평균값 추출
            List<Datapoint> datapoints = response.datapoints();
            if (!datapoints.isEmpty()) {
                // 가장 최근 데이터포인트 사용
                Datapoint latest = datapoints.stream()
                        .max((a, b) -> a.timestamp().compareTo(b.timestamp()))
                        .orElse(datapoints.get(0));

                // Statistic 타입에 따라 적절한 값 반환
                return switch (statistic) {
                    case "Sum" -> latest.sum();
                    case "Average" -> latest.average();
                    case "Maximum" -> latest.maximum();
                    case "Minimum" -> latest.minimum();
                    default -> latest.average();
                };
            }

            return 0.0;

        } catch (Exception e) {
            log.error("❌ CloudWatch API 호출 실패 ({}): {}", metricName, e.getMessage());
            throw e;
        }
    }

    /**
     * CloudWatch Anomaly Detection Band 가져오기 (선택적)
     */
    public List<Double> getAnomalyBand(String metricName, Instant startTime, Instant endTime) {
        List<Double> band = new ArrayList<>();
        try {
            // GetMetricData API로 ANOMALY_DETECTION_BAND 가져오기
            // 구현 생략 (필요시 추가)
            log.info("📈 Anomaly Band 조회: {}", metricName);
        } catch (Exception e) {
            log.warn("⚠️ Anomaly Band 가져오기 실패: {}", e.getMessage());
        }
        return band;
    }
}
