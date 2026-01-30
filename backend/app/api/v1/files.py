"""
File upload and management API endpoints.
Handles multipart file uploads with processing pipeline.
"""

import json
import os
import tempfile
from pathlib import Path
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status

from app.core.database import supabase
from app.models.file import FileUploadResponse
from app.services.data_cleaner import DataCleaner
from app.services.file_processor import FileProcessor
from app.services.storage import StorageService

router = APIRouter()

# Allowed file extensions
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".pdf", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


def get_file_type(filename: str) -> str:
    """
    Determine file type from filename extension.

    Args:
        filename: Name of the file

    Returns:
        File type: 'csv', 'excel', 'pdf', or 'image'
    """
    ext = Path(filename).suffix.lower()

    if ext == ".csv":
        return "csv"
    elif ext in [".xlsx", ".xls"]:
        return "excel"
    elif ext == ".pdf":
        return "pdf"
    elif ext in [".png", ".jpg", ".jpeg"]:
        return "image"
    else:
        raise ValueError(f"Unsupported file extension: {ext}")


@router.post("/files/upload", response_model=FileUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(..., description="File to upload"),
    project_id: Optional[str] = Form(None, description="Optional project ID for organization"),
):
    """
    Upload and process a data file.

    Supports CSV, Excel, PDF, and image files up to 50MB.
    The file is processed, cleaned, and analyzed with AI-powered insights.

    Args:
        file: Uploaded file (CSV, Excel, PDF, or image)
        project_id: Optional project ID for workspace organization

    Returns:
        FileUploadResponse with file ID, storage URL, and status
    """
    temp_file_path = None

    try:
        # TODO: Replace with actual user authentication in Phase 6
        user_id = "00000000-0000-0000-0000-000000000000"

        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to beginning

        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB",
            )

        # Determine file type
        file_type = get_file_type(file.filename)

        # Save file temporarily
        temp_file_path = Path(tempfile.gettempdir()) / f"{uuid4()}_{file.filename}"
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Reset file pointer for storage upload
        await file.seek(0)

        # Upload to Supabase Storage
        storage_service = StorageService()
        storage_path = await storage_service.upload_file(file, user_id)

        # Insert initial record into database
        file_record = (
            supabase.table("files")
            .insert(
                {
                    "user_id": user_id,
                    "project_id": project_id,
                    "filename": file.filename,
                    "file_type": file_type,
                    "file_size": file_size,
                    "storage_path": storage_path,
                    "status": "processing",
                }
            )
            .execute()
        )

        file_id = file_record.data[0]["id"]

        # Process file
        processor = FileProcessor()

        if file_type == "csv":
            processed_data = processor.process_csv(temp_file_path)
        elif file_type == "excel":
            processed_data = processor.process_excel(temp_file_path)
        elif file_type == "pdf":
            processed_data = processor.process_pdf(temp_file_path)
        elif file_type == "image":
            processed_data = processor.process_image(temp_file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")

        # Clean data if it's tabular (CSV/Excel)
        cleaned_data = {}
        data_schema = {}

        if file_type in ["csv", "excel"]:
            df = processed_data.get("dataframe")
            if df is not None:
                cleaner = DataCleaner()
                cleaned_df = cleaner.clean_dataframe(df)
                data_schema = cleaner.detect_data_schema(cleaned_df)

                # Convert DataFrame to JSON-serializable format
                # Use to_json with ISO date format, then parse back to ensure all types are JSON-safe
                # This handles datetime conversion, NaN -> null, and numpy/pandas scalar normalization
                json_safe_data = json.loads(cleaned_df.to_json(orient="records", date_format="iso"))

                cleaned_data = {
                    "columns": cleaned_df.columns.tolist(),
                    "data": json_safe_data,
                    "row_count": len(cleaned_df),
                }
            else:
                cleaned_data = {"error": "No data extracted"}

        elif file_type == "pdf":
            cleaned_data = {"text": processed_data.get("text", ""), "page_count": processed_data.get("page_count", 0)}

        elif file_type == "image":
            cleaned_data = processed_data.get("extracted_data", {})

        # Generate AI summary
        ai_summary = processor.generate_ai_summary(processed_data, file_type)

        # Insert processed data
        supabase.table("processed_data").insert(
            {"file_id": file_id, "cleaned_data": cleaned_data, "data_schema": data_schema}
        ).execute()

        # Update file record with results
        file_metadata = processed_data.get("summary", {})

        supabase.table("files").update(
            {"status": "completed", "ai_summary": ai_summary, "metadata": file_metadata}
        ).where("id", "eq", file_id).execute()

        # Get storage URL
        storage_url = storage_service.get_file_url(storage_path)

        return FileUploadResponse(
            file_id=UUID(file_id),
            storage_url=storage_url,
            status="completed",
            message="File uploaded and processed successfully",
        )

    except HTTPException:
        raise

    except Exception as e:
        # Update file status to failed if record was created
        try:
            if "file_id" in locals():
                supabase.table("files").update({"status": "failed", "metadata": {"error": str(e)}}).where(
                    "id", "eq", file_id
                ).execute()
        except Exception:
            pass

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Processing failed: {str(e)}")

    finally:
        # Clean up temporary file
        if temp_file_path and temp_file_path.exists():
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass
