from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class AnalysisRequest(BaseModel):
    """Request model for analysis generation."""
    file_id: UUID
    analysis_types: List[Literal["trend", "anomaly", "executive_summary"]]

class InsightItem(BaseModel):
    """Single insight item."""
    title: str
    description: str
    severity: Literal["high", "medium", "low"] = "medium"
    metric_value: Optional[float] = None
    metric_label: Optional[str] = None

class ChartConfig(BaseModel):
    """Chart configuration for visualization."""
    chart_type: Literal["line", "bar", "pie", "area"]
    data: List[Dict[str, Any]]
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    colors: List[str] = Field(default_factory=lambda: ["#1e40af", "#3b82f6", "#60a5fa"])
    title: str
    description: Optional[str] = None

class AnalysisResult(BaseModel):
    """Single analysis result."""
    id: UUID
    file_id: UUID
    analysis_type: Literal["trend", "anomaly", "executive_summary"]
    insights: List[InsightItem]
    chart_config: Optional[ChartConfig] = None
    anomalies: Optional[List[Dict[str, Any]]] = None
    key_metrics: Optional[List[Dict[str, Any]]] = None
    recommendations: Optional[List[str]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime

    class Config:
        from_attributes = True

class AnalysisResponse(BaseModel):
    """Response model for analysis endpoint."""
    file_id: UUID
    results: List[AnalysisResult]
    message: str
