from typing import List, Optional

import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session

from . import alerts, models, schemas
from .config import settings
from .database import Base, engine, get_db



def setup_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    handler = RotatingFileHandler("logs/system.log", maxBytes=1_000_000, backupCount=3)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)


setup_logging()
logger = logging.getLogger("main")

Base.metadata.create_all(bind=engine)


app = FastAPI(title=settings.app_name)


@app.get("/")
def root():
    return {"message": "IoT Alert System is running", "app": settings.app_name}


@app.post("/api/readings", response_model=schemas.ReadingWithAlerts)
def create_reading(
    payload: schemas.ReadingCreate,
    db: Session = Depends(get_db),
):
    reading = models.Reading(**payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)

    generated_alerts = alerts.evaluate_reading(db, reading)

    
    reading_out = schemas.ReadingOut.model_validate(reading)
    alerts_out = [
        schemas.AlertOut.model_validate(alert_obj)
        for alert_obj in generated_alerts
    ]

    return schemas.ReadingWithAlerts(reading=reading_out, alerts=alerts_out)



@app.get("/api/readings", response_model=List[schemas.ReadingOut])
def list_readings(
    db: Session = Depends(get_db),
    device_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
):
    query = db.query(models.Reading).order_by(models.Reading.id.desc())
    if device_id:
        query = query.filter(models.Reading.device_id == device_id)
    return query.limit(limit).all()


@app.get("/api/alerts", response_model=List[schemas.AlertOut])
def list_alerts(
    db: Session = Depends(get_db),
    device_id: Optional[str] = None,
    limit: int = Query(50, ge=1, le=500),
):
    query = db.query(models.Alert).order_by(models.Alert.id.desc())
    if device_id:
        query = query.filter(models.Alert.device_id == device_id)
    return query.limit(limit).all()


@app.get("/api/email-log", response_model=List[schemas.EmailRecordOut])
def list_email_log(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=500),
):
    
    alert_rows = (
        db.query(models.Alert)
        .filter(models.Alert.emailed == True)  
        .order_by(models.Alert.id.desc())
        .limit(limit)
        .all()
    )

    records: List[schemas.EmailRecordOut] = []

    for a in alert_rows:
        subject = f"IoT Alert: {a.alert_type}"
        body = f"{a.message}\n\nTime: {a.created_at}"
        to_addr = settings.email_to or "(not configured)"

        records.append(
            schemas.EmailRecordOut(
                id=a.id,
                to_address=to_addr,
                subject=subject,
                body=body,
                sent_at=a.created_at,
            )
        )

    return records
