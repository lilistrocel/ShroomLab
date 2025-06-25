# ShroomLab IoT Architecture - Phase 2

## Overview
Modular IoT system for mushroom farm management using ESP32 and Raspberry Pi 4B devices.

## Hardware Platforms

### ESP32 Microcontrollers
- **Use Cases**: Sensors, simple controls, battery-powered devices
- **Advantages**: Low power, Wi-Fi/Bluetooth, cost-effective
- **Typical Applications**:
  - Temperature/humidity sensors
  - Soil moisture sensors
  - Light sensors
  - Simple relay controls

### Raspberry Pi 4B (Raspbian)
- **Use Cases**: Complex controls, data processing, camera systems
- **Advantages**: Full Linux OS, multiple I/O options, processing power
- **Typical Applications**:
  - Environmental control systems
  - Camera monitoring
  - Complex automation logic
  - Local data processing/edge computing

## Device Categories

### 1. Sensors 📊
**Environmental Monitoring Devices**

#### Sensor Types:
- **Temperature Sensors** (DS18B20, DHT22)
- **Humidity Sensors** (DHT22, SHT30)
- **CO2 Sensors** (MH-Z19, SCD30)
- **pH Sensors** (Atlas Scientific pH probe)
- **Light Sensors** (BH1750, TSL2561)
- **Soil Moisture** (Capacitive sensors)
- **Air Quality** (BME680)
- **Water Level** (Ultrasonic, float switches)

#### Data Flow:
```
Sensor → ESP32/RPi → MQTT → IoT Service → InfluxDB
                          ↓
                     WebSocket → Frontend Dashboard
```

### 2. Controls 🎛️
**Automated System Controllers**

#### Control Types:
- **Irrigation Systems** (pumps, valves, timers)
- **Ventilation** (fans, air circulation)
- **Lighting** (LED strips, grow lights)
- **Heating/Cooling** (heaters, coolers, thermostats)
- **Misting Systems** (humidity control)
- **Air Filtration** (HEPA filters, UV sterilization)

#### Control Flow:
```
Dashboard/Schedule → API Gateway → IoT Service → MQTT → ESP32/RPi → Actuator
                                                     ↓
                               Status Feedback → InfluxDB
```

## MQTT Topic Structure

### Sensor Topics (Publishing)
```
sensors/{farm_id}/{device_id}/{sensor_type}/data
sensors/{farm_id}/{device_id}/status
sensors/{farm_id}/{device_id}/heartbeat
```

**Examples:**
```
sensors/farm1/esp32_001/temperature/data
sensors/farm1/esp32_001/humidity/data
sensors/farm1/rpi_001/co2/data
sensors/farm1/esp32_002/status
```

### Control Topics (Commands & Status)
```
controls/{farm_id}/{device_id}/command
controls/{farm_id}/{device_id}/status
controls/{farm_id}/{device_id}/feedback
```

**Examples:**
```
controls/farm1/rpi_irrigation_001/command
controls/farm1/esp32_relay_001/status
controls/farm1/rpi_hvac_001/feedback
```

### System Topics
```
system/{farm_id}/alerts
system/{farm_id}/maintenance
system/global/broadcast
```

## Device Registration & Management

### Device Registration Process
1. **Physical Setup**: Connect device to network
2. **Auto-Discovery**: Device broadcasts discovery message
3. **Registration**: Device registers with ShroomLab system
4. **Configuration**: System assigns farm, location, and parameters
5. **Activation**: Device begins normal operation

### Device Metadata
```json
{
  "device_id": "esp32_temp_001",
  "device_type": "sensor",
  "hardware": "ESP32",
  "farm_id": 1,
  "location": "Growing Room A",
  "sensor_types": ["temperature", "humidity"],
  "firmware_version": "1.2.3",
  "last_seen": "2024-12-25T10:30:00Z",
  "status": "online",
  "battery_level": 85
}
```

## Data Payloads

### Sensor Data Payload
```json
{
  "device_id": "esp32_temp_001",
  "timestamp": "2024-12-25T10:30:15Z",
  "farm_id": 1,
  "location": "Room A",
  "readings": {
    "temperature": {
      "value": 22.5,
      "unit": "°C"
    },
    "humidity": {
      "value": 65.3,
      "unit": "%"
    }
  },
  "battery": 87,
  "signal_strength": -45
}
```

### Control Command Payload
```json
{
  "command_id": "cmd_001",
  "device_id": "rpi_irrigation_001",
  "timestamp": "2024-12-25T10:30:00Z",
  "action": "start_irrigation",
  "parameters": {
    "duration": 300,
    "zone": "A1",
    "flow_rate": 2.5
  },
  "priority": "normal"
}
```

### Control Status Payload
```json
{
  "device_id": "rpi_irrigation_001",
  "timestamp": "2024-12-25T10:30:20Z",
  "status": "running",
  "current_action": "irrigation",
  "parameters": {
    "zone": "A1",
    "remaining_time": 285,
    "flow_rate": 2.5
  },
  "system_health": "good"
}
```

## API Endpoints

### Sensor Management
```
GET    /api/v1/devices/sensors              # List all sensors
POST   /api/v1/devices/sensors              # Register new sensor
GET    /api/v1/devices/sensors/{device_id}  # Get sensor details
PUT    /api/v1/devices/sensors/{device_id}  # Update sensor config
DELETE /api/v1/devices/sensors/{device_id}  # Remove sensor

GET    /api/v1/sensors/data/{device_id}     # Get sensor data
GET    /api/v1/sensors/data/farm/{farm_id}  # Get farm sensor data
```

### Control Management
```
GET    /api/v1/devices/controls              # List all controls
POST   /api/v1/devices/controls              # Register new control
GET    /api/v1/devices/controls/{device_id}  # Get control details
PUT    /api/v1/devices/controls/{device_id}  # Update control config
DELETE /api/v1/devices/controls/{device_id}  # Remove control

POST   /api/v1/controls/command/{device_id}  # Send command
GET    /api/v1/controls/status/{device_id}   # Get status
GET    /api/v1/controls/schedule/{device_id} # Get schedule
POST   /api/v1/controls/schedule/{device_id} # Set schedule
```

## Security Considerations

### MQTT Security
- **Authentication**: Username/password for device connections
- **Authorization**: Topic-based access control
- **Encryption**: TLS/SSL for MQTT connections
- **Certificate Management**: Device certificates for authentication

### Device Security
- **Firmware Updates**: OTA (Over-The-Air) updates
- **Access Control**: Role-based device permissions
- **Network Security**: WPA2/WPA3 Wi-Fi encryption
- **Data Validation**: Input sanitization and validation

## Implementation Phases

### Phase 2.1: Sensor Infrastructure
1. Design sensor registration API
2. Implement MQTT sensor data ingestion
3. Create InfluxDB time-series storage
4. Build real-time dashboard updates

### Phase 2.2: Control Infrastructure
1. Design control command API
2. Implement MQTT control messaging
3. Create scheduling system
4. Build control status monitoring

### Phase 2.3: Device Management
1. Device discovery and registration
2. Health monitoring and alerts
3. Firmware update system
4. Device configuration management

## Example Device Code

### ESP32 Sensor Example (Arduino)
```cpp
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>
#include <ArduinoJson.h>

// Device configuration
const char* DEVICE_ID = "esp32_temp_001";
const char* FARM_ID = "farm1";
const char* MQTT_TOPIC = "sensors/farm1/esp32_temp_001/data";

// Initialize sensor and MQTT
DHT dht(2, DHT22);
WiFiClient espClient;
PubSubClient client(espClient);

void sendSensorData() {
  StaticJsonDocument<200> doc;
  doc["device_id"] = DEVICE_ID;
  doc["timestamp"] = getTimestamp();
  doc["farm_id"] = FARM_ID;
  
  JsonObject readings = doc.createNestedObject("readings");
  readings["temperature"]["value"] = dht.readTemperature();
  readings["temperature"]["unit"] = "°C";
  readings["humidity"]["value"] = dht.readHumidity();
  readings["humidity"]["unit"] = "%";
  
  char buffer[256];
  serializeJson(doc, buffer);
  client.publish(MQTT_TOPIC, buffer);
}
```

### Raspberry Pi Control Example (Python)
```python
import paho.mqtt.client as mqtt
import json
import time
import RPi.GPIO as GPIO

DEVICE_ID = "rpi_irrigation_001"
FARM_ID = "farm1"
MQTT_BROKER = "shroomlab-mqtt"
COMMAND_TOPIC = f"controls/{FARM_ID}/{DEVICE_ID}/command"
STATUS_TOPIC = f"controls/{FARM_ID}/{DEVICE_ID}/status"

class IrrigationController:
    def __init__(self):
        self.client = mqtt.Client()
        self.client.on_message = self.on_message
        self.client.connect(MQTT_BROKER, 1883, 60)
        self.client.subscribe(COMMAND_TOPIC)
        
    def on_message(self, client, userdata, msg):
        command = json.loads(msg.payload.decode())
        if command['action'] == 'start_irrigation':
            self.start_irrigation(command['parameters'])
        elif command['action'] == 'stop_irrigation':
            self.stop_irrigation()
            
    def start_irrigation(self, params):
        # Control irrigation valve
        GPIO.output(18, GPIO.HIGH)
        self.send_status("running", params)
        
    def send_status(self, status, params=None):
        payload = {
            "device_id": DEVICE_ID,
            "timestamp": int(time.time()),
            "status": status,
            "parameters": params or {}
        }
        self.client.publish(STATUS_TOPIC, json.dumps(payload))
```

This architecture provides a robust, scalable foundation for your ESP32 and Raspberry Pi devices in the mushroom farm IoT ecosystem! 