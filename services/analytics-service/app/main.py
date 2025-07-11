from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(
    title="ShroomLab Analytics Service",
    description="Data Analysis and Reporting Service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "ShroomLab Analytics Service",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "analytics-service"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8003, reload=True) 