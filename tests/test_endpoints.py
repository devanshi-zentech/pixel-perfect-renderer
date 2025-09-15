# --- Core Imports ---
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

# --- Add project root to Python path ---
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# --- Third-Party Imports ---
from fastapi.testclient import TestClient

# --- Custom Imports ---
from app.core import constants


class TestEndpoints:
    # === Test for the /health endpoint ===
    def test_health_check(self, client: TestClient):
        """Tests that the health check endpoint is alive and returns the correct message."""
        response = client.get("/health")
        assert response.status_code == 200
        json_response = response.json()
        assert json_response["status"] is True
        assert json_response["message"] == constants.HEALTH_MSG

    # === Tests for the /analyze-document endpoint ===
    def test_analyze_document_success(self, client: TestClient, valid_api_key: dict):
        mock_analysis_result = {"pages": [{"pageNumber": 1}], "content": "mocked"}

        with patch("app.services.renderer.DocumentRenderer.analyze_document", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = mock_analysis_result

            response = client.post(
                "/analyze-document",
                files={"file": ("test.pdf", constants.TEST_DUMMY_FILE_CONTENT, constants.TEST_PDF_CONTENT_TYPE)},
                headers=valid_api_key,
            )

        assert response.status_code == 200
        json_response = response.json()
        assert json_response["status"] is True
        assert "azure_json" in json_response["data"]
        assert json_response["data"]["azure_json"] == mock_analysis_result

    def test_analyze_document_invalid_key(self, client: TestClient, invalid_api_key: dict):
        """Tests that the endpoint fails with a 403 Forbidden error for an invalid API key."""
        file = ("test.pdf", constants.TEST_DUMMY_FILE_CONTENT, constants.TEST_PDF_CONTENT_TYPE)
        response = client.post("/analyze-document", files={"file": file}, headers=invalid_api_key)
        assert response.status_code == 403
        assert response.json()["message"] == constants.STATUS_403_FORBIDDEN_DETAIL

    # === Tests for the /render-json endpoint ===
    def test_render_json_success(self, client: TestClient, valid_api_key: dict):
        """Tests that /render-json successfully converts valid Azure JSON to PDF and returns expected structure"""
        payload = {
            "azure_json": {"pages": [{"pageNumber": 1, "paragraphs": [{"role": "title", "content": "Test Title"}]}]},
            "options": {"dpi": 96, "mode": "word", "font_stack": "Arial"}
        }

        # Mock PDF conversion to return valid PDF bytes
        with patch("app.services.html_to_pdf_converter.HtmlToPdfConverter.convert_to_pdf", new_callable=AsyncMock) as mock_convert:
            mock_convert.return_value = b"%PDF-1.4 FAKE PDF BYTES%"

            response = client.post("/render-json", json=payload, headers=valid_api_key)
            print("RESPOSNE: ", response.json())

        assert response.status_code == 200
        json_response = response.json()
        assert json_response["status"] is True
        assert json_response["data"]["page_count"] >= 1
        assert isinstance(json_response["data"]["html_pages"], list)

    def test_render_json_invalid_key(self, client: TestClient, invalid_api_key: dict):
        """Tests that the endpoint fails with a 403 Forbidden error for an invalid API key."""
        payload = {"azure_json": {"pages": []}, "options": {}}
        response = client.post("/render-json", json=payload, headers=invalid_api_key)
        assert response.status_code == 403
        assert response.json()["message"] == constants.STATUS_403_FORBIDDEN_DETAIL

    def test_render_json_bad_payload(self, client: TestClient, valid_api_key: dict):
        """Tests for a 422 error when the payload is missing required fields."""
        payload = {"azure_json": {"pages": []}}
        response = client.post("/render-json", json=payload, headers=valid_api_key)
        assert response.status_code == 422
    
    def test_analyze_document_rate_limit(self, client: TestClient, valid_api_key: dict):
        """
        Tests that the /analyze-document endpoint enforces rate limiting.
        Rate limit is set to 10 requests per minute.
        """

        file = ("test.pdf", constants.TEST_DUMMY_FILE_CONTENT, constants.TEST_PDF_CONTENT_TYPE)

        # Mock the Azure Document Intelligence call so we don't hit the real API
        with patch("app.services.renderer.DocumentRenderer.analyze_document", new_callable=AsyncMock) as mock_method:
            mock_method.return_value = {"pages": [{"pageNumber": 1}], "content": "mocked"}

            # Make 9 requests – should all succeed
            for i in range(9):
                response = client.post("/analyze-document", files={"file": file}, headers=valid_api_key)
                assert response.status_code == 200

            # 10th request – should hit the rate limit
            response = client.post("/analyze-document", files={"file": file}, headers=valid_api_key)
            assert response.status_code == 429
            assert "rate limit exceeded" in response.text.lower()