from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator
from typing import List, Optional
import uvicorn
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.models.models import Vehicle, MaintenanceRecord, ChatHistory
from app.services.chat_service import chat_service

app = FastAPI(
    title="Car Maintenance Chatbot",
    description="An AI-powered chatbot for car maintenance and repairs",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    vehicle_info: Optional[dict] = None

class ChatResponse(BaseModel):
    response: str
    suggested_actions: List[str]

class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int
    vin: str
    mileage: int

    @validator('year')
    def validate_year(cls, v):
        if v < 1900 or v > 2100:
            raise ValueError('Year must be between 1900 and 2100')
        return v

    @validator('mileage')
    def validate_mileage(cls, v):
        if v < 0:
            raise ValueError('Mileage cannot be negative')
        return v

class MaintenanceRecordCreate(BaseModel):
    vehicle_id: int
    serviceType: str
    date: datetime
    mileage: int
    cost: float
    notes: Optional[str] = None

    @validator('mileage')
    def validate_mileage(cls, v):
        if v < 0:
            raise ValueError('Mileage cannot be negative')
        return v

    @validator('cost')
    def validate_cost(cls, v):
        if v < 0:
            raise ValueError('Cost cannot be negative')
        return v

# Routes
@app.get("/")
async def root():
    return {"message": "Welcome to Car Maintenance Chatbot API"}

@app.get("/vehicles")
async def get_vehicles(db: Session = Depends(get_db)):
    vehicles = db.query(Vehicle).all()
    return vehicles

@app.post("/vehicles")
async def create_vehicle(vehicle: VehicleCreate, db: Session = Depends(get_db)):
    try:
        db_vehicle = Vehicle(
            make=vehicle.make,
            model=vehicle.model,
            year=vehicle.year,
            vin=vehicle.vin,
            mileage=vehicle.mileage,
            user_id=1  # TODO: Get from current user
        )
        db.add(db_vehicle)
        db.commit()
        db.refresh(db_vehicle)
        return db_vehicle
    except IntegrityError as e:
        db.rollback()
        if "unique constraint" in str(e.orig).lower():
            raise HTTPException(status_code=400, detail="A vehicle with this VIN already exists")
        raise HTTPException(status_code=400, detail="Database integrity error")
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/vehicles/{vehicle_id}")
async def delete_vehicle(vehicle_id: int, db: Session = Depends(get_db)):
    try:
        vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")
        
        db.delete(vehicle)
        db.commit()
        return {"message": "Vehicle deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/maintenance/records")
async def get_maintenance_records(vehicle_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(MaintenanceRecord)
    if vehicle_id:
        query = query.filter(MaintenanceRecord.vehicle_id == vehicle_id)
    return query.all()

@app.get("/maintenance/records/{record_id}")
async def get_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Maintenance record not found")
    return record

@app.post("/maintenance/records")
async def create_maintenance_record(record: MaintenanceRecordCreate, db: Session = Depends(get_db)):
    try:
        # Verify vehicle exists
        vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        db_record = MaintenanceRecord(
            vehicle_id=record.vehicle_id,
            service_type=record.serviceType,
            date_performed=record.date,
            mileage=record.mileage,
            cost=record.cost,
            notes=record.notes
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/maintenance/records/{record_id}")
async def update_maintenance_record(record_id: int, record: MaintenanceRecordCreate, db: Session = Depends(get_db)):
    try:
        db_record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
        if not db_record:
            raise HTTPException(status_code=404, detail="Maintenance record not found")

        # Verify vehicle exists
        vehicle = db.query(Vehicle).filter(Vehicle.id == record.vehicle_id).first()
        if not vehicle:
            raise HTTPException(status_code=404, detail="Vehicle not found")

        # Update record fields
        for key, value in record.dict().items():
            if key == "serviceType":
                setattr(db_record, "service_type", value)
            elif key == "date":
                setattr(db_record, "date_performed", value)
            else:
                setattr(db_record, key, value)

        db.commit()
        db.refresh(db_record)
        return db_record
    except HTTPException as e:
        raise e
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/maintenance/records/{record_id}")
async def delete_maintenance_record(record_id: int, db: Session = Depends(get_db)):
    try:
        record = db.query(MaintenanceRecord).filter(MaintenanceRecord.id == record_id).first()
        if not record:
            raise HTTPException(status_code=404, detail="Maintenance record not found")
        
        db.delete(record)
        db.commit()
        return {"message": "Maintenance record deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/chat/history")
async def get_chat_history(db: Session = Depends(get_db)):
    try:
        # Get chat history for the current user (user_id=1 for now)
        chat_history = db.query(ChatHistory).filter(ChatHistory.user_id == 1).all()
        return [{"role": "assistant" if h.message else "user", "content": h.message or h.response} for h in chat_history]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/suggestions")
async def get_suggestions(vehicle_info: dict, db: Session = Depends(get_db)):
    try:
        # Get vehicle-specific suggestions based on maintenance records
        vehicle = db.query(Vehicle).filter(
            Vehicle.make == vehicle_info.get('make'),
            Vehicle.model == vehicle_info.get('model'),
            Vehicle.year == vehicle_info.get('year')
        ).first()

        if not vehicle:
            return {"suggestions": [
                "Add your vehicle to the system",
                "Schedule a maintenance check",
                "Get a vehicle inspection"
            ]}

        # Get recent maintenance records
        recent_records = db.query(MaintenanceRecord).filter(
            MaintenanceRecord.vehicle_id == vehicle.id
        ).order_by(MaintenanceRecord.date_performed.desc()).limit(5).all()

        suggestions = []
        if not recent_records:
            suggestions.append("Schedule your first maintenance service")
        else:
            last_record = recent_records[0]
            if last_record.mileage - vehicle.mileage > 5000:
                suggestions.append("Schedule an oil change")
            if last_record.mileage - vehicle.mileage > 10000:
                suggestions.append("Schedule a tire rotation")
            if last_record.mileage - vehicle.mileage > 30000:
                suggestions.append("Schedule a major service")

        suggestions.extend([
            "Check maintenance schedule",
            "View maintenance history",
            "Get maintenance cost estimate"
        ])

        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # Save the user's message to chat history
        user_message = request.messages[-1]
        db_chat = ChatHistory(
            user_id=1,  # TODO: Get from current user
            message=user_message.content,
            response="",  # Will be updated after getting AI response
            context={"vehicle_info": request.vehicle_info}
        )
        db.add(db_chat)
        db.commit()

        # Get response from chat service
        chat_response = chat_service.get_response(
            user_input=user_message.content,
            vehicle_info=request.vehicle_info
        )

        # Update the chat history with the response
        db_chat.response = chat_response["response"]
        db.commit()

        return ChatResponse(
            response=chat_response["response"],
            suggested_actions=chat_response["suggested_actions"]
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 