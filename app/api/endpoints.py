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
from fastapi.responses import RedirectResponse
from fastapi.security.api_key import APIKeyHeader
from starlette.responses import RedirectResponse

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
        # Add a tag to group related endpoints in the documentation
        self.router = APIRouter(tags=["Document Processing"])
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
        @self.router.get("/",include_in_schema=False)
        async def get_root():
            return RedirectResponse(url="/health")
        @self.router.get("/", include_in_schema=False)
        async def root():
            return RedirectResponse(url="/health")
        @self.router.post(
            "/analyze-document",
            response_model=APIResponse[AzureJson],
            summary="Step 1: Analyze a Document",
            description=(
                "Upload a file (e.g., PDF, PNG, JPG, JPEG) to be analyzed by the Document Intelligence engine. "
                "The response contains a structured `azure_json` object representing the document's content and layout. "
                "**The `data` object from this response should be used as the `azure_json` value in the 'Render JSON' request.**"
            )
        )
        @limiter.limit(settings.rate_limit)
        async def analyze_document_endpoint(
            request: Request,
            file: UploadFile = File(..., description="The document file to be analyzed."),
            api_key: str = Depends(self.get_api_key),
        ):
            """
            SAMPLE INPUT FOR ENDPOINT:
            Upload a file (PDF, PNG, JPG, JPEG) as 'file' form-data.
            """
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

        @self.router.post(
            "/render-json",
            response_model=APIResponse[RenderResponse],
            summary="Step 2: Render JSON to HTML",
            description=(
                """
                    Takes Azure JSON and renders both HTML pages and a downloadable PDF file.
                    """
            )
        )
        @limiter.limit(settings.rate_limit)
        async def render_json_endpoint(
            request: Request,
            payload: RenderRequest = Body(..., description="The JSON payload containing the analysis result and rendering options."),
            api_key: str = Depends(self.get_api_key),
        ):
            """
            SAMPLE INPUT FOR ENDPOINTS:
            {
            "azure_json": {
                "pages": [
                    { "number": 1, "content": "Sample text", "layout": {...} }
                ]
                },
                "options": {
                    "mode": "words",
                    "font_stack": "Arial, Helvetica, sans-serif"
                    "dpi": 96
                }
            }"""
            try:
                blob_url, html_pages = await self.service.render_document(payload.azure_json, payload.options)

                render_data = RenderResponse(
                    file_path=blob_url,
                    page_count=len(html_pages),
                    html_pages=html_pages
                )
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

        @self.router.get(
            "/health",
            response_model=APIResponse,
            summary="Health Check",
            description="A simple endpoint to verify that the API service is running and healthy. No authentication is required."
        )
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
