from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# Sensor data models
class SensorReading(BaseModel):
    device_id: str = Field(..., description="Device identifier (e.g., ESP32_001)")
    farm_id: str = Field(..., description="Farm identifier")
    sensor_type: str = Field(..., description="Type of sensor")
    value: float = Field(..., description="Sensor reading value")
    unit: str = Field(..., description="Unit of measurement")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)
    location: Optional[str] = Field(None, description="Physical location description")
    calibration_offset: Optional[float] = Field(0.0, description="Calibration offset applied")
    quality_score: Optional[float] = Field(1.0, description="Data quality score (0-1)")

class BulkSensorData(BaseModel):
    readings: List[SensorReading]

class SensorType(BaseModel):
    type_name: str
    unit: str
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    optimal_min: Optional[float] = None
    optimal_max: Optional[float] = None
    reading_frequency: int = 30  # seconds
    description: Optional[str] = None

# Supported sensor types with their specifications
SENSOR_TYPES = {
    "humidity": SensorType(
        type_name="humidity",
        unit="%RH", 
        min_value=0, 
        max_value=100, 
        optimal_min=55, 
        optimal_max=75,
        reading_frequency=30,
        description="Relative humidity sensor"
    ),
    "temperature": SensorType(
        type_name="temperature",
        unit="°C",
        min_value=-40,
        max_value=85,
        optimal_min=18,
        optimal_max=24,
        reading_frequency=30,
        description="Temperature sensor"
    ),
    "light": SensorType(
        type_name="light",
        unit="lux",
        min_value=0,
        max_value=100000,
        optimal_min=200,
        optimal_max=800,
        reading_frequency=60,
        description="Light intensity sensor"
    ),
    "co2": SensorType(
        type_name="co2",
        unit="ppm",
        min_value=300,
        max_value=5000,
        optimal_min=400,
        optimal_max=1000,
        reading_frequency=60,
        description="CO2 concentration sensor"
    ),
    "pollution": SensorType(
        type_name="pollution",
        unit="µg/m³",
        min_value=0,
        max_value=500,
        optimal_min=0,
        optimal_max=35,
        reading_frequency=300,
        description="Air pollution sensor (PM2.5/PM10)"
    ),
    "noise": SensorType(
        type_name="noise",
        unit="dB",
        min_value=0,
        max_value=120,
        optimal_min=0,
        optimal_max=50,
        reading_frequency=60,
        description="Noise level sensor"
    ),
    "airflow": SensorType(
        type_name="airflow",
        unit="m/s",
        min_value=0,
        max_value=20,
        optimal_min=0.1,
        optimal_max=2.0,
        reading_frequency=30,
        description="Airflow velocity sensor"
    ),
    "weight": SensorType(
        type_name="weight",
        unit="kg",
        min_value=0,
        max_value=1000,
        reading_frequency=300,
        description="Weight/load cell sensor for harvest monitoring"
    ),
    "liquidflow": SensorType(
        type_name="liquidflow",
        unit="L/min",
        min_value=0,
        max_value=100,
        reading_frequency=60,
        description="Liquid flow rate sensor for irrigation monitoring"
    )
}

def validate_sensor_reading(reading: SensorReading) -> bool:
    """Validate sensor reading against known sensor types and ranges"""
    if reading.sensor_type not in SENSOR_TYPES:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown sensor type: {reading.sensor_type}"
        )
    
    sensor_spec = SENSOR_TYPES[reading.sensor_type]
    
    # Check unit consistency
    if reading.unit != sensor_spec.unit:
        logger.warning(
            f"Unit mismatch for {reading.sensor_type}: "
            f"expected {sensor_spec.unit}, got {reading.unit}"
        )
    
    # Check value ranges
    if sensor_spec.min_value is not None and reading.value < sensor_spec.min_value:
        logger.warning(
            f"Reading below minimum for {reading.sensor_type}: "
            f"{reading.value} < {sensor_spec.min_value}"
        )
        
    if sensor_spec.max_value is not None and reading.value > sensor_spec.max_value:
        logger.warning(
            f"Reading above maximum for {reading.sensor_type}: "
            f"{reading.value} > {sensor_spec.max_value}"
        )
    
    return True

@router.get("/")
async def list_sensor_endpoints():
    """List all available sensor endpoints"""
    return {
        "endpoints": {
            "POST /data": "Ingest sensor data (single reading)",
            "POST /bulk": "Ingest bulk sensor data (multiple readings)",
            "GET /types": "List supported sensor types",
            "GET /{farm_id}/latest": "Get latest readings by farm",
            "GET /{farm_id}/{sensor_type}": "Get historical data for sensor type",
            "POST /calibrate/{device_id}": "Set calibration for device"
        },
        "supported_sensors": list(SENSOR_TYPES.keys())
    }

@router.get("/types")
async def get_sensor_types():
    """Get all supported sensor types and their specifications"""
    return {"sensor_types": SENSOR_TYPES}

@router.get("/types/{sensor_type}")
async def get_sensor_type_spec(sensor_type: str):
    """Get specification for a specific sensor type"""
    if sensor_type not in SENSOR_TYPES:
        raise HTTPException(status_code=404, detail=f"Sensor type '{sensor_type}' not found")
    
    return {"sensor_type": SENSOR_TYPES[sensor_type]}

@router.post("/data")
async def receive_sensor_data(reading: SensorReading):
    """Receive single sensor reading from IoT device"""
    try:
        # Validate the reading
        validate_sensor_reading(reading)
        
        # TODO: Store in InfluxDB for time-series data
        # TODO: Store metadata in MySQL
        # TODO: Publish to MQTT for real-time updates
        # TODO: Check for alerts/thresholds
        
        logger.info(
            f"Received {reading.sensor_type} reading from {reading.device_id}: "
            f"{reading.value} {reading.unit}"
        )
        
        return {
            "status": "success",
            "message": "Sensor data received successfully",
            "reading_id": f"{reading.device_id}_{reading.sensor_type}_{int(reading.timestamp.timestamp())}",
            "timestamp": reading.timestamp
        }
        
    except Exception as e:
        logger.error(f"Error processing sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing sensor data: {str(e)}")

@router.post("/bulk")
async def receive_bulk_sensor_data(bulk_data: BulkSensorData):
    """Receive multiple sensor readings in bulk"""
    try:
        processed_readings = []
        failed_readings = []
        
        for reading in bulk_data.readings:
            try:
                validate_sensor_reading(reading)
                processed_readings.append(reading)
                
                logger.info(
                    f"Processed {reading.sensor_type} from {reading.device_id}: "
                    f"{reading.value} {reading.unit}"
                )
                
            except Exception as e:
                failed_readings.append({
                    "reading": reading.dict(),
                    "error": str(e)
                })
                logger.error(f"Failed to process reading: {str(e)}")
        
        # TODO: Batch insert to InfluxDB
        # TODO: Batch insert metadata to MySQL
        # TODO: Publish batch updates via MQTT
        
        return {
            "status": "success",
            "processed_count": len(processed_readings),
            "failed_count": len(failed_readings),
            "failed_readings": failed_readings,
            "timestamp": datetime.now()
        }
        
    except Exception as e:
        logger.error(f"Error processing bulk sensor data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing bulk data: {str(e)}")

@router.get("/{farm_id}/latest")
async def get_latest_readings(farm_id: str, sensor_type: Optional[str] = None):
    """Get latest sensor readings for a farm"""
    # TODO: Query InfluxDB for latest readings
    # TODO: Apply farm_id and optional sensor_type filters
    
    return {
        "message": f"Latest readings for farm {farm_id}",
        "farm_id": farm_id,
        "sensor_type": sensor_type,
        "note": "Database integration coming soon"
    }

@router.get("/{farm_id}/{sensor_type}")
async def get_sensor_history(
    farm_id: str, 
    sensor_type: str,
    hours: int = 24,
    device_id: Optional[str] = None
):
    """Get historical sensor data"""
    if sensor_type not in SENSOR_TYPES:
        raise HTTPException(status_code=404, detail=f"Sensor type '{sensor_type}' not found")
    
    # TODO: Query InfluxDB for historical data
    # TODO: Apply time range and device filters
    
    return {
        "message": f"Historical {sensor_type} data for farm {farm_id}",
        "farm_id": farm_id,
        "sensor_type": sensor_type,
        "hours": hours,
        "device_id": device_id,
        "note": "Database integration coming soon"
    }

@router.post("/calibrate/{device_id}")
async def calibrate_device(device_id: str, calibration_data: dict):
    """Set calibration parameters for a device"""
    # TODO: Store calibration data in MySQL
    # TODO: Send calibration commands via MQTT
    
    return {
        "message": f"Calibration settings updated for device {device_id}",
        "device_id": device_id,
        "calibration_data": calibration_data,
        "note": "Calibration system coming soon"
    }

@router.get("/health")
async def sensor_health():
    """Health check for sensor service"""
    return {
        "status": "healthy", 
        "service": "sensors",
        "supported_sensor_count": len(SENSOR_TYPES),
        "timestamp": datetime.now()
    } 