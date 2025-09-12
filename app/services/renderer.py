# --- Core Imports ---
import asyncio
from typing import Any, Dict
import uuid
from datetime import datetime
import uuid

# --- Third-Party Imports ---
# Azure SDK components for authentication and Document Intelligence client.
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.storage.blob import BlobClient
from fastapi import HTTPException

# --- Custom Imports ---
from app.core.config import settings
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
                    constants.AZURE_ANALYZE_MODEL,
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

    async def render_document(self, analysis_payload, options):
        """Renders JSON to HTML and uploads PDF to Azure Blob Storage."""
        pages_data = self.converter.to_html_pages(analysis_payload, options)

        pdf_converter = HtmlToPdfConverter(pages_data)
        pdf_bytes = await pdf_converter.convert_to_pdf()

        # Generate unique suffix with timestamp + short uuid
        unique_suffix = datetime.now().strftime(constants.BLOB_SUFFIX_TIMESTAMP_FORMAT) + "_" + uuid.uuid4().hex[:constants.BLOB_SUFFIX_UUID_LENGTH]
        blob_name = f"doc_{unique_suffix}.pdf"

        blob_url = self.upload_pdf_bytes_to_blob(blob_name, pdf_bytes)

        html_pages = [page["html"] for page in pages_data]
        return blob_url, html_pages


    def upload_pdf_bytes_to_blob(self, blob_name: str, pdf_bytes: bytes) -> str:
        """
        Uploads PDF bytes directly to Azure Blob Storage.
        """
        try:
            base_url = settings.blob_url

            base_url, sas_token = base_url.split("?", 1)
            full_blob_url = f"{base_url}/{blob_name}?{sas_token}"

            blob_client = BlobClient.from_blob_url(full_blob_url)

            blob_client.upload_blob(pdf_bytes, overwrite=True)
            return full_blob_url

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=constants.STATUS_500_BLOB_UPLOAD_ERROR_DETAIL.format(e=str(e)),
            )
        