-- ShroomLab Database Initialization Script
-- This script creates the initial database structure

USE shroomlab;

-- Enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    role ENUM('admin', 'manager', 'operator', 'viewer') DEFAULT 'viewer',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role)
);

-- Create farms table
CREATE TABLE IF NOT EXISTS farms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    location VARCHAR(200),
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
    owner_id INT NOT NULL,
    total_area FLOAT,
    growing_rooms INT DEFAULT 1,
    max_capacity FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_owner (owner_id),
    INDEX idx_status (status)
);

-- Create sensors table
CREATE TABLE IF NOT EXISTS sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    location VARCHAR(200),
    device_id VARCHAR(100) UNIQUE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    min_threshold FLOAT,
    max_threshold FLOAT,
    alert_enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    INDEX idx_farm (farm_id),
    INDEX idx_device (device_id),
    INDEX idx_type (sensor_type)
);

-- Create growing_cycles table
CREATE TABLE IF NOT EXISTS growing_cycles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    mushroom_variety VARCHAR(100) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    expected_harvest_date TIMESTAMP,
    actual_harvest_date TIMESTAMP,
    status VARCHAR(50) DEFAULT 'active',
    substrate_weight FLOAT,
    expected_yield FLOAT,
    actual_yield FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    INDEX idx_farm (farm_id),
    INDEX idx_status (status),
    INDEX idx_variety (mushroom_variety)
);

-- Create production_logs table
CREATE TABLE IF NOT EXISTS production_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    growing_cycle_id INT NOT NULL,
    log_type VARCHAR(50) NOT NULL,
    description TEXT,
    quantity FLOAT,
    unit VARCHAR(20),
    performed_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (growing_cycle_id) REFERENCES growing_cycles(id) ON DELETE CASCADE,
    INDEX idx_cycle (growing_cycle_id),
    INDEX idx_type (log_type)
);

-- Create alerts table
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    sensor_id INT,
    alert_type VARCHAR(50) NOT NULL,
    severity VARCHAR(20) DEFAULT 'medium',
    title VARCHAR(200) NOT NULL,
    description TEXT,
    is_resolved BOOLEAN DEFAULT FALSE,
    resolved_at TIMESTAMP NULL,
    resolved_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE SET NULL,
    INDEX idx_farm (farm_id),
    INDEX idx_sensor (sensor_id),
    INDEX idx_severity (severity),
    INDEX idx_resolved (is_resolved)
);

-- Insert default admin user (password: admin123)
INSERT INTO users (username, email, hashed_password, full_name, role) VALUES 
('admin', 'admin@shroomlab.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdKuJP4HwHT5qza', 'System Administrator', 'admin')
ON DUPLICATE KEY UPDATE username = username;

-- Insert sample farm
INSERT INTO farms (name, description, location, owner_id, total_area, growing_rooms, max_capacity) VALUES 
('Demo Farm', 'Demonstration mushroom farm for testing', 'Lab Environment', 1, 100.0, 3, 500.0)
ON DUPLICATE KEY UPDATE name = name; 