from fastapi import HTTPException, UploadFile
from app.core import constants
from app.core.config import settings

class FileValidator:
    """Utility class to validate uploaded files for /analyze-document."""

    @staticmethod
    async def validate_upload(file: UploadFile) -> bytes:
        """
        Validates that a file is uploaded, non-empty, and within size limits.
        Returns the file content if valid, otherwise raises HTTPException.
        """
        file_content = await file.read()

        if not file_content:
            raise HTTPException(
                status_code=400,
                detail=constants.STATUS_400_EMPTY_FILE
            )

        if len(file_content) > settings.max_request_size:
            raise HTTPException(
                status_code=413,
                detail=constants.STATUS_413_PAYLOAD_TOO_LARGE_DETAIL.format(max_size=settings.max_request_size)
            )

        return file_content
