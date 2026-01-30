"""
Unit tests for FileProcessor service.
Tests CSV, Excel, PDF, and image processing functionality.
"""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from app.services.file_processor import FileProcessor


@pytest.fixture
def file_processor():
    """Create a FileProcessor instance with mocked Gemini."""
    with patch("app.services.file_processor.genai.configure"):
        processor = FileProcessor()
        processor.gemini_model = MagicMock()
        return processor


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing."""
    csv_path = tmp_path / "sample.csv"
    csv_content = """name,age,city
John Doe,30,New York
Jane Smith,25,Los Angeles

Bob Johnson,35,Chicago
"""
    csv_path.write_text(csv_content)
    return csv_path


@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file for testing."""
    excel_path = tmp_path / "sample.xlsx"

    # Create a simple Excel file
    df = pd.DataFrame({"Product": ["A", "B", "C"], "Revenue": [100, 200, 300], "Date": ["2024-01-01", "2024-01-02", "2024-01-03"]})

    df.to_excel(excel_path, index=False, engine="openpyxl")
    return excel_path


class TestFileProcessor:
    """Test suite for FileProcessor class."""

    def test_process_csv_success(self, file_processor, sample_csv_file):
        """Test successful CSV processing."""
        result = file_processor.process_csv(sample_csv_file)

        assert "dataframe" in result
        assert "summary" in result

        df = result["dataframe"]
        assert len(df) == 3  # Empty row should be dropped by pandas
        assert list(df.columns) == ["name", "age", "city"]

        summary = result["summary"]
        assert summary["row_count"] == 3
        assert summary["column_count"] == 3
        assert summary["columns"] == ["name", "age", "city"]

    def test_process_csv_encoding_fallback(self, file_processor, tmp_path):
        """Test CSV processing with encoding issues."""
        # Create a CSV with latin-1 encoding
        csv_path = tmp_path / "encoded.csv"
        content = "name,value\nJosé,100\n"
        csv_path.write_bytes(content.encode("latin-1"))

        result = file_processor.process_csv(csv_path)

        assert "dataframe" in result
        assert len(result["dataframe"]) == 1

    def test_process_csv_invalid_file(self, file_processor, tmp_path):
        """Test CSV processing with invalid file."""
        invalid_path = tmp_path / "invalid.csv"
        invalid_path.write_text("This is not valid CSV content {{{}}")

        with pytest.raises(ValueError, match="Failed to process CSV file"):
            file_processor.process_csv(invalid_path)

    def test_process_excel_success(self, file_processor, sample_excel_file):
        """Test successful Excel processing."""
        result = file_processor.process_excel(sample_excel_file)

        assert "dataframe" in result
        assert "summary" in result

        df = result["dataframe"]
        assert len(df) == 3
        assert "Product" in df.columns
        assert "Revenue" in df.columns

        summary = result["summary"]
        assert summary["row_count"] == 3
        assert summary["column_count"] == 3

    def test_process_excel_multi_sheet(self, file_processor, tmp_path):
        """Test Excel processing with multiple sheets."""
        excel_path = tmp_path / "multi_sheet.xlsx"

        with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
            pd.DataFrame({"A": [1, 2]}).to_excel(writer, sheet_name="Sheet1", index=False)
            pd.DataFrame({"B": [3, 4]}).to_excel(writer, sheet_name="Sheet2", index=False)

        result = file_processor.process_excel(excel_path)

        summary = result["summary"]
        assert "total_sheets" in summary
        assert summary["total_sheets"] == 2
        assert "sheet_names" in summary
        assert len(summary["sheet_names"]) == 2

    def test_process_pdf_with_text(self, file_processor, tmp_path):
        """Test PDF processing with extractable text."""
        # Note: Creating a real PDF requires additional libraries
        # This test would need a sample PDF file or mocking PyPDF2
        pass

    def test_process_image_success(self, file_processor, tmp_path):
        """Test image processing."""
        # Create a simple test image
        from PIL import Image

        image_path = tmp_path / "test.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(image_path)

        # Mock Gemini Vision response
        mock_response = Mock()
        mock_response.text = '{"table": [["Header1", "Header2"], ["Value1", "Value2"]]}'
        file_processor.gemini_model.generate_content.return_value = mock_response

        result = file_processor.process_image(image_path)

        assert "extracted_data" in result
        assert "image_dimensions" in result
        assert result["image_dimensions"]["width"] == 100
        assert result["image_dimensions"]["height"] == 100

    def test_generate_ai_summary_csv(self, file_processor):
        """Test AI summary generation for CSV data."""
        # Mock Gemini response
        mock_response = Mock()
        mock_response.text = "This dataset contains sales data for 2024 with revenue and product information."
        file_processor.gemini_model.generate_content.return_value = mock_response

        df = pd.DataFrame({"product": ["A", "B"], "revenue": [100, 200]})
        data = {"dataframe": df}

        summary = file_processor.generate_ai_summary(data, "csv")

        assert isinstance(summary, str)
        assert len(summary) > 0
        file_processor.gemini_model.generate_content.assert_called_once()

    def test_generate_ai_summary_pdf(self, file_processor):
        """Test AI summary generation for PDF data."""
        mock_response = Mock()
        mock_response.text = "This is a financial report covering Q1 2024."
        file_processor.gemini_model.generate_content.return_value = mock_response

        data = {"text": "Financial Report Q1 2024... [more text]", "page_count": 5}

        summary = file_processor.generate_ai_summary(data, "pdf")

        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_generate_ai_summary_empty_data(self, file_processor):
        """Test AI summary with empty data."""
        df = pd.DataFrame()
        data = {"dataframe": df}

        summary = file_processor.generate_ai_summary(data, "csv")

        assert summary == "Empty dataset"
