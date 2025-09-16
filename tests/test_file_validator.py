import pytest
from fastapi import HTTPException

from app.utils.file_validator import FileValidator
from app.core import constants
from app.core.config import settings


class MockUploadFile:
    """Mock for FastAPI UploadFile"""
    def __init__(self, content: bytes, filename: str, content_type: str):
        self.filename = filename
        self._content = content
        self.content_type = content_type

    async def read(self):
        """Return file content asynchronously"""
        return self._content


@pytest.mark.asyncio
class TestFileValidator:
    async def test_validate_upload_valid_pdf(self):
        """Tests that a valid PDF file is accepted"""
        file = MockUploadFile(b"fakepdf", "test.pdf", "application/pdf")
        content = await FileValidator.validate_upload(file)
        assert content == b"fakepdf"

    async def test_validate_upload_invalid_type(self):
        """Tests that an unsupported file type raises 400"""
        file = MockUploadFile(b"hello", "test.txt", "text/plain")
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_upload(file)
        assert exc_info.value.status_code == 400
        assert "Invalid file type" in str(exc_info.value.detail)

    async def test_validate_upload_empty_file(self):
        """Tests that an empty file raises 400"""
        file = MockUploadFile(b"", "empty.pdf", "application/pdf")
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_upload(file)
        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == constants.STATUS_400_EMPTY_FILE

    async def test_validate_upload_too_large_file(self, monkeypatch):
        """Tests that a file exceeding max size raises 413"""
        monkeypatch.setattr(settings, "max_request_size", 5)  # Override max size for test
        file = MockUploadFile(b"x" * 50, "big.pdf", "application/pdf")
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_upload(file)
        assert exc_info.value.status_code == 413
        assert "File size is too large" in str(exc_info.value.detail)

    async def test_validate_upload_multiple_files(self):
        """Tests that uploading multiple files raises 400"""
        files = [
            MockUploadFile(b"a", "a.pdf", "application/pdf"),
            MockUploadFile(b"b", "b.pdf", "application/pdf"),
        ]
        with pytest.raises(HTTPException) as exc_info:
            await FileValidator.validate_upload(files)
        assert exc_info.value.status_code == 400
        assert "Only one file is allowed" in str(exc_info.value.detail)

    async def test_validate_upload_supported_image(self):
        """Tests that a supported image type is accepted"""
        file = MockUploadFile(b"image", "test.heic", "image/heic")
        content = await FileValidator.validate_upload(file)
        assert content == b"image"
