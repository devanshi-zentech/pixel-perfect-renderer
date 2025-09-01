from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    HTTPException,
    Request,
    Security,
    UploadFile,
)
from fastapi.security.api_key import APIKeyHeader

from app.core.config import settings
from app.core import constants
from app.core.limiter import limiter
from app.models.schemas import (
    APIResponse,
    AzureJson,
    RenderRequest,
    RenderResponse,
)
from app.services.renderer import DocumentRenderer
from app.utils.file_validator import FileValidator

class RendererAPI:
    def __init__(self, service: DocumentRenderer):
        self.router = APIRouter()
        self.service = service
        self.api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
        self.file_validator = FileValidator()

        # register routes
        self._add_routes()

    async def get_api_key(self, api_key_header: str = Security(APIKeyHeader(name="X-API-Key", auto_error=False))):
        if api_key_header == settings.api_key:
            return api_key_header
        else:
            raise HTTPException(status_code=403, detail=constants.STATUS_403_FORBIDDEN_DETAIL)

    def _add_routes(self):
        """Attach all endpoints to router"""

        @self.router.post("/analyze-document", response_model=APIResponse[AzureJson])
        @limiter.limit(settings.rate_limit)
        async def analyze_document_endpoint(
            request: Request,
            file: UploadFile = File(...),
            api_key: str = Depends(self.get_api_key),
        ):
            try:
                file_content = await self.file_validator.validate_upload(file)
                # Call the service for document analysis
                analysis_result = await self.service.analyze_document(file_content)
                return {
                    "status": True,
                    "message": constants.ANALYZE_SUCCESS_MSG,
                    "data": AzureJson(azure_json=analysis_result),
                }
            except HTTPException:
                raise  
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=constants.STATUS_500_ANALYSIS_ERROR_DETAIL.format(e=str(e)),
                )

        @self.router.post("/render-json", response_model=APIResponse[RenderResponse])
        @limiter.limit(settings.rate_limit)
        async def render_json_endpoint(
            request: Request,
            payload: RenderRequest = Body(...),
            api_key: str = Depends(self.get_api_key),
        ):
            try:
                html_pages = self.service.render_html(payload.azure_json, payload.options)
                render_data = RenderResponse(page_count=len(html_pages), html_pages=html_pages)
                return {
                    "status": True,
                    "message": constants.RENDER_SUCCESS_MSG,
                    "data": render_data,
                }
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=str(ve))
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=constants.STATUS_500_RENDERING_ERROR_DETAIL.format(e=str(e)),
                )

        @self.router.get("/health", response_model=APIResponse)
        async def health_check():
            return {
                "status": True,
                "message": constants.HEALTH_MSG,
            }

    def get_router(self) -> APIRouter:
        return self.router

# Instantiate API + router for main.py
renderer_api = RendererAPI(service=DocumentRenderer())
router = renderer_api.get_router()
