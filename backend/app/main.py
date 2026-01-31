from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.files import router as files_router
from app.api.v1.analysis import router as analysis_router
from app.core.config import settings

app = FastAPI(
    title="Sichelgaita.AI API",
    version="0.1.0",
    description="Backend API for Sichelgaita.AI Data Wealth Platform",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Sichelgaita.AI API",
        "version": "0.1.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "sichelgaita-backend",
        "version": "0.1.0",
    }


# Include API routers
app.include_router(files_router, prefix="/api/v1", tags=["files"])
app.include_router(analysis_router, prefix="/api/v1", tags=["analysis"])
