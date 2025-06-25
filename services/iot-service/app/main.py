from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from dotenv import load_dotenv

from app.routers import sensors, devices

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ShroomLab IoT Service",
    description="IoT and Sensor Management Service for Mushroom Farm",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(sensors.router, prefix="/api/v1/sensors", tags=["Sensors"])
app.include_router(devices.router, prefix="/api/v1/devices", tags=["Devices"])

@app.get("/")
async def root():
    return {
        "message": "ShroomLab IoT Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "iot-service"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    ) 