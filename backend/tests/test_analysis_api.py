import pytest
from uuid import uuid4
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.analysis import AnalysisRequest

client = TestClient(app)


@pytest.fixture
def mock_file_id():
    """Generate a mock file UUID."""
    return str(uuid4())


@pytest.fixture
def mock_supabase_responses(mock_file_id):
    """Create mock Supabase responses."""
    return {
        "file_exists": Mock(
            data=[{
                "id": mock_file_id,
                "file_name": "test.csv",
                "file_size": 1024,
                "status": "completed",
                "created_at": "2024-01-01T00:00:00Z"
            }]
        ),
        "processed_data": Mock(
            data=[{
                "file_id": mock_file_id,
                "cleaned_data": [
                    {"date": "2024-01-01", "value": 100},
                    {"date": "2024-01-02", "value": 150},
                    {"date": "2024-01-03", "value": 200}
                ],
                "data_schema": {
                    "columns": [
                        {"name": "date", "type": "string"},
                        {"name": "value", "type": "integer"}
                    ]
                }
            }]
        ),
        "analysis_insert": Mock(
            data=[{
                "id": str(uuid4()),
                "file_id": mock_file_id,
                "analysis_type": "trend",
                "insights": [{
                    "title": "Test Insight",
                    "description": "Test description",
                    "severity": "high"
                }],
                "chart_config": {
                    "chart_type": "line",
                    "data": [{"x": "Jan", "y": 100}],
                    "title": "Trend Analysis",
                    "colors": ["#1e40af"]
                },
                "metadata": {},
                "created_at": "2024-01-01T00:00:00Z"
            }]
        ),
        "analysis_select": Mock(
            data=[{
                "id": str(uuid4()),
                "file_id": mock_file_id,
                "analysis_type": "trend",
                "insights": [{
                    "title": "Test Insight",
                    "description": "Test description",
                    "severity": "high"
                }],
                "chart_config": None,
                "metadata": {},
                "created_at": "2024-01-01T00:00:00Z"
            }]
        )
    }


class TestAnalysisAPI:
    """Test suite for analysis API endpoints."""

    @patch("app.api.v1.analysis.get_supabase")
    @patch("app.api.v1.analysis.AIAnalyzer")
    def test_generate_analysis_success(
        self, mock_analyzer_class, mock_supabase, mock_file_id, mock_supabase_responses
    ):
        """Test successful analysis generation."""
        # Setup Supabase mocks
        mock_client = Mock()
        mock_table = Mock()
        
        # Chain table operations
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            mock_supabase_responses["file_exists"],
            mock_supabase_responses["processed_data"]
        ]
        mock_table.insert.return_value.execute.return_value = mock_supabase_responses["analysis_insert"]
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = \
            mock_supabase_responses["analysis_select"]
        
        mock_client.table.return_value = mock_table
        mock_supabase.return_value = mock_client
        
        # Setup analyzer mock
        mock_analyzer = Mock()
        mock_analyzer.analyze_trends.return_value = {
            "insights": [{
                "title": "Test Insight",
                "description": "Test description",
                "severity": "high"
            }],
            "chart_data": [{"x": "Jan", "y": 100}],
            "recommended_chart": "line"
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        # Make request
        response = client.post(
            "/api/v1/analysis/generate",
            json={
                "file_id": mock_file_id,
                "analysis_types": ["trend"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["file_id"] == mock_file_id
        assert "results" in data
        assert len(data["results"]) > 0

    @patch("app.api.v1.analysis.get_supabase")
    def test_generate_analysis_file_not_found(self, mock_supabase, mock_file_id):
        """Test analysis with non-existent file."""
        mock_client = Mock()
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.execute.return_value = Mock(data=[])
        mock_client.table.return_value = mock_table
        mock_supabase.return_value = mock_client
        
        response = client.post(
            "/api/v1/analysis/generate",
            json={
                "file_id": mock_file_id,
                "analysis_types": ["trend"]
            }
        )
        
        assert response.status_code == 404
        assert "File not found" in response.json()["detail"]

    @patch("app.api.v1.analysis.get_supabase")
    def test_generate_analysis_file_not_completed(self, mock_supabase, mock_file_id):
        """Test analysis with non-completed file."""
        mock_client = Mock()
        mock_table = Mock()
        mock_table.select.return_value.eq.return_value.execute.return_value = Mock(
            data=[{
                "id": mock_file_id,
                "status": "processing"
            }]
        )
        mock_client.table.return_value = mock_table
        mock_supabase.return_value = mock_client
        
        response = client.post(
            "/api/v1/analysis/generate",
            json={
                "file_id": mock_file_id,
                "analysis_types": ["trend"]
            }
        )
        
        assert response.status_code == 400
        assert "completed" in response.json()["detail"]

    @patch("app.api.v1.analysis.get_supabase")
    def test_generate_analysis_no_processed_data(self, mock_supabase, mock_file_id):
        """Test analysis with missing processed data."""
        mock_client = Mock()
        mock_table = Mock()
        
        # File exists but no processed data
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            Mock(data=[{"id": mock_file_id, "status": "completed"}]),
            Mock(data=[])
        ]
        mock_client.table.return_value = mock_table
        mock_supabase.return_value = mock_client
        
        response = client.post(
            "/api/v1/analysis/generate",
            json={
                "file_id": mock_file_id,
                "analysis_types": ["trend"]
            }
        )
        
        assert response.status_code == 400
        assert "processed data" in response.json()["detail"]

    @patch("app.api.v1.analysis.get_supabase")
    @patch("app.api.v1.analysis.AIAnalyzer")
    def test_generate_multiple_analysis_types(
        self, mock_analyzer_class, mock_supabase, mock_file_id, mock_supabase_responses
    ):
        """Test generating multiple analysis types."""
        # Setup mocks
        mock_client = Mock()
        mock_table = Mock()
        
        mock_table.select.return_value.eq.return_value.execute.side_effect = [
            mock_supabase_responses["file_exists"],
            mock_supabase_responses["processed_data"]
        ]
        mock_table.insert.return_value.execute.return_value = mock_supabase_responses["analysis_insert"]
        mock_table.select.return_value.eq.return_value.order.return_value.execute.return_value = Mock(
            data=[
                {
                    "id": str(uuid4()),
                    "file_id": mock_file_id,
                    "analysis_type": "trend",
                    "insights": [{"title": "Trend", "description": "Test", "severity": "high"}],
                    "chart_config": None,
                    "metadata": {},
                    "created_at": "2024-01-01T00:00:00Z"
                },
                {
                    "id": str(uuid4()),
                    "file_id": mock_file_id,
                    "analysis_type": "anomaly",
                    "insights": [{"title": "Anomaly", "description": "Test", "severity": "medium"}],
                    "chart_config": None,
                    "metadata": {},
                    "created_at": "2024-01-01T00:00:00Z"
                }
            ]
        )
        
        mock_client.table.return_value = mock_table
        mock_supabase.return_value = mock_client
        
        # Setup analyzer
        mock_analyzer = Mock()
        mock_analyzer.analyze_trends.return_value = {
            "insights": [{"title": "Trend", "description": "Test", "severity": "high"}]
        }
        mock_analyzer.detect_anomalies.return_value = {
            "insights": [{"title": "Anomaly", "description": "Test", "severity": "medium"}],
            "anomalies": []
        }
        mock_analyzer_class.return_value = mock_analyzer
        
        # Make request with multiple types
        response = client.post(
            "/api/v1/analysis/generate",
            json={
                "file_id": mock_file_id,
                "analysis_types": ["trend", "anomaly"]
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) == 2

    def test_invalid_request_format(self):
        """Test request with invalid format."""
        response = client.post(
            "/api/v1/analysis/generate",
            json={
                "file_id": "not-a-valid-uuid",
                "analysis_types": ["trend"]
            }
        )
        
        assert response.status_code == 422  # Validation error
