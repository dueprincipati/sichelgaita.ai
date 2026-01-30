# Sichelgaida.AI Backend

FastAPI backend service for the Sichelgaida.AI Data Wealth Platform.

## Features

- **FastAPI**: Modern, fast web framework for building APIs
- **Pandas**: Powerful data processing and analysis
- **Gemini AI**: AI-powered insights using Google's Gemini Pro
- **Supabase**: Database and authentication integration
- **Poetry**: Dependency management and packaging

## Setup

### Prerequisites

- Python 3.11+
- Poetry

### Installation

```bash
# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Copy environment file
cp ../.env.example .env
# Edit .env with your configuration
```

## Development

### Run the server

```bash
# Development mode with auto-reload
poetry run uvicorn app.main:app --reload

# The API will be available at:
# - API: http://localhost:8000
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

### Code Quality

```bash
# Format code with Black
poetry run black .

# Lint with Ruff
poetry run ruff check .

# Type checking with MyPy
poetry run mypy .
```

### Testing

```bash
# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/test_main.py
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI application entry point
│   ├── core/             # Core configurations
│   │   ├── config.py     # Settings and environment variables
│   ├── api/              # API endpoints
│   │   └── v1/          # API version 1
│   ├── services/         # Business logic
│   └── models/           # Data models
├── tests/                # Test suite
├── pyproject.toml        # Poetry configuration
└── README.md
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

See `.env.example` in the root directory for required environment variables.
