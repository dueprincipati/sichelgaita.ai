"""
Unit tests for DataCleaner service.
Tests data cleaning, normalization, and schema detection.
"""

import pandas as pd
import pytest

from app.services.data_cleaner import DataCleaner


class TestDataCleaner:
    """Test suite for DataCleaner class."""

    def test_clean_dataframe_removes_empty_rows(self):
        """Test that empty rows are removed."""
        df = pd.DataFrame({"A": [1, None, 3, None], "B": [4, None, 6, None], "C": [7, None, 9, None]})

        cleaned = DataCleaner.clean_dataframe(df)

        assert len(cleaned) == 2  # Only rows with data
        assert cleaned["A"].tolist() == [1, 3]

    def test_clean_dataframe_removes_duplicates(self):
        """Test that duplicate rows are removed."""
        df = pd.DataFrame({"Name": ["Alice", "Bob", "Alice", "Charlie"], "Age": [25, 30, 25, 35]})

        cleaned = DataCleaner.clean_dataframe(df)

        assert len(cleaned) == 3  # Duplicate Alice removed
        assert "alice" in cleaned.columns  # Header normalized

    def test_normalize_headers(self):
        """Test header normalization."""
        df = pd.DataFrame({"First Name": [1, 2], "Last-Name": [3, 4], "AGE!!!": [5, 6], "  City  ": [7, 8]})

        normalized = DataCleaner.normalize_headers(df)

        expected_columns = ["first_name", "lastname", "age", "city"]
        assert normalized.columns.tolist() == expected_columns

    def test_normalize_headers_handles_special_chars(self):
        """Test that special characters are removed from headers."""
        df = pd.DataFrame({"Column@#1": [1], "Column$%2": [2], "Column&*3": [3]})

        normalized = DataCleaner.normalize_headers(df)

        assert "column1" in normalized.columns
        assert "column2" in normalized.columns
        assert "column3" in normalized.columns

    def test_normalize_headers_handles_empty(self):
        """Test handling of empty column names."""
        df = pd.DataFrame([[1, 2, 3]])
        df.columns = ["Valid", "", "   "]

        normalized = DataCleaner.normalize_headers(df)

        assert "valid" in normalized.columns
        assert "column_1" in normalized.columns
        assert "column_2" in normalized.columns

    def test_infer_and_convert_types_numeric(self):
        """Test numeric type inference."""
        df = pd.DataFrame({"numbers_as_string": ["1", "2", "3", "4"], "mixed": ["1", "2", "not_a_number", "4"]})

        cleaned = DataCleaner.clean_dataframe(df)

        # First column should be converted to numeric
        assert pd.api.types.is_numeric_dtype(cleaned["numbers_as_string"])

        # Mixed column should remain as string (less than 50% valid numbers)
        assert cleaned["mixed"].dtype == object or cleaned["mixed"].dtype == "string"

    def test_infer_and_convert_types_datetime(self):
        """Test datetime type inference."""
        df = pd.DataFrame({"dates": ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]})

        cleaned = DataCleaner.clean_dataframe(df)

        # Should be converted to datetime
        assert pd.api.types.is_datetime64_any_dtype(cleaned["dates"])

    def test_detect_data_schema(self):
        """Test schema detection."""
        df = pd.DataFrame(
            {
                "int_col": [1, 2, 3],
                "float_col": [1.1, 2.2, 3.3],
                "string_col": ["a", "b", "c"],
                "date_col": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
                "bool_col": [True, False, True],
            }
        )

        schema = DataCleaner.detect_data_schema(df)

        assert schema["int_col"] == "integer"
        assert schema["float_col"] == "float"
        assert schema["string_col"] == "string"
        assert schema["date_col"] == "datetime"
        assert schema["bool_col"] == "boolean"

    def test_clean_dataframe_preserves_data(self):
        """Test that cleaning preserves valid data."""
        df = pd.DataFrame(
            {
                "Product": ["Widget A", "Widget B", "Widget C"],
                "Revenue": [1000.50, 2000.75, 1500.25],
                "Date": ["2024-01-01", "2024-01-02", "2024-01-03"],
            }
        )

        cleaned = DataCleaner.clean_dataframe(df)

        assert len(cleaned) == 3
        assert "product" in cleaned.columns
        assert "revenue" in cleaned.columns
        assert cleaned["revenue"].sum() == pytest.approx(4501.50)

    def test_clean_dataframe_handles_empty(self):
        """Test cleaning an empty dataframe."""
        df = pd.DataFrame()

        cleaned = DataCleaner.clean_dataframe(df)

        assert len(cleaned) == 0
        assert cleaned.empty
