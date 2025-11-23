package com.penguin.healthscore;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class PenguinLandApplication {

    public static void main(String[] args) {
        SpringApplication.run(PenguinLandApplication.class, args);

        System.out.println("======================================================================");
        System.out.println("Penguin-Land Health Score API Started!");
        System.out.println("======================================================================");
        System.out.println("Server: http://localhost:8080");
        System.out.println("Main API: http://localhost:8080/monitoring");
        System.out.println("Auto Simulation: POST http://localhost:8080/monitoring/simulate/auto");
        System.out.println("======================================================================");
    }
}
