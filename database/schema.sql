-- Video Overlay SaaS - Database Schema
-- MySQL 8.0+ with utf8mb4

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- Users table
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(255) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL,
  `role` ENUM('user', 'admin') NOT NULL DEFAULT 'user',
  `status` ENUM('active', 'suspended', 'deleted') NOT NULL DEFAULT 'active',
  `email_verified` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  KEY `role` (`role`),
  KEY `status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User profiles
CREATE TABLE IF NOT EXISTS `user_profiles` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `first_name` VARCHAR(100) DEFAULT NULL,
  `last_name` VARCHAR(100) DEFAULT NULL,
  `avatar` VARCHAR(255) DEFAULT NULL,
  `timezone` VARCHAR(50) DEFAULT 'UTC',
  `language` VARCHAR(10) DEFAULT 'en',
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fk_profiles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Balance/credits system
CREATE TABLE IF NOT EXISTS `balances` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `credits` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `minutes` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `total_spent_credits` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `total_rendered_minutes` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`),
  CONSTRAINT `fk_balances_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Balance transactions (history)
CREATE TABLE IF NOT EXISTS `balance_transactions` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `type` ENUM('credit', 'debit', 'refund') NOT NULL,
  `amount` DECIMAL(10,2) NOT NULL,
  `description` VARCHAR(255) DEFAULT NULL,
  `reference_id` INT UNSIGNED DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `type` (`type`),
  CONSTRAINT `fk_transactions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Videos (uploaded files)
CREATE TABLE IF NOT EXISTS `videos` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `original_filename` VARCHAR(255) NOT NULL,
  `storage_path` VARCHAR(500) NOT NULL,
  `file_size` BIGINT UNSIGNED NOT NULL,
  `duration` DECIMAL(10,2) DEFAULT NULL,
  `width` INT UNSIGNED DEFAULT NULL,
  `height` INT UNSIGNED DEFAULT NULL,
  `format` VARCHAR(20) DEFAULT NULL,
  `status` ENUM('uploaded', 'processing', 'ready', 'failed', 'deleted') NOT NULL DEFAULT 'uploaded',
  `metadata` JSON DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `status` (`status`),
  CONSTRAINT `fk_videos_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Presets (overlay configurations)
CREATE TABLE IF NOT EXISTS `presets` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NULL,
  `name` VARCHAR(255) NOT NULL,
  `description` TEXT DEFAULT NULL,
  `is_global` TINYINT(1) NOT NULL DEFAULT 0,
  `is_default` TINYINT(1) NOT NULL DEFAULT 0,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` TIMESTAMP NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `is_global` (`is_global`),
  CONSTRAINT `fk_presets_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Preset items (individual overlay elements)
CREATE TABLE IF NOT EXISTS `preset_items` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `preset_id` INT UNSIGNED NOT NULL,
  `type` ENUM('subscribe', 'like', 'title') NOT NULL,
  `position_x` VARCHAR(20) NOT NULL DEFAULT 'center',
  `position_y` VARCHAR(20) NOT NULL DEFAULT 'center',
  `start_time` DECIMAL(10,2) DEFAULT 0.00,
  `end_time` DECIMAL(10,2) DEFAULT NULL,
  `opacity` DECIMAL(3,2) NOT NULL DEFAULT 1.00,
  `scale` DECIMAL(3,2) NOT NULL DEFAULT 1.00,
  `animation` ENUM('none', 'fade', 'bounce', 'slide') NOT NULL DEFAULT 'none',
  `text` VARCHAR(500) DEFAULT NULL,
  `font_size` INT UNSIGNED DEFAULT 24,
  `font_color` VARCHAR(7) DEFAULT '#FFFFFF',
  `background_color` VARCHAR(7) DEFAULT NULL,
  `order` INT UNSIGNED NOT NULL DEFAULT 0,
  `config` JSON DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `preset_id` (`preset_id`),
  CONSTRAINT `fk_preset_items_preset` FOREIGN KEY (`preset_id`) REFERENCES `presets` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Render jobs
CREATE TABLE IF NOT EXISTS `render_jobs` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED NOT NULL,
  `video_id` INT UNSIGNED NOT NULL,
  `preset_id` INT UNSIGNED NOT NULL,
  `status` ENUM('pending', 'processing', 'completed', 'failed', 'cancelled') NOT NULL DEFAULT 'pending',
  `priority` INT NOT NULL DEFAULT 0,
  `output_path` VARCHAR(500) DEFAULT NULL,
  `output_filename` VARCHAR(255) DEFAULT NULL,
  `output_size` BIGINT UNSIGNED DEFAULT NULL,
  `error_message` TEXT DEFAULT NULL,
  `progress` INT UNSIGNED NOT NULL DEFAULT 0,
  `started_at` TIMESTAMP NULL DEFAULT NULL,
  `completed_at` TIMESTAMP NULL DEFAULT NULL,
  `retry_count` INT UNSIGNED NOT NULL DEFAULT 0,
  `max_retries` INT UNSIGNED NOT NULL DEFAULT 3,
  `worker_id` VARCHAR(100) DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `video_id` (`video_id`),
  KEY `preset_id` (`preset_id`),
  KEY `status` (`status`),
  KEY `priority` (`priority`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `fk_jobs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_jobs_video` FOREIGN KEY (`video_id`) REFERENCES `videos` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_jobs_preset` FOREIGN KEY (`preset_id`) REFERENCES `presets` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- System settings
CREATE TABLE IF NOT EXISTS `system_settings` (
  `id` INT UNSIGNED NOT NULL AUTO_INCREMENT,
  `key` VARCHAR(100) NOT NULL,
  `value` TEXT DEFAULT NULL,
  `type` ENUM('string', 'integer', 'float', 'boolean', 'json') NOT NULL DEFAULT 'string',
  `description` VARCHAR(255) DEFAULT NULL,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `key` (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Activity logs
CREATE TABLE IF NOT EXISTS `logs` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT UNSIGNED DEFAULT NULL,
  `type` VARCHAR(50) NOT NULL,
  `action` VARCHAR(100) NOT NULL,
  `message` TEXT DEFAULT NULL,
  `ip_address` VARCHAR(45) DEFAULT NULL,
  `user_agent` VARCHAR(500) DEFAULT NULL,
  `data` JSON DEFAULT NULL,
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `type` (`type`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `fk_logs_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Sessions (for authentication)
CREATE TABLE IF NOT EXISTS `sessions` (
  `id` VARCHAR(128) NOT NULL,
  `user_id` INT UNSIGNED NOT NULL,
  `ip_address` VARCHAR(45) DEFAULT NULL,
  `user_agent` VARCHAR(500) DEFAULT NULL,
  `data` TEXT DEFAULT NULL,
  `last_activity` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `last_activity` (`last_activity`),
  CONSTRAINT `fk_sessions_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default admin user (password: admin123 - change immediately!)
INSERT INTO `users` (`email`, `password_hash`, `role`, `status`, `email_verified`) VALUES
('admin@example.com', '$2y$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi', 'admin', 'active', 1);

-- Insert default system settings
INSERT INTO `system_settings` (`key`, `value`, `type`, `description`) VALUES
('max_upload_size', '104857600', 'integer', 'Max upload size in bytes (100MB)'),
('max_render_duration', '300', 'integer', 'Max render duration in seconds (5 minutes)'),
('credit_cost_per_minute', '1.00', 'float', 'Credit cost per minute of video'),
('output_width', '1080', 'integer', 'Default output video width'),
('output_height', '1920', 'integer', 'Default output video height'),
('output_format', 'mp4', 'string', 'Default output format'),
('queue_worker_count', '1', 'integer', 'Number of queue workers'),
('ffmpeg_threads', '4', 'integer', 'FFmpeg thread count');

SET FOREIGN_KEY_CHECKS = 1;
