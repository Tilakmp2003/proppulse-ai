from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./proppulse_ai.db"
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Email Configuration
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_EMAIL: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    
    # External APIs
    COSTAR_API_KEY: Optional[str] = None
    ZILLOW_API_KEY: Optional[str] = None
    NEIGHBORHOODSCOUT_API_KEY: Optional[str] = None
    RAPIDAPI_KEY: Optional[str] = None
    
    # AI APIs
    GEMINI_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    
    # JWT
    SECRET_KEY: str = "your_secret_key_change_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 50000000  # 50MB
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
