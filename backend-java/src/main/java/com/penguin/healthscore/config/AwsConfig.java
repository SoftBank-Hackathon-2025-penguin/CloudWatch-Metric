package com.penguin.healthscore.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import software.amazon.awssdk.auth.credentials.AwsBasicCredentials;
import software.amazon.awssdk.auth.credentials.AwsCredentialsProvider;
import software.amazon.awssdk.auth.credentials.DefaultCredentialsProvider;
import software.amazon.awssdk.auth.credentials.StaticCredentialsProvider;
import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.cloudwatch.CloudWatchClient;

/**
 * AWS CloudWatch 클라이언트 설정
 */
@Configuration
public class AwsConfig {

    @Value("${aws.region:ap-northeast-2}")
    private String awsRegion;

    @Value("${aws.access-key-id:#{null}}")
    private String accessKeyId;

    @Value("${aws.secret-access-key:#{null}}")
    private String secretAccessKey;

    /**
     * CloudWatch 클라이언트 빈 생성
     */
    @Bean
    public CloudWatchClient cloudWatchClient() {
        AwsCredentialsProvider credentialsProvider = createCredentialsProvider();

        return CloudWatchClient.builder()
                .region(Region.of(awsRegion))
                .credentialsProvider(credentialsProvider)
                .build();
    }

    /**
     * AWS 자격 증명 제공자 생성
     *
     * 우선순위:
     * 1. application.yml의 명시적 키
     * 2. 환경 변수 (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)
     * 3. AWS CLI 설정 파일 (~/.aws/credentials)
     */
    private AwsCredentialsProvider createCredentialsProvider() {
        if (accessKeyId != null && !accessKeyId.isEmpty() &&
            secretAccessKey != null && !secretAccessKey.isEmpty()) {
            // 명시적 자격 증명
            return StaticCredentialsProvider.create(
                AwsBasicCredentials.create(accessKeyId, secretAccessKey)
            );
        } else {
            // 기본 자격 증명 체인 (환경 변수 → AWS CLI 설정)
            return DefaultCredentialsProvider.create();
        }
    }
}
