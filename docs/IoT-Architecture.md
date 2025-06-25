# ShroomLab IoT Architecture - Phase 2

## Overview
This document outlines the IoT architecture for ShroomLab's mushroom farm monitoring and control system, specifically designed for the confirmed sensor inventory and hardware platforms.

## Hardware Platforms
- **ESP32 Microcontrollers**: Primary sensor nodes and relay controllers
- **Raspberry Pi 4B (Raspbian OS)**: Advanced processing nodes and IP camera hubs

## Confirmed IoT Device Inventory

### Environment Sensors
| Sensor Type | Purpose | Data Type | Units | Frequency |
|-------------|---------|-----------|-------|-----------|
| **Relative Humidity** | Moisture level monitoring | Float | % RH | 30s |
| **Temperature** | Ambient temperature | Float | °C | 30s |
| **Light Sensor** | PAR/Ambient light levels | Float | lux/µmol | 60s |
| **CO2 Sensor** | Air quality monitoring | Integer | ppm | 60s |
| **Air Pollution** | Air quality (PM2.5/PM10) | Float | µg/m³ | 300s |
| **Noise Sensor** | Sound level monitoring | Float | dB | 60s |
| **Airflow Sensor** | Ventilation monitoring | Float | m/s | 30s |
| **Weight Sensor** | Harvest/growth monitoring | Float | kg | 300s |
| **Liquid Flow** | Irrigation monitoring | Float | L/min | 60s |

### Visual Monitoring
- **IP Camera**: Real-time visual monitoring and time-lapse recording

### Control Systems
- **Relay Modules**: Automated control for irrigation, fans, lights, heaters, etc.

## MQTT Topic Structure

### Sensor Data Topics
```
sensors/{farm_id}/{device_id}/humidity/data
sensors/{farm_id}/{device_id}/temperature/data
sensors/{farm_id}/{device_id}/light/data
sensors/{farm_id}/{device_id}/co2/data
sensors/{farm_id}/{device_id}/pollution/data
sensors/{farm_id}/{device_id}/noise/data
sensors/{farm_id}/{device_id}/airflow/data
sensors/{farm_id}/{device_id}/weight/data
sensors/{farm_id}/{device_id}/liquidflow/data
```

### Control Topics
```
controls/{farm_id}/{device_id}/relay/{relay_number}/command
controls/{farm_id}/{device_id}/relay/{relay_number}/status
```

### Camera Topics
```
camera/{farm_id}/{camera_id}/stream/status
camera/{farm_id}/{camera_id}/snapshot/request
camera/{farm_id}/{camera_id}/recording/command
```

### System Topics
```
system/{farm_id}/alerts
system/{farm_id}/device/{device_id}/status
system/{farm_id}/device/{device_id}/heartbeat
```

## Data Models

### Sensor Reading Format
```json
{
  "device_id": "ESP32_001",
  "farm_id": "farm_01",
  "sensor_type": "humidity",
  "value": 65.5,
  "unit": "%RH",
  "timestamp": "2024-12-25T10:30:00Z",
  "location": "growing_room_1",
  "calibration_offset": 0.0,
  "quality_score": 1.0
}
```

### Relay Control Format
```json
{
  "device_id": "ESP32_002",
  "farm_id": "farm_01",
  "relay_number": 1,
  "command": "ON",
  "duration": 300,
  "scheduled_time": "2024-12-25T10:35:00Z",
  "priority": "manual"
}
```

### Camera Event Format
```json
{
  "camera_id": "RPI_CAM_001",
  "farm_id": "farm_01",
  "event_type": "motion_detected",
  "timestamp": "2024-12-25T10:30:00Z",
  "snapshot_url": "/snapshots/farm_01/2024-12-25_10-30-00.jpg",
  "confidence": 0.85
}
```

## Device Integration Examples

### ESP32 Sensor Node Code
```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// Sensor pins and types
#define DHT_PIN 4
#define DHT_TYPE DHT22
#define LIGHT_PIN A0
#define CO2_PIN A1
#define NOISE_PIN A2
#define AIRFLOW_PIN A3

DHT dht(DHT_PIN, DHT_TYPE);

// WiFi and MQTT configuration
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";
const char* mqtt_server = "192.168.1.100";  // ShroomLab server IP
const int mqtt_port = 1883;

WiFiClient espClient;
PubSubClient client(espClient);

String device_id = "ESP32_001";
String farm_id = "farm_01";

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  // Connect to MQTT
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(onMqttMessage);
}

void loop() {
  if (!client.connected()) {
    reconnectMqtt();
  }
  client.loop();
  
  // Read sensors every 30 seconds
  static unsigned long lastSensorRead = 0;
  if (millis() - lastSensorRead > 30000) {
    readAndPublishSensors();
    lastSensorRead = millis();
  }
  
  delay(100);
}

void readAndPublishSensors() {
  // Read humidity and temperature
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();
  
  if (!isnan(humidity)) {
    publishSensorData("humidity", humidity, "%RH");
  }
  
  if (!isnan(temperature)) {
    publishSensorData("temperature", temperature, "°C");
  }
  
  // Read light sensor
  int lightRaw = analogRead(LIGHT_PIN);
  float lightLux = map(lightRaw, 0, 4095, 0, 100000); // Convert to lux
  publishSensorData("light", lightLux, "lux");
  
  // Read CO2 (example for MQ-135 or similar)
  int co2Raw = analogRead(CO2_PIN);
  float co2ppm = map(co2Raw, 0, 4095, 300, 5000); // Convert to ppm
  publishSensorData("co2", co2ppm, "ppm");
  
  // Read noise level
  int noiseRaw = analogRead(NOISE_PIN);
  float noiseDb = map(noiseRaw, 0, 4095, 30, 120); // Convert to dB
  publishSensorData("noise", noiseDb, "dB");
  
  // Read airflow
  int airflowRaw = analogRead(AIRFLOW_PIN);
  float airflowMs = map(airflowRaw, 0, 4095, 0, 10); // Convert to m/s
  publishSensorData("airflow", airflowMs, "m/s");
}

void publishSensorData(String sensorType, float value, String unit) {
  StaticJsonDocument<200> doc;
  doc["device_id"] = device_id;
  doc["farm_id"] = farm_id;
  doc["sensor_type"] = sensorType;
  doc["value"] = value;
  doc["unit"] = unit;
  doc["timestamp"] = WiFi.getTime();
  doc["location"] = "growing_room_1";
  doc["quality_score"] = 1.0;
  
  String jsonString;
  serializeJson(doc, jsonString);
  
  String topic = "sensors/" + farm_id + "/" + device_id + "/" + sensorType + "/data";
  client.publish(topic.c_str(), jsonString.c_str());
  
  Serial.println("Published: " + topic + " -> " + jsonString);
}

void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  
  Serial.println("Received: " + String(topic) + " -> " + message);
  
  // Handle relay commands
  if (String(topic).indexOf("/relay/") > 0) {
    handleRelayCommand(message);
  }
}

void reconnectMqtt() {
  while (!client.connected()) {
    if (client.connect(device_id.c_str())) {
      // Subscribe to control topics
      String relayTopic = "controls/" + farm_id + "/" + device_id + "/relay/+/command";
      client.subscribe(relayTopic.c_str());
    } else {
      delay(5000);
    }
  }
}
```

### Raspberry Pi Camera Integration
```python
#!/usr/bin/env python3
import cv2
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime
import base64
import io
from PIL import Image

class CameraModule:
    def __init__(self, camera_id="RPI_CAM_001", farm_id="farm_01"):
        self.camera_id = camera_id
        self.farm_id = farm_id
        self.cap = cv2.VideoCapture(0)  # USB camera or Pi camera
        
        # MQTT setup
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.connect("192.168.1.100", 1883, 60)  # ShroomLab server
        
        self.recording = False
        
    def on_connect(self, client, userdata, flags, rc):
        print(f"Camera {self.camera_id} connected to MQTT")
        # Subscribe to camera commands
        command_topic = f"camera/{self.farm_id}/{self.camera_id}/+/command"
        client.subscribe(command_topic)
        
    def on_message(self, client, userdata, msg):
        topic_parts = msg.topic.split('/')
        command_type = topic_parts[-2]  # snapshot, recording, etc.
        command = msg.payload.decode()
        
        if command_type == "snapshot":
            self.take_snapshot()
        elif command_type == "recording":
            if command == "START":
                self.start_recording()
            elif command == "STOP":
                self.stop_recording()
                
    def take_snapshot(self):
        ret, frame = self.cap.read()
        if ret:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"/snapshots/{self.farm_id}/{timestamp}.jpg"
            cv2.imwrite(filename, frame)
            
            # Publish snapshot event
            event_data = {
                "camera_id": self.camera_id,
                "farm_id": self.farm_id,
                "event_type": "snapshot_taken",
                "timestamp": datetime.now().isoformat(),
                "snapshot_url": filename,
                "resolution": f"{frame.shape[1]}x{frame.shape[0]}"
            }
            
            topic = f"camera/{self.farm_id}/{self.camera_id}/snapshot/status"
            self.mqtt_client.publish(topic, json.dumps(event_data))
            
    def start_recording(self):
        self.recording = True
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.video_filename = f"/recordings/{self.farm_id}/{timestamp}.mp4"
        
        # Video writer setup
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.video_writer = cv2.VideoWriter(self.video_filename, fourcc, 20.0, (640, 480))
        
        print(f"Started recording: {self.video_filename}")
        
    def stop_recording(self):
        self.recording = False
        if hasattr(self, 'video_writer'):
            self.video_writer.release()
            
        # Publish recording event
        event_data = {
            "camera_id": self.camera_id,
            "farm_id": self.farm_id,
            "event_type": "recording_completed",
            "timestamp": datetime.now().isoformat(),
            "video_url": self.video_filename
        }
        
        topic = f"camera/{self.farm_id}/{self.camera_id}/recording/status"
        self.mqtt_client.publish(topic, json.dumps(event_data))
        
    def run(self):
        while True:
            self.mqtt_client.loop_start()
            
            ret, frame = self.cap.read()
            if ret:
                # Process frame for motion detection, etc.
                if self.recording and hasattr(self, 'video_writer'):
                    self.video_writer.write(frame)
                    
                # Send periodic heartbeat
                heartbeat = {
                    "camera_id": self.camera_id,
                    "farm_id": self.farm_id,
                    "status": "online",
                    "timestamp": datetime.now().isoformat()
                }
                
                topic = f"system/{self.farm_id}/device/{self.camera_id}/heartbeat"
                self.mqtt_client.publish(topic, json.dumps(heartbeat))
                
            time.sleep(0.1)

if __name__ == "__main__":
    camera = CameraModule()
    camera.run()
```

## Database Schema Updates

### Sensor Types Table
```sql
CREATE TABLE sensor_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    unit VARCHAR(20) NOT NULL,
    min_value DECIMAL(10,3),
    max_value DECIMAL(10,3),
    optimal_min DECIMAL(10,3),
    optimal_max DECIMAL(10,3),
    reading_frequency INT DEFAULT 30,
    description TEXT
);

-- Insert sensor types
INSERT INTO sensor_types (type_name, unit, min_value, max_value, optimal_min, optimal_max, reading_frequency) VALUES
('humidity', '%RH', 0, 100, 55, 75, 30),
('temperature', '°C', -40, 85, 18, 24, 30),
('light', 'lux', 0, 100000, 200, 800, 60),
('co2', 'ppm', 300, 5000, 400, 1000, 60),
('pollution', 'µg/m³', 0, 500, 0, 35, 300),
('noise', 'dB', 0, 120, 0, 50, 60),
('airflow', 'm/s', 0, 20, 0.1, 2.0, 30),
('weight', 'kg', 0, 1000, NULL, NULL, 300),
('liquidflow', 'L/min', 0, 100, NULL, NULL, 60);
```

### Device Types Table
```sql
CREATE TABLE device_types (
    id INT PRIMARY KEY AUTO_INCREMENT,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    category ENUM('sensor', 'control', 'camera') NOT NULL,
    description TEXT,
    supported_sensors TEXT -- JSON array of sensor types
);

INSERT INTO device_types (type_name, category, supported_sensors) VALUES
('ESP32_Multi_Sensor', 'sensor', '["humidity", "temperature", "light", "co2", "noise", "airflow"]'),
('ESP32_Relay_Controller', 'control', '[]'),
('Load_Cell_Scale', 'sensor', '["weight"]'),
('Flow_Meter', 'sensor', '["liquidflow"]'),
('Air_Quality_Monitor', 'sensor', '["pollution"]'),
('IP_Camera', 'camera', '[]');
```

## API Endpoints for IoT Integration

### Sensor Data Endpoints
- `POST /api/v1/sensors/data` - Bulk sensor data ingestion
- `GET /api/v1/sensors/{farm_id}/latest` - Latest readings by farm
- `GET /api/v1/sensors/{farm_id}/{sensor_type}` - Historical data
- `POST /api/v1/sensors/calibrate/{device_id}` - Calibration settings

### Device Management Endpoints  
- `POST /api/v1/devices/register` - Register new device
- `GET /api/v1/devices/{farm_id}` - List farm devices
- `PUT /api/v1/devices/{device_id}/status` - Update device status
- `POST /api/v1/devices/{device_id}/command` - Send control commands

### Camera Endpoints
- `GET /api/v1/cameras/{farm_id}/stream` - Live stream access
- `POST /api/v1/cameras/{camera_id}/snapshot` - Request snapshot
- `GET /api/v1/cameras/{farm_id}/recordings` - List recordings
- `POST /api/v1/cameras/{camera_id}/recording/start` - Start recording

### Relay Control Endpoints
- `POST /api/v1/controls/relay/{device_id}/{relay_number}` - Control relay
- `GET /api/v1/controls/{farm_id}/status` - Get all control statuses
- `POST /api/v1/controls/schedule` - Schedule automated actions

## Implementation Priority

### Phase 2.1: Core Sensors (Week 1)
1. ✅ Temperature & Humidity (DHT22/SHT30)
2. ✅ Light sensor integration
3. ✅ Basic MQTT communication
4. ✅ Database storage setup

### Phase 2.2: Advanced Sensors (Week 2)  
1. ⏳ CO2 sensor integration
2. ⏳ Air quality/pollution monitoring
3. ⏳ Noise level monitoring
4. ⏳ Airflow sensor setup

### Phase 2.3: Specialized Sensors (Week 3)
1. ⏳ Weight sensor/load cell integration
2. ⏳ Liquid flow sensor setup
3. ⏳ Sensor calibration system
4. ⏳ Data validation and quality checks

### Phase 2.4: Control & Visual (Week 4)
1. ⏳ Relay control implementation
2. ⏳ IP camera integration
3. ⏳ Real-time dashboard updates
4. ⏳ Mobile-responsive interface

## Security Considerations
- MQTT authentication and encryption
- Device certificate management
- Network segmentation for IoT devices
- Regular security updates for ESP32/Pi firmware
- Camera stream encryption and access control

## Monitoring & Maintenance
- Device heartbeat monitoring
- Sensor drift detection and alerts
- Automatic calibration reminders
- Battery level monitoring (for wireless sensors)
- Network connectivity monitoring

This architecture provides a robust, scalable foundation for your ESP32 and Raspberry Pi devices in the mushroom farm IoT ecosystem! 