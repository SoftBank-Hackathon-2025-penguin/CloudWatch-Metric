package com.penguin.healthscore.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

import java.time.Instant;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.util.*;

/**
 * Slack Webhook으로 건강 점수 경보를 전송하는 서비스
 */
@Slf4j
@Service
public class SlackService {

    @Value("${slack.webhook-url:#{null}}")
    private String slackWebhookUrl;

    private final WebClient webClient;
    private final ObjectMapper objectMapper;

    private static final DateTimeFormatter FORMATTER =
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")
            .withZone(ZoneId.of("UTC"));

    public SlackService() {
        this.webClient = WebClient.builder()
            .defaultHeader(HttpHeaders.CONTENT_TYPE, MediaType.APPLICATION_JSON_VALUE)
            .build();
        this.objectMapper = new ObjectMapper();
    }

    /**
     * Slack으로 건강 점수 경보 전송 (70점 이상일 때만)
     */
    public void sendHealthAlert(int healthScore, String healthState,
                               String coachMessage, Map<String, Double> metrics) {

        // 🔕 Slack 알림 비활성화 옵션 (필요시 이 return 주석 제거)
        // return;

        // 70점 미만이면 전송 안 함
        if (healthScore < 70) {
            return;
        }

        // Webhook URL이 없으면 전송 안 함
        if (slackWebhookUrl == null || slackWebhookUrl.isEmpty()) {
            log.warn("⚠️ Slack Webhook URL이 설정되지 않았습니다!");
            return;
        }

        // 상태별 이모지
        String emoji = getEmojiForState(healthState);

        // Slack Block Kit 메시지 생성
        Map<String, Object> message = createSlackMessage(
            emoji, healthScore, healthState, coachMessage, metrics
        );

        try {
            // HTTP POST 요청
            webClient.post()
                .uri(slackWebhookUrl)
                .bodyValue(message)
                .retrieve()
                .bodyToMono(String.class)
                .subscribe(
                    response -> log.info("✅ Slack 알림 전송! (점수: {}점)", healthScore),
                    error -> log.error("❌ Slack 알림 실패: {}", error.getMessage())
                );

        } catch (Exception e) {
            log.error("❌ Slack 오류: {}", e.getMessage());
        }
    }

    /**
     * Slack Block Kit 메시지 생성
     */
    private Map<String, Object> createSlackMessage(String emoji, int healthScore,
                                                   String healthState, String coachMessage,
                                                   Map<String, Double> metrics) {
        List<Map<String, Object>> blocks = new ArrayList<>();

        // 헤더 블록
        blocks.add(Map.of(
            "type", "header",
            "text", Map.of(
                "type", "plain_text",
                "text", emoji + " Penguin-Land 배포 경보!"
            )
        ));

        // 점수 및 상태 블록
        blocks.add(Map.of(
            "type", "section",
            "fields", Arrays.asList(
                Map.of("type", "mrkdwn", "text", "*점수:*\n" + healthScore + "/100점"),
                Map.of("type", "mrkdwn", "text", "*상태:*\n" + healthState.toUpperCase())
            )
        ));

        // 메시지 블록
        blocks.add(Map.of(
            "type", "section",
            "text", Map.of(
                "type", "mrkdwn",
                "text", "*메시지:*\n" + coachMessage
            )
        ));

        // 구분선
        blocks.add(Map.of("type", "divider"));

        // 메트릭 상세 정보
        blocks.add(Map.of(
            "type", "section",
            "fields", Arrays.asList(
                Map.of("type", "mrkdwn",
                       "text", "*에러율:*\n" + String.format("%.2f%%", metrics.get("errorRate"))),
                Map.of("type", "mrkdwn",
                       "text", "*응답시간:*\n" + String.format("%.0fms", metrics.get("latency"))),
                Map.of("type", "mrkdwn",
                       "text", "*CPU:*\n" + String.format("%.0f%%", metrics.get("cpu")))
            )
        ));

        // 타임스탬프
        blocks.add(Map.of(
            "type", "context",
            "elements", Collections.singletonList(
                Map.of("type", "mrkdwn",
                       "text", "🕐 " + FORMATTER.format(Instant.now()) + " UTC")
            )
        ));

        return Map.of("blocks", blocks);
    }

    /**
     * 상태별 이모지 반환
     */
    private String getEmojiForState(String healthState) {
        return switch (healthState.toLowerCase()) {
            case "healthy" -> "✅";
            case "warning" -> "⚠️";
            case "danger" -> "🚨";
            default -> "⚠️";
        };
    }
}
