# Pixel Perfect Renderer API

**Version:** 1.0.0
**Last Updated:** September 1, 2025

---

## 1. Introduction

Welcome to the **Pixel Perfect Renderer API**. This high-performance web
service provides a robust solution for analyzing document layouts and
converting them into pixel-perfect HTML and HTML to PDF.

The core functionality is powered by Azure's Document Intelligence API for state-of-the-art layout analysis, a sophisticated internal rendering engine to reconstruct the document's visual structure with high fidelity, and Azure Blob Storage for secure and scalable storage of the generated PDFs.

This service is designed to be secure, scalable, and easy to integrate into larger workflows.
---

## 2. Core Features

- **Document Analysis**: Upload a document (e.g., PDF, image) to the
  `/analyze-document` endpoint to receive a detailed JSON
  representation of its structure, including text, tables, and their
  precise coordinates.
- **Pixel-Perfect HTML Rendering**: Submit the analysis JSON to the
  `/render-json` endpoint to generate
  A standalone HTML page that visually mirrors the original document.
  A PDF file, securely stored in Azure Blob Storage, with a downloadable file path returned in the response.
  Metadata including page count and the generated HTML content.
- **Robust Security**: Implements API key authentication, rate
  limiting, and configurable CORS policies.
- **Enterprise-Grade Logging**: Generates structured JSON logs with
  unique request IDs for easy tracing and monitoring.
- **Containerized Deployment**: Includes a complete Docker setup for
  consistent and straightforward deployment in any environment.
- **Interactive API Docs**: Comes with self-generating Swagger UI for
  easy exploration and testing of the API endpoints.

---

## 3. Architecture & Workflow

The application is built using the **FastAPI** framework and follows a
clean, modular architecture. The typical workflow is a two-step process:

1.  **Analysis Step**:    The client sends a document file to the `/analyze-document`
    endpoint. The API validates the file, sends it to the Azure Document
    Intelligence service, and returns a structured JSON object
    describing the layout.

2.  **Rendering Step**:    The client sends this JSON object to the `/render-json` endpoint.
    The API’s internal rendering engine processes the JSON—calculating
    positions, angles, and styles—and generates:
    A pixel-perfect HTML representation of the document.
    A PDF file stored securely in Azure Blob Storage, with a
    downloadable file path included in the response.
    Metadata such as page count and the generated HTML content.

---

## 4. Setup and Installation

### 4.1. Local Development Setup

**Prerequisites:** 
- Python 3.10+ 
- An active Azure account with a
- **Document Intelligence** resource  
  - **Blob Storage** resource (for storing generated PDFs)

**Steps:** 

1. **Clone the Repository:**
```bash
git clone <your-repository-url>
```

2.  **Create and Activate a Virtual Environment:**

**Windows**
```powershell
python -m venv venv
venv\Scripts\activate
```

**Linux / MacOS**
```bash
python3 -m venv venv
source venv/bin/activate
```

3.  **Install Dependencies:**

```bash
pip install -r requirements.txt
```

4.  **Install Playwright Browsers**:     Playwright requires browser binaries to be downloaded. This is a crucial one-time setup step.

```bash
playwright install
```

5.  **Configure Environment Variables:**    You can either download the pre-configured project.env file from the link below, rename it to .env, and place it in the project root directory:

Download project.env : https://utslanguagetranslator.blob.core.windows.net/sensitive-details/project.env?sp=racwdl&st=2025-09-15T12:34:02Z&se=2026-09-15T20:49:02Z&spr=https&sv=2024-11-04&sr=c&sig=8B0E3KHH25ldW%2B0V71%2BZenzgns3JFKiq75FIPns6WkI%3D

or create a new .env file manually in the project root directory and populate it with your credentials:

```ini
# .env
API_KEY="your-secret-api-key" # Generate a secure key, Use this key in API Headers as "X-API-KEY"
DOC_INTELLIGENCE_ENDPOINT="https://your-azure-endpoint.cognitiveservices.azure.com/"
DOC_INTELLIGENCE_KEY="your-azure-document-intelligence-key"
RATE_LIMIT="your-rate-limit-per-minute" # Format Ex: "10/minute", "15/minute"
MAX_REQUEST_SIZE="your-max-request-size-in-bytes" #  Format Ex: "31457280" in bytes
BLOB_URL="your-azure-blob-storage-url"
AZURE_STORAGE_CONTAINER_NAME="your-container-name"
```

### 4.2. Docker Deployment

**Prerequisites:** 
- Docker and Docker Compose installed.

**Steps:** 

1. **Clone the Repository:**
```bash
git clone <your-repository-url>
```

2.  **Configure Environment Variables:**    Create the `.env` file in the project root as described in the local
    setup guide. The Docker container will automatically use this file.

3.  **Build and Run with Docker Compose:**

```bash
docker-compose up --build
```

The API will be accessible at **http://localhost:8000**.
To run in the background, add the `-d` flag.

---

## 5. Running the Application

### Run Locally (after setup)

Use **uvicorn**, the ASGI server that powers FastAPI.

**Windows**
```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Linux / MacOS**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Important Note on --reload

While FastAPI supports the --reload flag for auto-restarting the server during development:
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

It is not recommended in this project.
Here’s why:
  - FastAPI restarts the application process instantly on code changes.
  - Playwright’s Chromium browser instance, however, does not refresh as quickly and can remain in a stale state.
  - This leads to inconsistent rendering, Browser.close / NoneType errors.
```
### Accessing the API Documentation

Once the server is running, navigate to:
**http://localhost:8000/docs**
Here you'll find the interactive Swagger UI to test all endpoints.

---

## 6. API Endpoints Guide

### `/health`

- **Method:** GET
- **Description:** Health check to verify service is running.
- **Response (200 OK):**

```json
{
  "status": true,
  "message": "Service is healthy.",
  "data": null
}
```

### `/analyze-document`

- **Method:** POST
- **Description:** Analyzes a document and returns its layout as JSON.
- **Headers:**  `X-API-Key: Your secret API key.`
- **Body:** `multipart/form-data` with field:
  - `file`: Document to analyze (PDF, JPEG, PNG, JPG, etc).

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/analyze-document" \
     -H "X-API-Key: your-secret-api-key" \
     -F "file=@/path/to/your/document.pdf"
```

**Response (200 OK):**
```json
{
  "status": true,
  "message": "Document analysis was successful.",
  "data": {
    "azure_json": {
      "apiVersion": "2024-11-30",
      "modelId": "prebuilt-layout",
      "content": "...",
      "pages": [...]
    }
  }
}
```

### `/render-json`

- **Method:** POST
- **Description:** Renders the layout JSON into HTML and PDF.
- **Headers:**  `X-API-Key: Your secret API key.`
- **Body:** Raw JSON payload.

**Example JSON body:**
```json
{
  "azure_json": {
    "apiVersion": "...",
    "pages": [...]
  },
  "options": {
    "dpi": 96,
    "mode": "word",
    "font_stack": "Arial, sans-serif"
  }
}
```

**Curl Example:**
```bash
curl -X POST "http://localhost:8000/render-json" \
     -H "X-API-Key: your-secret-api-key" \
     -H "Content-Type: application/json" \
     -d @/path/to/analysis_result.json
```

**Response (200 OK):**
```json
{
  "status": true,
  "message": "Successfully rendered JSON to HTML and PDF.",
  "data": {
    "file_path": "https://<your-azure-blob-container>/rendered/abcd1234.pdf",
    "page_count": 1,
    "html_pages": ["<!DOCTYPE html><html><head>..."]
  }
}
```

**Important Note for Client/Receiver Side:**
  - file_path is a downloadable Azure Blob Storage URL pointing to the generated PDF.
  - html_pages is an array of raw HTML strings wrapped inside JSON.
    When consuming this response, you must call JSON.parse (or equivalent) to correctly deserialize the array.
    Some clients may show escaped characters like `\/` until parsed. After parsing, you’ll get clean HTML you can directly render or save to a file.

---

## 7. Testing

This project includes a **pytest test suite** that runs without making
live calls to Azure.

Run tests with:

```bash
pytest -v
```

---

## 8. Command-Line Interface (CLI) Helper

For local testing and batch processing, a command-line helper script `render_doc.py` is provided.  
It allows you to render an Azure JSON file directly to HTML and PDF without running the web server.

**Usage:**  
The script takes an input JSON file and an output directory as arguments.

**Windows**
```powershell
python -m app.services.render_doc --input "<path-to-json>" --out output_files --mode words --dpi 96 --font "Arial, sans-serif"

**Linux / MacOS**
```bash
python -m app.services.render_doc --input "<path-to-json>" --out output_files --mode words --dpi 96 --font "Arial, sans-serif"
```

This command will read the specified JSON file and save the rendered HTML pages (e.g., page_1.html, page_2.html) and a single combined PDF inside the `./output_files` directory.
