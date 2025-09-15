import pytest
from typing import Generator
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.browser_manager import browser_manager

@pytest.fixture(scope="function")
async def fresh_browser():
    """Each test starts with a fresh Playwright browser instance."""
    browser_manager.browser = None
    yield
    if browser_manager.browser:
        await browser_manager.stop()
    browser_manager.browser = None


@pytest.fixture(scope="module")
async def browser_per_module():
    """Launch one Playwright browser for all tests in a module."""
    browser_manager.browser = None
    browser = await browser_manager.get_browser()
    yield browser
    if browser_manager.browser:
        await browser_manager.stop()
    browser_manager.browser = None


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
