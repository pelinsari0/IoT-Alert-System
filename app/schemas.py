from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class ReadingBase(BaseModel):
    device_id: str
    location: str
    temperature: float
    humidity: float
    motion: bool


class ReadingCreate(ReadingBase):
    pass


class ReadingOut(ReadingBase):
    id: int
    created_at: datetime

    # Pydantic v2: replaces orm_mode = True
    model_config = ConfigDict(from_attributes=True)


class AlertOut(BaseModel):
    id: int
    device_id: str
    location: str
    alert_type: str
    message: str
    emailed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReadingWithAlerts(BaseModel):
    reading: ReadingOut
    alerts: List[AlertOut]

class EmailRecordOut(BaseModel):
    id: int
    to_address: str
    subject: str
    body: str
    sent_at: datetime
