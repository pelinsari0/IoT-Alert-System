from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from sqlalchemy.sql import func

from .database import Base


class Reading(Base):
    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    location = Column(String, index=True)
    temperature = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    motion = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, index=True)
    location = Column(String, index=True)
    alert_type = Column(String, index=True)
    message = Column(String)
    emailed = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
