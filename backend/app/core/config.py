from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Data Preprocessing Platform"
    API_VERSION: str = "1.0.0"
    
    # CORS - Must specify exact origins when using credentials (cookies)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    # File upload settings
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS: List[str] = [".csv", ".xlsx", ".xls"]
    UPLOAD_DIR: str = "uploads"
    TEMP_DIR: str = "temp"
    
    # Analysis settings
    OUTLIER_THRESHOLD: float = 1.5  # IQR multiplier
    HIGH_CARDINALITY_THRESHOLD: int = 50
    CORRELATION_THRESHOLD: float = 0.9
    SKEWNESS_THRESHOLD: float = 1.0
    
    # Database settings
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/dml_db"
    
    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email Configuration (for OTP)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""
    SMTP_FROM_NAME: str = "Data Preprocessing Platform"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
