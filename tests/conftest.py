import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

# This fixture will be used by all tests to make requests to the API
@pytest.fixture(scope="module")
def client() -> Generator[TestClient, None, None]:
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(app) as c:
        yield c

# This fixture provides a valid API key for authenticated endpoints
@pytest.fixture(scope="module")
def valid_api_key() -> dict:
    """
    Returns a dictionary with the valid API key header.
    """
    return {"X-API-Key": settings.api_key}

# This fixture provides an invalid API key to test security
@pytest.fixture(scope="module")
def invalid_api_key() -> dict:
    """
    Returns a dictionary with an invalid API key header.
    """
    return {"X-API-Key": "this-is-a-wrong-key"}