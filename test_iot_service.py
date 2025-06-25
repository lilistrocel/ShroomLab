#!/usr/bin/env python3
"""
Test script for ShroomLab IoT Service
Tests the new sensor data ingestion and device management endpoints
"""
import requests
import json
from datetime import datetime

# IoT Service base URL
BASE_URL = "http://localhost:8001/api/v1"

def test_sensor_types():
    """Test sensor types endpoint"""
    print("🧪 Testing Sensor Types Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/sensors/types")
        if response.status_code == 200:
            data = response.json()
            sensor_types = data.get("sensor_types", {})
            print(f"✅ Found {len(sensor_types)} supported sensor types:")
            for sensor_type, spec in sensor_types.items():
                print(f"   - {sensor_type}: {spec['unit']} ({spec['description']})")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_device_types():
    """Test device types endpoint"""
    print("\n🧪 Testing Device Types Endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/devices/types")
        if response.status_code == 200:
            data = response.json()
            device_types = data.get("device_types", {})
            print(f"✅ Found {len(device_types)} supported device types:")
            for device_type, spec in device_types.items():
                print(f"   - {device_type}: {spec['description']}")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sensor_data_ingestion():
    """Test sensor data ingestion"""
    print("\n🧪 Testing Sensor Data Ingestion...")
    
    # Test data for all your sensor types
    test_readings = [
        {
            "device_id": "ESP32_001",
            "farm_id": "farm_01",
            "sensor_type": "humidity",
            "value": 65.5,
            "unit": "%RH",
            "location": "growing_room_1"
        },
        {
            "device_id": "ESP32_001",
            "farm_id": "farm_01",
            "sensor_type": "temperature",
            "value": 22.3,
            "unit": "°C",
            "location": "growing_room_1"
        },
        {
            "device_id": "ESP32_002",
            "farm_id": "farm_01",
            "sensor_type": "co2",
            "value": 850,
            "unit": "ppm",
            "location": "growing_room_2"
        },
        {
            "device_id": "ESP32_003",
            "farm_id": "farm_01",
            "sensor_type": "light",
            "value": 450,
            "unit": "lux",
            "location": "growing_room_1"
        },
        {
            "device_id": "SCALE_001",
            "farm_id": "farm_01",
            "sensor_type": "weight",
            "value": 12.5,
            "unit": "kg",
            "location": "harvest_station"
        }
    ]
    
    success_count = 0
    for reading in test_readings:
        try:
            response = requests.post(f"{BASE_URL}/sensors/data", json=reading)
            if response.status_code == 200:
                print(f"✅ {reading['sensor_type']}: {reading['value']} {reading['unit']}")
                success_count += 1
            else:
                print(f"❌ {reading['sensor_type']}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {reading['sensor_type']}: {e}")
    
    print(f"📊 Sensor ingestion: {success_count}/{len(test_readings)} successful")
    return success_count == len(test_readings)

def test_relay_control():
    """Test relay control"""
    print("\n🧪 Testing Relay Control...")
    
    relay_command = {
        "device_id": "ESP32_RELAY_001",
        "relay_number": 1,
        "command": "ON",
        "duration": 30,
        "priority": "manual"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/devices/relay/command", json=relay_command)
        if response.status_code == 200:
            print("✅ Relay control command sent successfully")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_camera_control():
    """Test camera control"""
    print("\n🧪 Testing Camera Control...")
    
    camera_command = {
        "camera_id": "RPI_CAM_001",
        "command_type": "snapshot",
        "action": "request",
        "parameters": {"resolution": "1920x1080"}
    }
    
    try:
        response = requests.post(f"{BASE_URL}/devices/camera/command", json=camera_command)
        if response.status_code == 200:
            print("✅ Camera control command sent successfully")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_device_registration():
    """Test device registration"""
    print("\n🧪 Testing Device Registration...")
    
    device = {
        "device_id": "ESP32_TEST_001",
        "farm_id": "farm_01",
        "device_type": "ESP32_Multi_Sensor",
        "hardware_platform": "ESP32",
        "location": "test_room",
        "supported_sensors": ["humidity", "temperature", "light"],
        "firmware_version": "1.0.0",
        "ip_address": "192.168.1.100"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/devices/register", json=device)
        if response.status_code == 200:
            print("✅ Device registration successful")
            return True
        else:
            print(f"❌ Failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("🍄 ShroomLab IoT Service Test Suite")
    print("=" * 50)
    
    tests = [
        test_sensor_types,
        test_device_types,
        test_sensor_data_ingestion,
        test_relay_control,
        test_camera_control,
        test_device_registration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📋 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your IoT service is ready for sensor integration.")
    else:
        print("⚠️  Some tests failed. Check the service logs for details.")
    
    print("\n🔗 Available endpoints:")
    print("   • Sensor API: http://localhost:8001/docs#/Sensors")
    print("   • Device API: http://localhost:8001/docs#/Devices")
    print("   • Service Health: http://localhost:8001/health")

if __name__ == "__main__":
    main() 