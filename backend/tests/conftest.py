"""
Pytest configuration and shared fixtures for backend tests.
"""
import os
import pytest
from unittest.mock import Mock, MagicMock

# Set test environment variables before importing app components
os.environ.setdefault("SUPABASE_URL", "https://test.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_KEY", "test-key")
os.environ.setdefault("GEMINI_API_KEY", "test-gemini-key")


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client for testing."""
    mock_client = MagicMock()
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    return mock_client


@pytest.fixture
def mock_gemini_model():
    """Create a mock Gemini model for testing."""
    mock_model = MagicMock()
    return mock_model


@pytest.fixture(autouse=True)
def reset_environment():
    """Reset environment variables after each test."""
    yield
    # Cleanup if needed
