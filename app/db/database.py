from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from motor.motor_asyncio import AsyncIOMotorClient
from redis import Redis
import os
from dotenv import load_dotenv

load_dotenv()

# SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./car_chatbot.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# MongoDB
mongodb_client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
mongodb = mongodb_client[os.getenv("MONGODB_DB")]

# Redis
redis_client = Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    decode_responses=True
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_mongodb():
    return mongodb

def get_redis():
    return redis_client 