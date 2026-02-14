from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "blogs"
    DB_USER: str = "postgres"
    DB_PASS: str = ""
    
    # Or use direct URL (priority to direct URL if provided)
    DATABASE_URL: Optional[str] = None
    
    # App settings
    APP_NAME: str = "FastAPI App"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key"
    API_PREFIX: str = ""
    
    # Redis (optional)
    REDIS_URL: Optional[str] = None
    
    # CORS (optional)
    CORS_ORIGINS: str = "*"
    
    # Build database URL if not provided directly
    @property
    def database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"postgresql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()