"""
File processing service for handling different file formats.
Supports CSV, Excel, PDF, and image files with format-specific extraction.
"""

import json
from pathlib import Path
from typing import Any, Dict

import fitz  # PyMuPDF
import google.generativeai as genai
import pandas as pd
from PIL import Image
from PyPDF2 import PdfReader

from app.core.config import settings


class FileProcessor:
    """Handles format-specific file processing and data extraction."""

    def __init__(self):
        """Initialize FileProcessor with Gemini AI configuration."""
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.gemini_model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def process_csv(self, file_path: Path) -> Dict[str, Any]:
        """
        Process CSV file using pandas.

        Args:
            file_path: Path to the CSV file

        Returns:
            Dictionary containing dataframe and summary statistics
        """
        try:
            # Try different encodings to handle encoding issues
            encodings = ["utf-8", "latin-1", "iso-8859-1", "cp1252"]
            df = None

            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except UnicodeDecodeError:
                    continue

            if df is None:
                raise ValueError("Failed to read CSV with any supported encoding")

            return {
                "dataframe": df,
                "summary": {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": df.columns.tolist(),
                },
            }

        except Exception as e:
            raise ValueError(f"Failed to process CSV file: {str(e)}")

    def process_excel(self, file_path: Path) -> Dict[str, Any]:
        """
        Process Excel file using pandas with openpyxl engine.

        Args:
            file_path: Path to the Excel file

        Returns:
            Dictionary containing dataframe and summary statistics
        """
        try:
            # Read Excel file with openpyxl engine
            excel_file = pd.ExcelFile(file_path, engine="openpyxl")

            # Get sheet names
            sheet_names = excel_file.sheet_names

            # Read the first sheet or active sheet
            df = pd.read_excel(file_path, sheet_name=sheet_names[0], engine="openpyxl")

            # If multiple sheets exist, store information about them
            sheet_info = {}
            if len(sheet_names) > 1:
                sheet_info = {
                    "total_sheets": len(sheet_names),
                    "sheet_names": sheet_names,
                    "active_sheet": sheet_names[0],
                }

            return {
                "dataframe": df,
                "summary": {
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": df.columns.tolist(),
                    **sheet_info,
                },
            }

        except Exception as e:
            raise ValueError(f"Failed to process Excel file: {str(e)}")

    def process_pdf(self, file_path: Path) -> Dict[str, Any]:
        """
        Process PDF file using PyPDF2 for text extraction.
        Falls back to Gemini Vision OCR if text extraction fails.

        Args:
            file_path: Path to the PDF file

        Returns:
            Dictionary containing extracted text and page count
        """
        try:
            reader = PdfReader(str(file_path))
            num_pages = len(reader.pages)

            # Extract text from all pages
            extracted_text = ""
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"

            # If no text was extracted (scanned PDF), use Gemini Vision
            if not extracted_text.strip():
                extracted_text = self._extract_pdf_with_gemini_vision(file_path)

            return {"text": extracted_text.strip(), "page_count": num_pages}

        except Exception as e:
            raise ValueError(f"Failed to process PDF file: {str(e)}")

    def process_image(self, file_path: Path) -> Dict[str, Any]:
        """
        Process image file using Pillow for validation and Gemini Vision for OCR.

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary containing extracted data and image dimensions
        """
        try:
            # Validate and get image dimensions
            with Image.open(file_path) as img:
                width, height = img.size
                image_format = img.format

            # Extract structured data using Gemini Vision
            extracted_data = self._extract_with_gemini_vision(file_path)

            return {
                "extracted_data": extracted_data,
                "image_dimensions": {"width": width, "height": height},
                "image_format": image_format,
            }

        except Exception as e:
            raise ValueError(f"Failed to process image file: {str(e)}")

    def _extract_with_gemini_vision(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract structured data from an image using Gemini Vision API.

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary containing structured data extracted from the image
        """
        try:
            # Determine MIME type from file extension
            file_ext = file_path.suffix.lower()
            mime_type_map = {
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".png": "image/png",
                ".gif": "image/gif",
                ".webp": "image/webp",
                ".bmp": "image/bmp",
            }
            mime_type = mime_type_map.get(file_ext, "image/jpeg")  # Default to jpeg if unknown

            # Read image file
            with open(file_path, "rb") as f:
                image_data = f.read()

            # Prepare image for Gemini with correct MIME type
            image_part = {"mime_type": mime_type, "data": image_data}

            # Prompt for structured data extraction
            prompt = (
                "Extract structured data from this image. "
                "If it contains tables, return JSON with column headers and rows. "
                "If it's a chart or graph, describe the data points in structured format. "
                "Return valid JSON only."
            )

            # Generate response
            response = self.gemini_model.generate_content([prompt, image_part])

            # Parse response
            try:
                # Try to extract JSON from response
                response_text = response.text.strip()
                if response_text.startswith("```json"):
                    response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
                return json.loads(response_text.strip())
            except json.JSONDecodeError:
                # If not valid JSON, return as text
                return {"extracted_text": response.text, "type": "unstructured"}

        except Exception as e:
            raise ValueError(f"Failed to extract data with Gemini Vision: {str(e)}")

    def _extract_pdf_with_gemini_vision(self, file_path: Path) -> str:
        """
        Extract text from scanned PDF using Gemini Vision API.
        Renders each page to an image and uses OCR to extract text.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text from all PDF pages
        """
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(str(file_path))
            extracted_texts = []

            # Process each page
            for page_num in range(len(pdf_document)):
                page = pdf_document[page_num]

                # Render page to image (high resolution for better OCR)
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                img_data = pix.tobytes("png")

                # Extract text using Gemini Vision
                try:
                    # Prepare image for Gemini
                    image_part = {"mime_type": "image/png", "data": img_data}

                    # Prompt for text extraction
                    prompt = (
                        "Extract all text from this PDF page image. "
                        "Return the text exactly as it appears, maintaining the original formatting and line breaks. "
                        "If there are tables, preserve their structure."
                    )

                    # Generate response
                    response = self.gemini_model.generate_content([prompt, image_part])
                    page_text = response.text.strip()

                    if page_text:
                        extracted_texts.append(f"--- Page {page_num + 1} ---\n{page_text}")

                except Exception as page_error:
                    extracted_texts.append(
                        f"--- Page {page_num + 1} ---\n[Error extracting text: {str(page_error)}]"
                    )

            pdf_document.close()

            # Concatenate all extracted text
            return "\n\n".join(extracted_texts) if extracted_texts else "[No text could be extracted]"

        except Exception as e:
            raise ValueError(f"Failed to extract PDF with Gemini Vision: {str(e)}")

    def generate_ai_summary(self, data: Dict[str, Any], file_type: str) -> str:
        """
        Generate AI-powered summary of the processed data.

        Args:
            data: Processed data dictionary
            file_type: Type of file ('csv', 'excel', 'pdf', 'image')

        Returns:
            AI-generated summary text
        """
        try:
            if file_type in ["csv", "excel"]:
                # Extract sample data from dataframe
                df = data.get("dataframe")
                if df is not None and not df.empty:
                    sample = df.head(5).to_dict(orient="records")
                    columns = df.columns.tolist()

                    prompt = (
                        f"Analyze this dataset. Provide a 2-sentence summary describing: "
                        f"(1) what type of data this is, (2) the time period or scope covered. "
                        f"Columns: {columns}. Data sample: {sample}"
                    )
                else:
                    return "Empty dataset"

            elif file_type == "pdf":
                # Use first 500 characters of extracted text
                text = data.get("text", "")[:500]
                prompt = (
                    f"Summarize this document in 2 sentences. "
                    f"Focus on the document type and main topic. Text: {text}"
                )

            elif file_type == "image":
                # Use extracted data
                extracted = data.get("extracted_data", {})
                prompt = (
                    f"Describe what data or information this image contains in 1-2 sentences. "
                    f"Extracted data: {extracted}"
                )

            else:
                return "Unknown file type"

            # Generate summary with low temperature for consistency
            response = self.gemini_model.generate_content(
                prompt, generation_config=genai.types.GenerationConfig(temperature=0.3)
            )

            return response.text.strip()

        except Exception as e:
            return f"Failed to generate AI summary: {str(e)}"
