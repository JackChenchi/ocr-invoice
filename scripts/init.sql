CREATE DATABASE IF NOT EXISTS ocr_db;
USE ocr_db;

CREATE TABLE IF NOT EXISTS `ocr_results` (
  `id` BIGINT NOT NULL AUTO_INCREMENT,
  `file_name` VARCHAR(255) NOT NULL,
  `file_size` INT NOT NULL,
  `upload_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ocr_text` LONGTEXT,
  `confidence` FLOAT,
  `process_time` FLOAT,
  `status` ENUM('pending', 'processing', 'completed', 'failed') NOT NULL DEFAULT 'pending',
  `error_msg` TEXT,
  `image_url` VARCHAR(512),
  `coordinates` JSON,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
