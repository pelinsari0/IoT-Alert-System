from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from . import models
from .config import settings

import logging
import smtplib
from email.message import EmailMessage

logger = logging.getLogger("iot_alerts")


def _is_night(now: datetime) -> bool:
    start = settings.night_start_hour
    end = settings.night_end_hour
    hour = now.hour

    if start < end:
        return start <= hour < end
    # night crosses midnight (e.g. 22–06)
    return hour >= start or hour < end


def _send_alert_email(alert: models.Alert) -> None:
    if not (settings.smtp_host and settings.email_from and settings.email_to):
        raise RuntimeError("Email settings are incomplete.")

    msg = EmailMessage()
    msg["Subject"] = f"IoT Alert: {alert.alert_type}"
    msg["From"] = settings.email_from
    msg["To"] = settings.email_to
    msg.set_content(f"{alert.message}\n\nTime: {alert.created_at}")

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        if settings.smtp_username and settings.smtp_password:
            server.login(settings.smtp_username, settings.smtp_password)
        server.send_message(msg)


def _create_alert(
    db: Session,
    reading: models.Reading,
    alert_type: str,
    message: str,
) -> models.Alert:
    alert = models.Alert(
        device_id=reading.device_id,
        location=reading.location,
        alert_type=alert_type,
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)

    logger.warning(f"ALERT [{alert.alert_type}] {alert.message}")

    if settings.enable_email:
        try:
            _send_alert_email(alert)
            alert.emailed = True
            db.commit()
        except Exception as exc:
            logger.error(f"Failed to send alert email: {exc}")

    return alert


def evaluate_reading(db: Session, reading: models.Reading) -> List[models.Alert]:
    alerts: List[models.Alert] = []

    # Temperature rule
    if reading.temperature > settings.temp_high_threshold:
        msg = (
            f"High temperature {reading.temperature:.1f}°C at "
            f"{reading.location} ({reading.device_id})"
        )
        alerts.append(_create_alert(db, reading, "HIGH_TEMP", msg))

    # Humidity rule
    if (
        reading.humidity < settings.humidity_low_threshold
        or reading.humidity > settings.humidity_high_threshold
    ):
        msg = (
            f"Abnormal humidity {reading.humidity:.1f}% at "
            f"{reading.location} ({reading.device_id})"
        )
        alerts.append(_create_alert(db, reading, "HUMIDITY", msg))

    # Motion-at-night rule
    now = datetime.utcnow()
    if reading.motion and _is_night(now):
        msg = f"Motion detected at night at {reading.location} ({reading.device_id})"
        alerts.append(_create_alert(db, reading, "MOTION_NIGHT", msg))

    if not alerts:
        logger.info(
            f"Reading OK from {reading.device_id} at {reading.location}: "
            f"T={reading.temperature:.1f}°C, H={reading.humidity:.1f}%, "
            f"MOTION={reading.motion}"
        )

    return alerts
