# --- Core Imports ---
import sys
from pathlib import Path
import io
from unittest.mock import AsyncMock

# --- Add project root to Python path ---
# This allows tests to import modules from the 'app' directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- Third-Party Imports ---
from fastapi.testclient import TestClient

# --- Custom Imports ---
from app.core import constants


# === Test for the /health endpoint ===
def test_health_check(client: TestClient):
    """Tests that the health check endpoint is alive and returns the correct message."""
    response = client.get("/health")
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] is True
    assert json_response["message"] == constants.HEALTH_MSG


# === Tests for the /analyze-document endpoint ===
def test_analyze_document_success(client: TestClient, valid_api_key: dict, mocker):
    """
    Tests successful document analysis by mocking the service layer.
    This ensures the test is fast and doesn't make a real API call.
    """
    # Arrange: Mock the service method to prevent a real network call.
    mock_analysis_result = {"pages": [{"pageNumber": 1}], "content": "mocked"}
    mocker.patch(
        "app.services.renderer.DocumentRenderer.analyze_document",
        new_callable=AsyncMock,
        return_value=mock_analysis_result,
    )

    # Act: Call the endpoint with a dummy file.
    response = client.post(
        "/analyze-document",
        files={"file": ("test.pdf", constants.TEST_DUMMY_FILE_CONTENT, constants.TEST_PDF_CONTENT_TYPE)},
        headers=valid_api_key,
    )

    # Assert: Check for a successful response and correct data structure.
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] is True
    assert "azure_json" in json_response["data"]
    assert json_response["data"]["azure_json"] == mock_analysis_result


def test_analyze_document_missing_file(client: TestClient, valid_api_key: dict):
    """Tests that the endpoint returns a 422 error when no file is uploaded."""
    response = client.post("/analyze-document", headers=valid_api_key)
    assert response.status_code == 422
    json_response = response.json()
    assert json_response["status"] is False
    # FastAPI's default validation for a missing file will trigger our generic
    # 422 handler message. This is the expected behavior.
    assert json_response["message"] == constants.STATUS_422_VALIDATION_ERROR_DETAIL


def test_analyze_document_empty_file(client: TestClient, valid_api_key: dict):
    """Tests that the endpoint returns a 400 error for an empty file."""
    file = ("empty.pdf", io.BytesIO(b""), constants.TEST_PDF_CONTENT_TYPE)
    response = client.post("/analyze-document", files={"file": file}, headers=valid_api_key)
    assert response.status_code == 400
    json_response = response.json()
    assert json_response["message"] == constants.STATUS_400_EMPTY_FILE


def test_analyze_document_file_too_large(client: TestClient, valid_api_key: dict, monkeypatch):
    """Tests that the endpoint returns a 413 error for an oversized file."""
    from app.core import config
    monkeypatch.setattr(config.settings, "max_request_size", 10)

    file = ("big.pdf", io.BytesIO(b"x" * 50), constants.TEST_PDF_CONTENT_TYPE)
    response = client.post("/analyze-document", files={"file": file}, headers=valid_api_key)

    assert response.status_code == 413
    json_response = response.json()
    assert "File size is too large" in json_response["message"]


def test_analyze_document_invalid_key(client: TestClient, invalid_api_key: dict):
    """Tests that the endpoint fails with a 403 Forbidden error for an invalid API key."""
    file = ("test.pdf", constants.TEST_DUMMY_FILE_CONTENT, constants.TEST_PDF_CONTENT_TYPE)
    response = client.post("/analyze-document", files={"file": file}, headers=invalid_api_key)
    assert response.status_code == 403
    assert response.json()["message"] == constants.STATUS_403_FORBIDDEN_DETAIL


# === Tests for the /render-json endpoint ===
def test_render_json_success(client: TestClient, valid_api_key: dict):
    """Tests successful rendering with a valid JSON payload."""
    payload = {
        "azure_json": {
            "pages": [{"pageNumber": 1, "paragraphs": [{"role": "title", "content": "Test Title"}]}]
        },
        "options": {"dpi": 96, "mode": "word", "font_stack": "Arial"}
    }

    response = client.post("/render-json", json=payload, headers=valid_api_key)
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] is True
    assert json_response["data"]["page_count"] == 1

def test_render_json_invalid_key(client: TestClient, invalid_api_key: dict):
    """Tests that the endpoint fails with a 403 Forbidden error for an invalid API key."""
    payload = {"azure_json": {"pages": []}, "options": {}}
    response = client.post("/render-json", json=payload, headers=invalid_api_key)
    assert response.status_code == 403
    assert response.json()["message"] == constants.STATUS_403_FORBIDDEN_DETAIL


def test_render_json_bad_payload(client: TestClient, valid_api_key: dict):
    """Tests for a 422 error when the payload is missing required fields."""
    payload = {"azure_json": {"pages": []}}
    response = client.post("/render-json", json=payload, headers=valid_api_key)
    assert response.status_code == 422

