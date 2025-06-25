from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_sensors():
    return {"message": "Sensors endpoint - coming in Phase 2"}

@router.get("/health")
async def sensor_health():
    return {"status": "healthy", "service": "sensors"}

@router.post("/data")
async def receive_sensor_data():
    return {"message": "Sensor data ingestion endpoint - coming in Phase 2"} 