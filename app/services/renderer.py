# --- Core Imports ---
import asyncio
import os
from typing import Any, Dict
from dotenv import load_dotenv

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

    async def render_document(self, analysis_payload, options):
        """Renders JSON to HTML and uploads PDF to Azure Blob Storage."""
        pages_data = self.converter.to_html_pages(analysis_payload, options)

        pdf_converter = HtmlToPdfConverter(pages_data)
        local_pdf_path = await pdf_converter.convert_to_pdf("doc.pdf")
        blob_name = os.path.basename(local_pdf_path)
        blob_url = self.upload_pdf_to_blob(local_pdf_path)
        print(blob_url)
        html_pages = [page["html"] for page in pages_data]
        return blob_url, html_pages

    def upload_pdf_to_blob(self, file_path: str) -> str:
        """
        Uploads a PDF file to Azure Blob Storage using a blob URL with an SAS token.

        This function assumes the BLOB_URL environment variable contains the

        Args:
            file_path (str): The local path to the PDF file.
        Returns:
            str: The full URL of the uploaded blob.
        """
        load_dotenv()
        try:
            # 1. Retrieve the base URL with SAS token from environment variables.
            base_url= os.getenv("BLOB_URL")

            if not base_url:
                raise ValueError("BLOB_URL environment variable is not set.")

            # 2. Get the filename from the provided file path.
            blob_name = os.path.basename(file_path)

            # 3. Separate the base URL from the SAS token.
            #    The SAS token starts with a '?'.
            base_url, sas_token = base_url.split("?", 1)

            # 4. Correctly construct the full URL by appending the blob name
            #    to the path part of the URL, and then re-adding the SAS token.
            full_blob_url = f"{base_url}/{blob_name}?{sas_token}"
            print(full_blob_url)

            # 5. Create a BlobClient object using the correct URL.
            blob_client = BlobClient.from_blob_url(full_blob_url)

            print(f"Uploading '{blob_name}' to '{full_blob_url}'...")

            with open(file_path, "rb") as data:
                blob_client.upload_blob(data, overwrite=True)

            print("Upload successful.")

            return full_blob_url

        except FileNotFoundError:
            raise FileNotFoundError(f"The file at '{file_path}' was not found.")
        except ValueError as ve:
            # This will catch errors if the BLOB_URL is not in the expected format (missing '?').
            raise ValueError(
                f"BLOB_URL format is incorrect: {ve}. It should be a container URL with a SAS token appended.")
        except Exception as e:
            # This will now be a more specific error related to the SAS token or URL
            raise RuntimeError(f"An error occurred during blob upload: {e}")