from pydantic import Field
from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # General
    APP_NAME: str = "Data Preprocessing Pipeline"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=False)

    # API
    API_V1_PREFIX: str = "/api"
    ALLOWED_HOSTS: List[str] = Field(default=["*"])
    
    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/preprocessing_pipeline"
    )
    DB_ECHO_LOG: bool = Field(default=False)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    
    # Storage
    S3_ENDPOINT: Optional[str] = Field(default="http://localhost:9000")
    S3_ACCESS_KEY: str = Field(default="minioadmin")
    S3_SECRET_KEY: str = Field(default="minioadmin")
    S3_BUCKET_NAME: str = Field(default="preprocessing-pipeline")
    S3_REGION: Optional[str] = Field(default=None)
    USE_S3: bool = Field(default=True)
    
    # File uploads
    UPLOAD_DIR: str = Field(default="/tmp/preprocessing-pipeline/uploads")
    MAX_UPLOAD_SIZE: int = Field(default=100 * 1024 * 1024)  # 100MB
    ALLOWED_UPLOAD_EXTENSIONS: List[str] = Field(
        default=[
            # Documents
            ".csv", ".tsv", ".txt", ".json", ".jsonl", ".xml", ".pdf",
            # Images
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff",
            # Audio
            ".wav", ".mp3", ".ogg", ".flac", ".m4a",
            # Video
            ".mp4", ".avi", ".mov", ".mkv", ".webm",
            # Archives for batch uploads
            ".zip", ".tar", ".gz"
        ]
    )
    
    # Security
    SECRET_KEY: str = Field(default="dev_secret_key")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60 * 24 * 8)  # 8 days
    
    # Logging
    LOG_LEVEL: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Create global settings object
settings = Settings()

# Create upload directory if it doesn't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True) 