from sqlalchemy import create_engine, Column, String, DateTime, Float, Text, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

from config import settings

# Create engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DealModel(Base):
    __tablename__ = "deals"
    
    id = Column(String, primary_key=True, index=True)
    property_address = Column(String, index=True)
    property_type = Column(String)
    deal_size = Column(Float)
    status = Column(String)
    analysis_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
