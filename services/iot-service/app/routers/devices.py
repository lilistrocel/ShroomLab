from fastapi import APIRouter, HTTPException
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Device models
class DeviceRegistration(BaseModel):
    device_id: str = Field(..., description="Unique device identifier")
    farm_id: str = Field(..., description="Farm identifier")
    device_type: str = Field(..., description="Type of device (ESP32_Multi_Sensor, ESP32_Relay_Controller, etc.)")
    hardware_platform: str = Field(..., description="Hardware platform (ESP32, Raspberry_Pi)")
    location: Optional[str] = Field(None, description="Physical location description")
    supported_sensors: List[str] = Field(default=[], description="List of sensor types this device supports")
    relay_count: Optional[int] = Field(None, description="Number of relays for control devices")
    firmware_version: Optional[str] = Field(None, description="Device firmware version")
    ip_address: Optional[str] = Field(None, description="Device IP address")

class DeviceStatus(BaseModel):
    device_id: str
    status: str = Field(..., description="online, offline, error, maintenance")
    last_seen: datetime = Field(default_factory=datetime.now)
    battery_level: Optional[float] = Field(None, description="Battery percentage (if applicable)")
    signal_strength: Optional[float] = Field(None, description="WiFi signal strength (dBm)")
    uptime: Optional[int] = Field(None, description="Device uptime in seconds")
    memory_usage: Optional[float] = Field(None, description="Memory usage percentage")
    cpu_temperature: Optional[float] = Field(None, description="CPU temperature (°C)")

class RelayCommand(BaseModel):
    device_id: str = Field(..., description="Target device ID")
    relay_number: int = Field(..., description="Relay number (1-based)")
    command: str = Field(..., description="ON, OFF, TOGGLE, PULSE")
    duration: Optional[int] = Field(None, description="Duration in seconds (for PULSE or timed operations)")
    scheduled_time: Optional[datetime] = Field(None, description="Schedule command for future execution")
    priority: str = Field("normal", description="manual, scheduled, automatic, emergency")

class CameraCommand(BaseModel):
    camera_id: str = Field(..., description="Camera device ID")
    command_type: str = Field(..., description="snapshot, recording, stream")
    action: str = Field(..., description="start, stop, request")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Additional parameters")

# Device type specifications
DEVICE_TYPES = {
    "ESP32_Multi_Sensor": {
        "category": "sensor",
        "supported_sensors": ["humidity", "temperature", "light", "co2", "noise", "airflow"],
        "relay_count": 0,
        "description": "ESP32 with multiple environmental sensors"
    },
    "ESP32_Relay_Controller": {
        "category": "control",
        "supported_sensors": [],
        "relay_count": 8,
        "description": "ESP32 with relay module for automation control"
    },
    "Load_Cell_Scale": {
        "category": "sensor",
        "supported_sensors": ["weight"],
        "relay_count": 0,
        "description": "Load cell scale for harvest monitoring"
    },
    "Flow_Meter": {
        "category": "sensor",
        "supported_sensors": ["liquidflow"],
        "relay_count": 0,
        "description": "Flow meter for irrigation monitoring"
    },
    "Air_Quality_Monitor": {
        "category": "sensor",
        "supported_sensors": ["pollution"],
        "relay_count": 0,
        "description": "Air quality sensor for PM2.5/PM10 monitoring"
    },
    "IP_Camera": {
        "category": "camera",
        "supported_sensors": [],
        "relay_count": 0,
        "description": "IP camera for visual monitoring"
    }
}

@router.get("/")
async def list_device_endpoints():
    """List all available device management endpoints"""
    return {
        "endpoints": {
            "POST /register": "Register new device",
            "GET /types": "List supported device types",
            "GET /{farm_id}": "List devices by farm",
            "GET /{farm_id}/{device_id}": "Get device details",
            "PUT /{device_id}/status": "Update device status",
            "POST /{device_id}/command": "Send command to device",
            "POST /relay/command": "Control relay",
            "POST /camera/command": "Control camera",
            "GET /health": "Service health check"
        },
        "supported_device_types": list(DEVICE_TYPES.keys())
    }

@router.get("/types")
async def get_device_types():
    """Get all supported device types and their specifications"""
    return {"device_types": DEVICE_TYPES}

@router.get("/types/{device_type}")
async def get_device_type_spec(device_type: str):
    """Get specification for a specific device type"""
    if device_type not in DEVICE_TYPES:
        raise HTTPException(status_code=404, detail=f"Device type '{device_type}' not found")
    
    return {"device_type": DEVICE_TYPES[device_type]}

@router.post("/register")
async def register_device(device: DeviceRegistration):
    """Register a new IoT device"""
    try:
        # Validate device type
        if device.device_type not in DEVICE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown device type: {device.device_type}"
            )
        
        device_spec = DEVICE_TYPES[device.device_type]
        
        # Validate supported sensors
        if device.supported_sensors:
            for sensor in device.supported_sensors:
                if sensor not in device_spec["supported_sensors"]:
                    logger.warning(
                        f"Sensor {sensor} not typically supported by {device.device_type}"
                    )
        
        # TODO: Store device registration in MySQL
        # TODO: Send device configuration via MQTT
        # TODO: Initialize device monitoring
        
        logger.info(f"Registered device {device.device_id} of type {device.device_type}")
        
        return {
            "status": "success",
            "message": "Device registered successfully",
            "device_id": device.device_id,
            "assigned_farm": device.farm_id,
            "device_spec": device_spec,
            "registration_time": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error registering device: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error registering device: {str(e)}")

@router.get("/{farm_id}")
async def list_farm_devices(farm_id: str, device_type: Optional[str] = None):
    """List all devices for a specific farm"""
    # TODO: Query MySQL for farm devices
    # TODO: Apply optional device_type filter
    
    return {
        "message": f"Devices for farm {farm_id}",
        "farm_id": farm_id,
        "device_type_filter": device_type,
        "note": "Database integration coming soon"
    }

@router.get("/{farm_id}/{device_id}")
async def get_device_details(farm_id: str, device_id: str):
    """Get detailed information about a specific device"""
    # TODO: Query MySQL for device details
    # TODO: Get latest status from device heartbeat
    
    return {
        "message": f"Details for device {device_id} in farm {farm_id}",
        "farm_id": farm_id,
        "device_id": device_id,
        "note": "Database integration coming soon"
    }

@router.put("/{device_id}/status")
async def update_device_status(device_id: str, status: DeviceStatus):
    """Update device status (typically called by devices themselves)"""
    try:
        # TODO: Update device status in MySQL
        # TODO: Check for alerts (low battery, offline, etc.)
        # TODO: Update real-time dashboard via WebSocket
        
        logger.info(
            f"Device {device_id} status updated: {status.status} "
            f"(last seen: {status.last_seen})"
        )
        
        return {
            "status": "success",
            "message": "Device status updated",
            "device_id": device_id,
            "current_status": status.status,
            "updated_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error updating device status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error updating device status: {str(e)}")

@router.post("/{device_id}/command")
async def send_device_command(device_id: str, command: Dict[str, Any]):
    """Send generic command to device"""
    try:
        # TODO: Validate device exists and is online
        # TODO: Send command via MQTT
        # TODO: Log command for audit trail
        
        logger.info(f"Sending command to device {device_id}: {command}")
        
        return {
            "status": "success",
            "message": "Command sent to device",
            "device_id": device_id,
            "command": command,
            "sent_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error sending device command: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error sending device command: {str(e)}")

@router.post("/relay/command")
async def control_relay(relay_cmd: RelayCommand):
    """Control relay on ESP32 or other relay controller"""
    try:
        # Validate command
        valid_commands = ["ON", "OFF", "TOGGLE", "PULSE"]
        if relay_cmd.command not in valid_commands:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid relay command. Must be one of: {valid_commands}"
            )
        
        # Validate relay number (1-8 for typical ESP32 relay modules)
        if not 1 <= relay_cmd.relay_number <= 8:
            raise HTTPException(
                status_code=400,
                detail="Relay number must be between 1 and 8"
            )
        
        # TODO: Validate device exists and is a relay controller
        # TODO: Send relay command via MQTT
        # TODO: Store command in database for audit
        # TODO: Update relay status tracking
        
        logger.info(
            f"Relay command: {relay_cmd.command} relay {relay_cmd.relay_number} "
            f"on device {relay_cmd.device_id}"
        )
        
        return {
            "status": "success",
            "message": "Relay command sent",
            "device_id": relay_cmd.device_id,
            "relay_number": relay_cmd.relay_number,
            "command": relay_cmd.command,
            "duration": relay_cmd.duration,
            "priority": relay_cmd.priority,
            "sent_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error controlling relay: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error controlling relay: {str(e)}")

@router.post("/camera/command")
async def control_camera(camera_cmd: CameraCommand):
    """Control IP camera (snapshot, recording, streaming)"""
    try:
        # Validate command type and action combinations
        valid_combinations = {
            "snapshot": ["request"],
            "recording": ["start", "stop"],
            "stream": ["start", "stop"]
        }
        
        if camera_cmd.command_type not in valid_combinations:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid command type. Must be one of: {list(valid_combinations.keys())}"
            )
        
        if camera_cmd.action not in valid_combinations[camera_cmd.command_type]:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid action '{camera_cmd.action}' for command type '{camera_cmd.command_type}'"
            )
        
        # TODO: Validate camera device exists and is online
        # TODO: Send camera command via MQTT
        # TODO: Handle camera response and file storage
        
        logger.info(
            f"Camera command: {camera_cmd.command_type} {camera_cmd.action} "
            f"for camera {camera_cmd.camera_id}"
        )
        
        return {
            "status": "success",
            "message": "Camera command sent",
            "camera_id": camera_cmd.camera_id,
            "command_type": camera_cmd.command_type,
            "action": camera_cmd.action,
            "parameters": camera_cmd.parameters,
            "sent_at": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error controlling camera: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error controlling camera: {str(e)}")

@router.get("/{farm_id}/status")
async def get_farm_device_status(farm_id: str):
    """Get status summary for all devices in a farm"""
    # TODO: Query device statuses from MySQL
    # TODO: Aggregate status information
    # TODO: Identify offline or problematic devices
    
    return {
        "message": f"Device status summary for farm {farm_id}",
        "farm_id": farm_id,
        "note": "Database integration coming soon"
    }

@router.get("/health")
async def device_health():
    """Health check for device management service"""
    return {
        "status": "healthy",
        "service": "devices",
        "supported_device_types": len(DEVICE_TYPES),
        "timestamp": datetime.now()
    } 