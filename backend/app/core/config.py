from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Data Preprocessing Platform"
    API_VERSION: str = "1.0.0"
    
    # CORS
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
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# Create necessary directories
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.TEMP_DIR, exist_ok=True)
