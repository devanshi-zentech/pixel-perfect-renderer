from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core import constants

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    project_name: str = constants.PROJECT_TITLE
    project_version: str = constants.PROJECT_VERSION
    api_key: str
    rate_limit: str = constants.API_RATE_LIMIT
    cors_origins: list[str] = ["*"] # CRM's Origin
    max_request_size: int = constants.API_MAX_REQUEST_SIZE
    doc_intelligence_endpoint: str
    doc_intelligence_key: str

settings = Settings()
