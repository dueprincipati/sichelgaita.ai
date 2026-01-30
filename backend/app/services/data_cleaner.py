"""
Data cleaning and normalization service.
Handles data quality improvements, schema standardization, and type inference.
"""

import re
from typing import Dict

import pandas as pd


class DataCleaner:
    """Handles data cleaning and normalization for dataframes."""

    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and normalize a pandas DataFrame.

        Args:
            df: Input DataFrame to clean

        Returns:
            Cleaned DataFrame
        """
        # Create a copy to avoid modifying the original
        df_cleaned = df.copy()

        # Remove completely empty rows
        df_cleaned = df_cleaned.dropna(how="all")

        # Standardize column names
        df_cleaned = DataCleaner.normalize_headers(df_cleaned)

        # Remove duplicate rows
        df_cleaned = df_cleaned.drop_duplicates()

        # Infer and convert data types
        df_cleaned = DataCleaner._infer_and_convert_types(df_cleaned)

        # Reset index after cleaning
        df_cleaned = df_cleaned.reset_index(drop=True)

        return df_cleaned

    @staticmethod
    def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column headers to a standard format.
        Handles multi-row headers and standardizes naming.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with normalized column names
        """
        df_normalized = df.copy()

        # Detect and merge multi-row headers (common in Excel)
        # If first row contains many "Unnamed" columns, it might be a multi-row header
        unnamed_count = sum(1 for col in df_normalized.columns if "Unnamed" in str(col))

        if unnamed_count > len(df_normalized.columns) * 0.3:  # More than 30% unnamed
            # This might be a multi-row header - keep as is for now
            # Advanced implementation would merge rows
            pass

        # Standardize column names
        new_columns = []
        for col in df_normalized.columns:
            # Convert to string
            col_str = str(col)

            # Lowercase
            col_str = col_str.lower()

            # Replace spaces with underscores
            col_str = col_str.replace(" ", "_")

            # Remove special characters except underscores
            col_str = re.sub(r"[^a-z0-9_]", "", col_str)

            # Remove multiple consecutive underscores
            col_str = re.sub(r"_+", "_", col_str)

            # Strip leading/trailing underscores
            col_str = col_str.strip("_")

            # Handle empty column names
            if not col_str:
                col_str = f"column_{len(new_columns)}"

            new_columns.append(col_str)

        df_normalized.columns = new_columns

        return df_normalized

    @staticmethod
    def _infer_and_convert_types(df: pd.DataFrame) -> pd.DataFrame:
        """
        Infer and convert data types for each column.

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with inferred types
        """
        df_converted = df.copy()

        for col in df_converted.columns:
            # Skip if column is already numeric or datetime
            if pd.api.types.is_numeric_dtype(df_converted[col]) or pd.api.types.is_datetime64_any_dtype(
                df_converted[col]
            ):
                continue

            # Try to convert to numeric
            numeric_converted = pd.to_numeric(df_converted[col], errors="coerce")
            if numeric_converted.notna().sum() > len(df_converted) * 0.5:  # More than 50% valid
                df_converted[col] = numeric_converted
                continue

            # Try to convert to datetime
            try:
                datetime_converted = pd.to_datetime(df_converted[col], errors="coerce")
                if datetime_converted.notna().sum() > len(df_converted) * 0.5:  # More than 50% valid
                    df_converted[col] = datetime_converted
                    continue
            except (ValueError, TypeError):
                pass

            # Keep as string if no conversion worked
            df_converted[col] = df_converted[col].astype(str)

        return df_converted

    @staticmethod
    def detect_data_schema(df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect and return the schema of the DataFrame.

        Args:
            df: Input DataFrame

        Returns:
            Dictionary mapping column names to their detected types
        """
        schema = {}

        for col in df.columns:
            dtype = df[col].dtype

            if pd.api.types.is_integer_dtype(dtype):
                schema[col] = "integer"
            elif pd.api.types.is_float_dtype(dtype):
                schema[col] = "float"
            elif pd.api.types.is_datetime64_any_dtype(dtype):
                schema[col] = "datetime"
            elif pd.api.types.is_bool_dtype(dtype):
                schema[col] = "boolean"
            else:
                schema[col] = "string"

        return schema
