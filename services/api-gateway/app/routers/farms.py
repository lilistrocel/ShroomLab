from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.database import get_db
from app.models import Farm, User, FarmStatus, Sensor
from app.routers.auth import get_current_active_user

router = APIRouter()

# Pydantic models
class FarmCreate(BaseModel):
    name: str
    description: str = None
    location: str = None
    total_area: float = None
    growing_rooms: int = 1
    max_capacity: float = None

class FarmUpdate(BaseModel):
    name: str = None
    description: str = None
    location: str = None
    status: FarmStatus = None
    total_area: float = None
    growing_rooms: int = None
    max_capacity: float = None

class FarmResponse(BaseModel):
    id: int
    name: str
    description: str = None
    location: str = None
    status: FarmStatus
    total_area: float = None
    growing_rooms: int
    max_capacity: float = None
    created_at: datetime
    owner_id: int

    class Config:
        from_attributes = True

class SensorResponse(BaseModel):
    id: int
    sensor_type: str
    name: str
    location: str = None
    device_id: str
    is_active: bool
    min_threshold: float = None
    max_threshold: float = None

    class Config:
        from_attributes = True

# Routes
@router.post("/", response_model=FarmResponse)
async def create_farm(
    farm: FarmCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    db_farm = Farm(
        **farm.dict(),
        owner_id=current_user.id
    )
    db.add(db_farm)
    db.commit()
    db.refresh(db_farm)
    return db_farm

@router.get("/", response_model=List[FarmResponse])
async def read_farms(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # If user is admin or manager, show all farms, otherwise show only owned farms
    if current_user.role.value in ["admin", "manager"]:
        farms = db.query(Farm).offset(skip).limit(limit).all()
    else:
        farms = db.query(Farm).filter(Farm.owner_id == current_user.id).offset(skip).limit(limit).all()
    return farms

@router.get("/{farm_id}", response_model=FarmResponse)
async def read_farm(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role.value not in ["admin", "manager"] and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return farm

@router.put("/{farm_id}", response_model=FarmResponse)
async def update_farm(
    farm_id: int,
    farm_update: FarmUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role.value not in ["admin", "manager"] and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Update farm
    update_data = farm_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farm, field, value)
    
    db.commit()
    db.refresh(farm)
    return farm

@router.delete("/{farm_id}")
async def delete_farm(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role.value not in ["admin", "manager"] and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    db.delete(farm)
    db.commit()
    return {"message": "Farm deleted successfully"}

@router.get("/{farm_id}/sensors", response_model=List[SensorResponse])
async def get_farm_sensors(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role.value not in ["admin", "manager"] and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    sensors = db.query(Sensor).filter(Sensor.farm_id == farm_id).all()
    return sensors

@router.get("/{farm_id}/dashboard")
async def get_farm_dashboard(
    farm_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    farm = db.query(Farm).filter(Farm.id == farm_id).first()
    if farm is None:
        raise HTTPException(status_code=404, detail="Farm not found")
    
    # Check if user has access to this farm
    if current_user.role.value not in ["admin", "manager"] and farm.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Get basic farm statistics
    sensors_count = db.query(Sensor).filter(Sensor.farm_id == farm_id).count()
    active_sensors_count = db.query(Sensor).filter(
        Sensor.farm_id == farm_id,
        Sensor.is_active == True
    ).count()
    
    return {
        "farm": farm,
        "sensors": {
            "total": sensors_count,
            "active": active_sensors_count,
            "inactive": sensors_count - active_sensors_count
        },
        "status": farm.status,
        "capacity_utilization": 0.0  # TODO: Calculate from growing cycles
    } 