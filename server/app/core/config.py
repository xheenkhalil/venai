import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "VenAI API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str
    
    # Security
    BACKEND_CORS_ORIGINS: list[str] | str = ["http://localhost:3000", "https://venai.vercel.app", "https://venai-puce.vercel.app"]
    
    # Clerk Auth
    CLERK_SECRET_KEY: str | None = None
    CLERK_PUBLISHABLE_KEY: str | None = None
    # API Keys
    TAVILY_API_KEY: str | None = None
    GEMINI_API_KEY: str | None = None
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
