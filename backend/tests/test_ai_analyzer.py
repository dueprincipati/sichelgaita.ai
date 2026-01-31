import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from app.services.ai_analyzer import AIAnalyzer


@pytest.fixture
def mock_df():
    """Create a mock DataFrame with test data."""
    np.random.seed(42)
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    data = {
        "date": dates,
        "revenue": np.random.normal(1000, 100, 100),
        "users": np.random.randint(50, 150, 100),
        "conversion_rate": np.random.uniform(0.01, 0.05, 100)
    }
    return pd.DataFrame(data)


@pytest.fixture
def mock_schema():
    """Create a mock data schema."""
    return {
        "columns": [
            {"name": "date", "type": "datetime"},
            {"name": "revenue", "type": "float"},
            {"name": "users", "type": "integer"},
            {"name": "conversion_rate", "type": "float"}
        ]
    }


@pytest.fixture
def mock_gemini_response():
    """Create a mock Gemini response."""
    mock_response = Mock()
    mock_response.text = """{
        "insights": [
            {
                "title": "Revenue Growth Trend",
                "description": "Revenue shows consistent growth of 15% MoM",
                "severity": "high",
                "metric_value": 15.0,
                "metric_label": "Growth %"
            }
        ],
        "chart_data": [
            {"x": "Jan", "y": 1000},
            {"x": "Feb", "y": 1150},
            {"x": "Mar", "y": 1322}
        ],
        "recommended_chart": "line"
    }"""
    return mock_response


class TestAIAnalyzer:
    """Test suite for AIAnalyzer service."""

    @patch("app.services.ai_analyzer.genai.configure")
    @patch("app.services.ai_analyzer.genai.GenerativeModel")
    def test_initialization(self, mock_model, mock_configure):
        """Test AIAnalyzer initialization."""
        analyzer = AIAnalyzer()
        
        assert analyzer is not None
        mock_configure.assert_called_once()
        mock_model.assert_called_once()

    @patch("app.services.ai_analyzer.genai.configure")
    @patch("app.services.ai_analyzer.genai.GenerativeModel")
    def test_analyze_trends_success(
        self, mock_model_class, mock_configure, mock_df, mock_schema, mock_gemini_response
    ):
        """Test successful trend analysis."""
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_gemini_response
        mock_model_class.return_value = mock_model
        
        analyzer = AIAnalyzer()
        result = analyzer.analyze_trends(mock_df, mock_schema)
        
        assert "insights" in result
        assert len(result["insights"]) > 0
        assert result["insights"][0]["title"] == "Revenue Growth Trend"
        assert result["insights"][0]["severity"] == "high"
        assert "chart_data" in result
        assert result["recommended_chart"] == "line"

    @patch("app.services.ai_analyzer.genai.configure")
    @patch("app.services.ai_analyzer.genai.GenerativeModel")
    def test_detect_anomalies_with_outliers(
        self, mock_model_class, mock_configure, mock_df, mock_schema
    ):
        """Test anomaly detection with synthetic outliers."""
        # Add synthetic outliers
        mock_df.loc[10, "revenue"] = 5000  # Extreme outlier
        mock_df.loc[50, "revenue"] = 100   # Low outlier
        
        mock_response = Mock()
        mock_response.text = """{
            "insights": [
                {
                    "title": "Revenue Spike Detected",
                    "description": "Unusual revenue spike at row 10",
                    "severity": "high",
                    "metric_value": 5000,
                    "metric_label": "Revenue"
                }
            ],
            "anomalies": [
                {"index": 10, "value": 5000, "expected": 1000}
            ]
        }"""
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        analyzer = AIAnalyzer()
        result = analyzer.detect_anomalies(mock_df, mock_schema)
        
        assert "insights" in result
        assert "anomalies" in result
        assert len(result["anomalies"]) > 0

    @patch("app.services.ai_analyzer.genai.configure")
    @patch("app.services.ai_analyzer.genai.GenerativeModel")
    def test_generate_executive_summary(
        self, mock_model_class, mock_configure, mock_df, mock_schema
    ):
        """Test executive summary generation."""
        file_metadata = {
            "name": "test_data.csv",
            "size": 1024,
            "upload_date": "2024-01-01"
        }
        
        mock_response = Mock()
        mock_response.text = """{
            "insights": [
                {
                    "title": "Strong Performance",
                    "description": "Q1 revenue exceeded targets by 20%",
                    "severity": "high"
                }
            ],
            "key_metrics": [
                {"label": "Total Revenue", "value": 100000, "change": "+20%"}
            ],
            "recommendations": [
                "Scale marketing in high-performing segments",
                "Optimize conversion funnel based on user behavior"
            ]
        }"""
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        analyzer = AIAnalyzer()
        result = analyzer.generate_executive_summary(mock_df, mock_schema, file_metadata)
        
        assert "insights" in result
        assert "key_metrics" in result
        assert "recommendations" in result
        assert len(result["recommendations"]) == 2

    @patch("app.services.ai_analyzer.genai.configure")
    @patch("app.services.ai_analyzer.genai.GenerativeModel")
    def test_parse_json_with_markdown(self, mock_model_class, mock_configure):
        """Test JSON parsing with markdown code blocks."""
        analyzer = AIAnalyzer()
        
        # Test with markdown code blocks
        text_with_markdown = """```json
{
    "insights": [{"title": "Test", "description": "Test desc", "severity": "high"}]
}
```"""
        result = analyzer._parse_json_response(text_with_markdown)
        assert "insights" in result
        assert result["insights"][0]["title"] == "Test"

    @patch("app.services.ai_analyzer.genai.configure")
    @patch("app.services.ai_analyzer.genai.GenerativeModel")
    def test_analyze_trends_error_handling(
        self, mock_model_class, mock_configure, mock_df, mock_schema
    ):
        """Test error handling in trend analysis."""
        mock_model = Mock()
        mock_model.generate_content.side_effect = Exception("API Error")
        mock_model_class.return_value = mock_model
        
        analyzer = AIAnalyzer()
        result = analyzer.analyze_trends(mock_df, mock_schema)
        
        # Should return fallback structure
        assert "insights" in result
        assert "Analisi non disponibile" in result["insights"][0]["title"]
        assert result["insights"][0]["severity"] == "low"

    @patch("app.services.ai_analyzer.genai.configure")
    @patch("app.services.ai_analyzer.genai.GenerativeModel")
    def test_invalid_json_response(self, mock_model_class, mock_configure, mock_df, mock_schema):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.text = "This is not valid JSON"
        
        mock_model = Mock()
        mock_model.generate_content.return_value = mock_response
        mock_model_class.return_value = mock_model
        
        analyzer = AIAnalyzer()
        result = analyzer.analyze_trends(mock_df, mock_schema)
        
        # Should return error structure
        assert "insights" in result
        assert "Errore di parsing" in result["insights"][0]["title"]
