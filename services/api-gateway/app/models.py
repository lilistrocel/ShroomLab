from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    OPERATOR = "operator"
    VIEWER = "viewer"

class FarmStatus(enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.VIEWER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farms = relationship("Farm", back_populates="owner")

class Farm(Base):
    __tablename__ = "farms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    location = Column(String(200))
    status = Column(Enum(FarmStatus), default=FarmStatus.ACTIVE)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Farm specifications
    total_area = Column(Float)  # in square meters
    growing_rooms = Column(Integer, default=1)
    max_capacity = Column(Float)  # in kg
    
    # Relationships
    owner = relationship("User", back_populates="farms")
    growing_cycles = relationship("GrowingCycle", back_populates="farm")
    sensors = relationship("Sensor", back_populates="farm")

class GrowingCycle(Base):
    __tablename__ = "growing_cycles"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    mushroom_variety = Column(String(100), nullable=False)
    start_date = Column(DateTime(timezone=True), nullable=False)
    expected_harvest_date = Column(DateTime(timezone=True))
    actual_harvest_date = Column(DateTime(timezone=True))
    status = Column(String(50), default="active")  # active, harvested, failed
    
    # Production metrics
    substrate_weight = Column(Float)  # in kg
    expected_yield = Column(Float)  # in kg
    actual_yield = Column(Float)  # in kg
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farm = relationship("Farm", back_populates="growing_cycles")
    production_logs = relationship("ProductionLog", back_populates="growing_cycle")

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    sensor_type = Column(String(50), nullable=False)  # temperature, humidity, co2, ph, etc.
    name = Column(String(100), nullable=False)
    location = Column(String(200))  # room location within farm
    device_id = Column(String(100), unique=True, nullable=False)  # IoT device identifier
    is_active = Column(Boolean, default=True)
    
    # Sensor configuration
    min_threshold = Column(Float)
    max_threshold = Column(Float)
    alert_enabled = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    farm = relationship("Farm", back_populates="sensors")

class ProductionLog(Base):
    __tablename__ = "production_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    growing_cycle_id = Column(Integer, ForeignKey("growing_cycles.id"), nullable=False)
    log_type = Column(String(50), nullable=False)  # watering, harvesting, substrate_prep, etc.
    description = Column(Text)
    quantity = Column(Float)  # amount in relevant unit
    unit = Column(String(20))  # kg, liters, etc.
    performed_by = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    growing_cycle = relationship("GrowingCycle", back_populates="production_logs")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    farm_id = Column(Integer, ForeignKey("farms.id"), nullable=False)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))
    alert_type = Column(String(50), nullable=False)  # threshold, device_offline, system, etc.
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    title = Column(String(200), nullable=False)
    description = Column(Text)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True))
    resolved_by = Column(String(100))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 