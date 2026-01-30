import pytest
from app.core.config import Settings


def test_settings_initialization():
    """Test that Settings can be initialized"""
    settings = Settings()
    assert settings is not None
    assert settings.GEMINI_MODEL == "gemini-1.5-pro"
    assert settings.API_V1_PREFIX == "/api/v1"
    assert settings.PROJECT_NAME == "Pandada.AI Backend"


def test_settings_cors_origins():
    """Test CORS origins configuration"""
    settings = Settings()
    assert isinstance(settings.CORS_ORIGINS, list)
    assert len(settings.CORS_ORIGINS) >= 2
    assert "http://localhost:3000" in settings.CORS_ORIGINS
