# Pixel Perfect Renderer API

**Version:** 1.0.0\
**Last Updated:** September 1, 2025

---

## 1. Introduction

Welcome to the **Pixel Perfect Renderer API**. This high-performance web
service provides a robust solution for analyzing document layouts and
converting them into pixel-perfect HTML visualizations.

The core functionality is powered by **Azure's Document Intelligence
API** for state-of-the-art layout analysis and a sophisticated internal
rendering engine to reconstruct the document's visual structure with
high fidelity. This service is designed to be **secure, scalable, and
easy to integrate** into larger workflows.

---

## 2. Core Features

- **Document Analysis**: Upload a document (e.g., PDF, image) to the
  `/analyze-document` endpoint to receive a detailed JSON
  representation of its structure, including text, tables, and their
  precise coordinates.
- **Pixel-Perfect HTML Rendering**: Submit the analysis JSON to the
  `/render-json` endpoint to generate a standalone HTML page that
  visually mirrors the original document's layout.
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

1.  **Analysis Step**:\
    The client sends a document file to the `/analyze-document`
    endpoint. The API validates the file, sends it to the Azure Document
    Intelligence service, and returns a structured JSON object
    describing the layout.

2.  **Rendering Step**:\
    The client sends this JSON object to the `/render-json` endpoint.
    The API's internal rendering engine processes the JSON---calculating
    positions, angles, and styles---and returns one or more complete
    HTML pages as a response.

---

## 4. Setup and Installation

### 4.1. Local Development Setup

**Prerequisites:** - Python 3.10+ - An active Azure account with a
Document Intelligence resource.

**Steps:** 1. **Clone the Repository:**
`bash    git clone <your-repository-url>    cd pixel-perfect-renderer`

2.  **Create and Activate a Virtual Environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment Variables:**\
    Create a file named `.env` in the project root directory and
    populate it with your credentials. Use the `.env.example` file as a
    template:

    ```ini
    # .env
    API_KEY="your-secret-api-key" # Generate a secure key, e.g., using uuid.uuid4()
    DOC_INTELLIGENCE_ENDPOINT="https://your-azure-endpoint.cognitiveservices.azure.com/"
    DOC_INTELLIGENCE_KEY="your-azure-document-intelligence-key"
    ```

### 4.2. Docker Deployment

**Prerequisites:** - Docker and Docker Compose installed.

**Steps:** 1. **Clone the Repository:**
`bash    git clone <your-repository-url>    cd pixel-perfect-renderer`

2.  **Configure Environment Variables:**\
    Create the `.env` file in the project root as described in the local
    setup guide. The Docker container will automatically use this file.

3.  **Build and Run with Docker Compose:**

    ```bash
    docker-compose up --build
    ```

    The API will be accessible at **http://localhost:8000**.\
    To run in the background, add the `-d` flag.

---

## 5. Running the Application

### Run Locally (after setup)

Use **uvicorn**, the ASGI server that powers FastAPI.

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag is great for development as it automatically
restarts the server when you change the code.

### Accessing the API Documentation

Once the server is running, navigate to:\
👉 **http://localhost:8000/docs**\
Here you'll find the interactive Swagger UI to test all endpoints.

---

## 6. API Endpoints Guide

### `/api/health`

- **Method:** GET\

- **Description:** Health check to verify service is running.\

- **Response (200 OK):**

  ```json
  {
    "status": true,
    "message": "Service is healthy.",
    "data": null
  }
  ```

### `/api/analyze-document`

- **Method:** POST\
- **Description:** Analyzes a document and returns its layout as
  JSON.\
- **Headers:**\
  `X-API-Key: Your secret API key.`\
- **Body:** `multipart/form-data` with field:
  - `file`: Document to analyze (PDF, JPEG, etc).

**Curl Example:**

```bash
curl -X POST "http://localhost:8000/api/analyze-document"      -H "X-API-Key: your-secret-api-key"      -F "file=@/path/to/your/document.pdf"
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

### `/api/render-json`

- **Method:** POST\
- **Description:** Renders the layout JSON into HTML.\
- **Headers:**\
  `X-API-Key: Your secret API key.`\
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
curl -X POST "http://localhost:8000/api/render-json"      -H "X-API-Key: your-secret-api-key"      -H "Content-Type: application/json"      -d @/path/to/analysis_result.json
```

**Response (200 OK):**

```json
{
  "status": true,
  "message": "Successfully rendered JSON to HTML.",
  "data": {
    "page_count": 1,
    "html_pages": ["<!DOCTYPE html><html><head>..."]
  }
}
```

---

## 7. Testing

This project includes a **pytest test suite** that runs without making
live calls to Azure.

Run tests with:

```bash
pytest
```

## 8. Command-Line Interface (CLI) Helper

For local testing and batch processing, a command-line helper script render_doc.py is provided. It allows you to render an Azure JSON file directly to HTML without running the web server.

Usage
The script takes an input JSON file and an output directory as arguments.

Command:
python render_doc.py --input <path_to_azure.json> --out <output_directory> [options]

Arguments:
--input: (Required) Path to the input Azure JSON file.
--out: (Required) Path to the output directory where HTML files will be saved.
--dpi: (Optional) Dots per inch for rendering. Defaults to 96.
--font: (Optional) CSS font stack to use. Defaults to "Arial, sans-serif".

Example:
python render_doc.py --input "D:\user data\Downloads\default.json" --out output_html_files --dpi 96 --font "Arial, sans-serif"

This command will read the specified JSON file and save the rendered HTML pages (e.g., page_1.html, page_2.html) inside the ./rendered-output directory.
