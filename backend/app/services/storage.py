"""
Supabase Storage service for file management.
Handles file uploads, URL generation, and deletion.
"""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.database import supabase


class StorageService:
    """Handles file storage operations with Supabase Storage."""

    BUCKET_NAME = "files"

    @staticmethod
    async def upload_file(file: UploadFile, user_id: str) -> str:
        """
        Upload a file to Supabase Storage.

        Args:
            file: FastAPI UploadFile object
            user_id: User ID for organizing files

        Returns:
            Storage path of the uploaded file
        """
        try:
            # Generate unique storage path
            file_uuid = uuid4()
            storage_path = f"{user_id}/{file_uuid}/{file.filename}"

            # Read file content
            file_content = await file.read()

            # Reset file pointer for potential reuse
            await file.seek(0)

            # Upload to Supabase Storage
            supabase.storage.from_(StorageService.BUCKET_NAME).upload(
                path=storage_path, file=file_content, file_options={"content-type": file.content_type}
            )

            return storage_path

        except Exception as e:
            raise RuntimeError(f"Failed to upload file to storage: {str(e)}")

    @staticmethod
    def get_file_url(storage_path: str, expires_in: int = 3600) -> str:
        """
        Get a signed URL for a file in Supabase Storage.

        Args:
            storage_path: Path to the file in storage
            expires_in: URL expiration time in seconds (default: 1 hour)

        Returns:
            Signed URL for the file
        """
        try:
            # Create signed URL
            response = supabase.storage.from_(StorageService.BUCKET_NAME).create_signed_url(
                path=storage_path, expires_in=expires_in
            )

            return response["signedURL"]

        except Exception as e:
            raise RuntimeError(f"Failed to generate file URL: {str(e)}")

    @staticmethod
    def delete_file(storage_path: str) -> bool:
        """
        Delete a file from Supabase Storage.

        Args:
            storage_path: Path to the file in storage

        Returns:
            True if deletion was successful
        """
        try:
            supabase.storage.from_(StorageService.BUCKET_NAME).remove([storage_path])
            return True

        except Exception as e:
            raise RuntimeError(f"Failed to delete file from storage: {str(e)}")
