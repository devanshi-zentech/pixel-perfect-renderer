from pydantic_settings import BaseSettings, SettingsConfigDict
from app.core import constants


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    project_name: str = constants.PROJECT_TITLE
    project_version: str = constants.PROJECT_VERSION
    api_key: str
    rate_limit: str
    log_path: str
    cors_origins: list[str] = ["https://api.tranwise.com/AddOCRFile",
                               "https://stage.api.tranwise.com/AddOCRFile", "*"]  # CRM's Origin
    max_request_size: int
    doc_intelligence_endpoint: str
    doc_intelligence_key: str

    blob_url: str
    azure_storage_container_name: str


settings = Settings()
