from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicles = relationship("Vehicle", back_populates="owner")

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    make = Column(String)
    model = Column(String)
    year = Column(Integer)
    vin = Column(String, unique=True)
    mileage = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    owner = relationship("User", back_populates="vehicles")
    maintenance_records = relationship("MaintenanceRecord", back_populates="vehicle")

class MaintenanceRecord(Base):
    __tablename__ = "maintenance_records"

    id = Column(Integer, primary_key=True, index=True)
    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))
    service_type = Column(String)
    description = Column(String)
    date_performed = Column(DateTime)
    mileage = Column(Integer)
    cost = Column(Integer)
    parts_used = Column(JSON)
    notes = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    vehicle = relationship("Vehicle", back_populates="maintenance_records")

class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String)
    response = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    context = Column(JSON)  # Store any relevant context about the conversation 