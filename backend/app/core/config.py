from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Path to root .env file (shared with frontend)
ROOT_DIR = Path(__file__).resolve().parents[3]
ENV_FILE = ROOT_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Supabase Configuration
    SUPABASE_URL: str = ""
    SUPABASE_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""

    # Gemini AI Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-pro"

    # Database Configuration
    DATABASE_URL: str = ""

    # Application Configuration
    API_URL: str = "http://localhost:8000"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Pandada.AI Backend"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


# Create global settings instance
settings = Settings()
