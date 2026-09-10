CREATE DATABASE IF NOT EXISTS weather_prediction;

USE weather_prediction;

CREATE TABLE IF NOT EXISTS sensor_readings (
    id INT NOT NULL AUTO_INCREMENT,
    timestamp DATETIME NOT NULL,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    rain_value INT NOT NULL,
    rain_status VARCHAR(20) DEFAULT NULL,
    source VARCHAR(50) DEFAULT 'ESP32',
    device_id VARCHAR(50) NOT NULL DEFAULT 'ESP32_001',
    location VARCHAR(50) NOT NULL DEFAULT 'Kasoa',
    PRIMARY KEY (id)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_0900_ai_ci;