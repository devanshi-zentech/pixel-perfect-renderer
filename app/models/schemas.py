from pydantic import BaseModel, Field
from typing import Generic, Optional, TypeVar, Dict, Any, List
from app.core import constants
DataType = TypeVar("DataType")


# ----- Models for /render-json output -----
class RenderResponse(BaseModel):
    """Response model for the /render-json endpoint."""
    file_path: Optional[str] = None
    page_count: Optional[int] = None
    html_pages: Optional[List[str]] = None

# ----- Models for /analyze-and-render-docx output -----
class DocxRenderResponse(BaseModel):
    """Response model for the /analyze-and-render-docx endpoint."""
    download_url: str = Field(..., description="Azure Blob Storage URL for the generated DOCX file")
    file_name: str = Field(..., description="Name of the generated DOCX file")
    message: str = Field(..., description="Success message")

# ----- Models for rendering options -----
class RenderOptions(BaseModel):
    """Rendering configuration options for HTML output."""
    dpi: int = Field(constants.DEFAULT_DPI, description="Dots per inch for rendering")
    mode: str = Field(constants.DEFAULT_RENDER_MODE, description="Rendering mode: 'word' or 'line'")
    font_stack: str = Field(
        constants.DEFAULT_FONT_STACK,
        description="CSS font stack to use",
    )


# ----- Models for /analyze-document output -----
class AzureJson(BaseModel):
    """Raw Azure Document Intelligence JSON result."""
    azure_json: Dict[str, Any]


# ----- Models for /render-json input -----
class RenderRequest(BaseModel):
    """Request body for the /render-json endpoint (JSON + rendering options)."""
    azure_json: Dict[str, Any]
    options: RenderOptions


# ----- Generic API Response Wrapper -----
class APIResponse(BaseModel, Generic[DataType]):
    """Generic API response model used across all endpoints."""
    status: bool = True
    message: str
    data: Optional[DataType] = None
