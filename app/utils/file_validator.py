from fastapi import HTTPException, UploadFile
from typing import List
from app.core import constants
from app.core.config import settings


class FileValidator:
    """Utility class to validate uploaded files for /analyze-document."""

    allowed_mime_types: List[str] = [
        "application/pdf",
        "image/jpeg",
        "image/png",
        "image/jpg",
        "image/gif",
        "image/bmp",
        "image/webp",
        "image/tiff",
        "image/heif",
        "image/heic",
    ]

    @staticmethod
    async def validate_upload(file: UploadFile) -> bytes:
        """
        Validates the uploaded file:
        - Only one file (not a list)
        - Must be a supported type (PDF or image)
        - Non-empty
        - Not exceeding size limit

        Returns:
            file_content (bytes): The content of the file if valid.
        """
        # Ensure it's not a list
        if isinstance(file, list):
            raise HTTPException(
                status_code=400,
                detail="Only one file is allowed per request.",
            )

        # Validate file type
        if file.content_type not in FileValidator.allowed_mime_types:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type: Only PDF and image files are allowed.",
            )

        # Read file content
        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail=constants.STATUS_400_EMPTY_FILE
            )

        if len(file_content) > settings.max_request_size:
            raise HTTPException(
                status_code=413,
                detail=constants.STATUS_413_PAYLOAD_TOO_LARGE_DETAIL.format(
                    max_size=settings.max_request_size
                )
            )

        return file_content
