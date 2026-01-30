"""
Pydantic models for file management and data processing.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class DataSummary(BaseModel):
    """Internal model for summarizing extracted data."""

    row_count: Optional[int] = None
    column_count: Optional[int] = None
    columns: Optional[List[str]] = None
    date_range: Optional[Dict[str, str]] = None
    detected_entities: Optional[List[str]] = None


class FileMetadata(BaseModel):
    """Response model for file metadata."""

    id: UUID
    filename: str
    file_type: Literal["csv", "excel", "pdf", "image"]
    file_size: int
    status: Literal["uploading", "processing", "completed", "failed"]
    ai_summary: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True


class FileUploadResponse(BaseModel):
    """Response model for file upload endpoint."""

    file_id: UUID
    storage_url: str
    status: str
    message: str


class ProcessedData(BaseModel):
    """Model for processed and cleaned data."""

    file_id: UUID
    cleaned_data: Dict[str, Any]
    data_schema: Dict[str, str]

    class Config:
        from_attributes = True
