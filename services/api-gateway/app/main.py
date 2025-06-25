from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.routers import auth, users, farms, dashboard
from app.database import engine, Base
from app.websocket import WebSocketManager

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="ShroomLab API Gateway",
    description="Central API Hub for Mushroom Farm Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager for real-time communications
ws_manager = WebSocketManager()

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(farms.router, prefix="/api/v1/farms", tags=["Farms"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])

@app.get("/")
async def root():
    return {
        "message": "ShroomLab API Gateway",
        "version": "1.0.0",
        "status": "running",
        "services": {
            "iot_service": "http://iot-service:8001",
            "business_service": "http://business-service:8002",
            "analytics_service": "http://analytics-service:8003"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "api-gateway"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await ws_manager.connect(websocket, client_id)
    try:
        while True:
            data = await websocket.receive_text()
            await ws_manager.send_personal_message(f"Echo: {data}", client_id)
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    ) 