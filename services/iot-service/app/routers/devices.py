from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def list_devices():
    return {"message": "Devices endpoint - coming in Phase 2"}

@router.get("/health")
async def device_health():
    return {"status": "healthy", "service": "devices"}

@router.post("/register")
async def register_device():
    return {"message": "Device registration endpoint - coming in Phase 2"} 