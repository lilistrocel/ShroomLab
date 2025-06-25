from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import httpx
import os

from app.database import get_db
from app.models import User, Farm, Sensor, Alert, GrowingCycle
from app.routers.auth import get_current_active_user

router = APIRouter()

# Service URLs
IOT_SERVICE_URL = os.getenv("IOT_SERVICE_URL", "http://iot-service:8001")
ANALYTICS_SERVICE_URL = os.getenv("ANALYTICS_SERVICE_URL", "http://analytics-service:8003")

@router.get("/overview")
async def get_dashboard_overview(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get overall system overview statistics"""
    
    # Base query filters based on user role
    if current_user.role.value in ["admin", "manager"]:
        # Admin and managers see all data
        farms_query = db.query(Farm)
        sensors_query = db.query(Sensor)
        alerts_query = db.query(Alert)
        cycles_query = db.query(GrowingCycle)
    else:
        # Regular users see only their farms
        user_farm_ids = db.query(Farm.id).filter(Farm.owner_id == current_user.id).subquery()
        farms_query = db.query(Farm).filter(Farm.owner_id == current_user.id)
        sensors_query = db.query(Sensor).filter(Sensor.farm_id.in_(user_farm_ids))
        alerts_query = db.query(Alert).filter(Alert.farm_id.in_(user_farm_ids))
        cycles_query = db.query(GrowingCycle).filter(GrowingCycle.farm_id.in_(user_farm_ids))
    
    # Get basic counts
    total_farms = farms_query.count()
    active_farms = farms_query.filter(Farm.status == "active").count()
    total_sensors = sensors_query.count()
    active_sensors = sensors_query.filter(Sensor.is_active == True).count()
    
    # Get alert counts
    total_alerts = alerts_query.count()
    active_alerts = alerts_query.filter(Alert.is_resolved == False).count()
    critical_alerts = alerts_query.filter(
        Alert.is_resolved == False,
        Alert.severity == "critical"
    ).count()
    
    # Get growing cycle counts
    total_cycles = cycles_query.count()
    active_cycles = cycles_query.filter(GrowingCycle.status == "active").count()
    
    return {
        "farms": {
            "total": total_farms,
            "active": active_farms,
            "inactive": total_farms - active_farms
        },
        "sensors": {
            "total": total_sensors,
            "active": active_sensors,
            "offline": total_sensors - active_sensors
        },
        "alerts": {
            "total": total_alerts,
            "active": active_alerts,
            "critical": critical_alerts
        },
        "production": {
            "total_cycles": total_cycles,
            "active_cycles": active_cycles,
            "completed_cycles": total_cycles - active_cycles
        }
    }

@router.get("/recent-alerts")
async def get_recent_alerts(
    limit: int = 10,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recent alerts for the dashboard"""
    
    # Base query filters based on user role
    if current_user.role.value in ["admin", "manager"]:
        alerts_query = db.query(Alert)
    else:
        user_farm_ids = db.query(Farm.id).filter(Farm.owner_id == current_user.id).subquery()
        alerts_query = db.query(Alert).filter(Alert.farm_id.in_(user_farm_ids))
    
    alerts = alerts_query.order_by(Alert.created_at.desc()).limit(limit).all()
    
    return alerts

@router.get("/sensor-data/{farm_id}")
async def get_farm_sensor_data(
    farm_id: int,
    hours: int = 24,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get recent sensor data for a farm"""
    
    # Check if user has access to this farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if current_user.role.value not in ["admin", "manager"] and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get sensor data from IoT service
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{IOT_SERVICE_URL}/api/v1/sensors/data/farm/{farm_id}",
                params={"hours": hours}
            )
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": "Could not fetch sensor data", "sensors": []}
    except Exception as e:
        return {"error": str(e), "sensors": []}

@router.get("/production-summary/{farm_id}")
async def get_production_summary(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get production summary for a farm"""
    
    # Check if user has access to this farm
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    if current_user.role.value not in ["admin", "manager"] and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get growing cycles for this farm
    cycles = db.query(GrowingCycle).filter(GrowingCycle.farm_id == farm_id).all()
    
    # Calculate summary metrics
    total_cycles = len(cycles)
    active_cycles = len([c for c in cycles if c.status == "active"])
    completed_cycles = len([c for c in cycles if c.status == "harvested"])
    
    total_yield = sum([c.actual_yield or 0 for c in cycles if c.actual_yield])
    expected_yield = sum([c.expected_yield or 0 for c in cycles if c.expected_yield])
    
    # Group by mushroom variety
    varieties = {}
    for cycle in cycles:
        variety = cycle.mushroom_variety
        if variety not in varieties:
            varieties[variety] = {
                "count": 0,
                "total_yield": 0,
                "expected_yield": 0
            }
        varieties[variety]["count"] += 1
        varieties[variety]["total_yield"] += cycle.actual_yield or 0
        varieties[variety]["expected_yield"] += cycle.expected_yield or 0
    
    return {
        "farm_id": farm_id,
        "summary": {
            "total_cycles": total_cycles,
            "active_cycles": active_cycles,
            "completed_cycles": completed_cycles,
            "total_yield_kg": total_yield,
            "expected_yield_kg": expected_yield,
            "yield_efficiency": (total_yield / expected_yield * 100) if expected_yield > 0 else 0
        },
        "varieties": varieties,
        "recent_cycles": cycles[-5:] if cycles else []
    }

@router.get("/system-health")
async def get_system_health(
    current_user: User = Depends(get_current_active_user)
):
    """Get system health status"""
    
    if current_user.role.value not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Check service health
    services_health = {}
    
    # Check IoT Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{IOT_SERVICE_URL}/health")
            services_health["iot_service"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
    except Exception as e:
        services_health["iot_service"] = {
            "status": "offline",
            "error": str(e)
        }
    
    # Check Analytics Service
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{ANALYTICS_SERVICE_URL}/health")
            services_health["analytics_service"] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds()
            }
    except Exception as e:
        services_health["analytics_service"] = {
            "status": "offline",
            "error": str(e)
        }
    
    return {
        "api_gateway": {"status": "healthy"},
        "services": services_health,
        "timestamp": func.now()
    } 