# --- Core Imports ---
import asyncio
from typing import Any, Dict

# --- Third-Party Imports ---
# Azure SDK components for authentication and Document Intelligence client.
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from fastapi import HTTPException

# --- Custom Imports ---
from app.core.config import settings
from app.models.schemas import RenderOptions
from app.services.document_converter import DocumentConverter
from app.services.html_to_pdf_converter import HtmlToPdfConverter
from app.core import constants


class DocumentRenderer:
    """
    Handles document processing by interfacing with Azure Document Intelligence
    and rendering the results to HTML.
    """

    def __init__(self):
        """Initializes the Azure Document Intelligence client and the HTML converter."""
        self.converter = DocumentConverter()
        self.doc_intelligence_client = DocumentIntelligenceClient(
            endpoint=settings.doc_intelligence_endpoint,
            credential=AzureKeyCredential(settings.doc_intelligence_key),
        )

    async def analyze_document(self, file_content: bytes) -> Dict[str, Any]:
        """
        Analyzes document content using Azure Document Intelligence.

        This method sends the file content to the 'prebuilt-layout' model and
        handles potential errors from the Azure service by converting them into
        specific HTTP exceptions.
        """
        try:
            loop = asyncio.get_running_loop()
            
            # Run the blocking Azure SDK call in a separate thread to avoid
            # blocking the main asyncio event loop.
            poller = await loop.run_in_executor(
                None,
                lambda: self.doc_intelligence_client.begin_analyze_document(
                    "prebuilt-layout",
                    file_content,
                    features=[DocumentAnalysisFeature.KEY_VALUE_PAIRS],
                ),
            )
            result = poller.result()
            return result.as_dict()

        except ClientAuthenticationError:
            # This error occurs if the Azure API key or endpoint is incorrect.
            raise HTTPException(
                status_code=401, detail=constants.AZURE_401_AUTH_ERROR_DETAIL
            )
        except HttpResponseError as e:
            # This catches other API errors, like invalid input format (400)
            # or other server-side issues from Azure.
            raise HTTPException(
                status_code=e.status_code,
                detail=constants.AZURE_GENERAL_ERROR_DETAIL.format(e=e.message),
            )
        except Exception as e:
            # A fallback for any other unexpected errors during analysis.
            raise HTTPException(
                status_code=500,
                detail=constants.STATUS_500_ANALYSIS_ERROR_DETAIL.format(e=str(e)),
            )

    async def render_document(self, analysis_payload, options, file_name: str):
        """Renders JSON to both HTML and PDF, returns paths and HTML."""
        # Step 1: Convert JSON to HTML. This internal call also calculates the
        # exact dimensions needed for each page based on the document's content.
        pages_data = self.converter.to_html_pages(analysis_payload, options)

        # Step 2: Convert the HTML pages to a PDF. The pages_data object
        # contains the pre-calculated dimensions, ensuring a perfect fit.
        pdf_converter = HtmlToPdfConverter(pages_data)
        pdf_path = await pdf_converter.convert_to_pdf(file_name)

        # Step 3: Extract just the HTML strings for the final API response.
        html_pages = [page['html'] for page in pages_data]

        return pdf_path, html_pages

