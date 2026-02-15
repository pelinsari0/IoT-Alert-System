from pydantic import EmailStr
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "IoT Alert System (Local Simulation)"
    database_url: str = "sqlite:///./iot_alerts.db"

    # Thresholds
    temp_high_threshold: float = 28.0
    humidity_low_threshold: float = 30.0
    humidity_high_threshold: float = 70.0

    # Night-time for motion alerts (22:00–06:00 by default)
    night_start_hour: int = 22
    night_end_hour: int = 6

    # Email settings (optional)
    enable_email: bool = False
    smtp_host: str = "smtp.example.com"
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    email_from: Optional[EmailStr] = None
    email_to: Optional[EmailStr] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
