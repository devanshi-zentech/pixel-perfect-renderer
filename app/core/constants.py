PROJECT_TITLE = "Pixel Perfect Renderer"
PROJECT_VERSION = "1.0.0"
# --- API General ---
API_KEY_HEADER = "X-API-Key"
API_RATE_LIMIT = "10/minute"
API_MAX_REQUEST_SIZE = 30 * 1024 * 1024  # 30MB
HEALTH_MSG = "Service is healthy."
WELCOME_MSG = "Welcome to the Pixel Perfect Renderer API!"

# --- HTTP Status Messages ---
STATUS_403_FORBIDDEN_DETAIL = "Could not validate credentials"
STATUS_400_EMPTY_FILE = "No file content provided. Please upload a non-empty file."
STATUS_413_PAYLOAD_TOO_LARGE_DETAIL = "File size is too large. The limit is {max_size} bytes."
STATUS_422_VALIDATION_ERROR_DETAIL = "Field required"
STATUS_500_ANALYSIS_ERROR_DETAIL = "An unexpected error occurred during document analysis: {e}"
STATUS_500_RENDERING_ERROR_DETAIL = "An unexpected error occurred during rendering: {e}"
STATUS_500_DOCX_RENDERING_ERROR_DETAIL = "An unexpected error occurred during DOCX rendering: {e}"
STATUS_500_BLOB_UPLOAD_ERROR_DETAIL = "An unexpected error occurred during Blob upload: {e}"

AZURE_401_AUTH_ERROR_DETAIL = "Azure authentication failed. Check your Document Intelligence API key and endpoint."
AZURE_GENERAL_ERROR_DETAIL = "An error occurred with the Azure Document Intelligence service: {e}"
AZURE_ANALYZE_MODEL="prebuilt-layout"
# --- Endpoint Messages ---
ANALYZE_SUCCESS_MSG = "Document analysis was successful."
RENDER_SUCCESS_MSG = "Successfully rendered JSON to PDF."
DOCX_RENDER_SUCCESS_MSG = "Successfully analyzed document and generated DOCX file."

# --- Logging ---
LOG_FORMAT = "{time} {level} {extra[request_id]} {message}"

# --- Document Rendering ---
DEFAULT_FONT_STACK = "Arial, sans-serif"
DEFAULT_RENDER_MODE = "words"
DEFAULT_DPI = 96
HTML_VISUALIZATION_CSS = """
body {{ font-family: {font_style}; background: #f0f0f0; }}
.page {{ margin: 0 auto; border: 1px solid #ccc; box-shadow: 0 0 10px rgba(0,0,0,0.1); position: relative; overflow: hidden; background: white; }}
.table-container table {{ border-collapse: collapse; width: 100%; }}
.table-container th, .table-container td {{ border: 1px solid black; padding: 4px; text-align: center; font-size: 10px; position: relative; overflow: hidden; }}
"""
SCALE_FACTOR = 1000

DEFAULT_PAGE_WIDTH = 8.5
DEFAULT_PAGE_HEIGHT = 11
DEFAULT_PAGE_WIDTH_PIXEL = (8.5*96)
DEFAULT_PAGE_HEIGHT_PIXEL = (11*96)
DEFAULT_PAGE_ANGLE = 0


CONTAINER_STYLE =(
    '<div class="page" style="width:{page_width_scaled:.2f}px; '
    'height:{page_height_scaled:.2f}px; transform:rotate({page_angle}deg);">'
    '{content}</div>')

RENDER_WORD_STYLE = (
        'position: absolute; left: {left:.2f}px; top: {top:.2f}px; '
        'transform-origin: top left; transform: rotate({angle_deg:.2f}deg); '
        'font-size: {font_size:.2f}px; line-height: {word_height:.2f}px; '
        'white-space: nowrap; color: rgba(0,0,0,0.9);'
    )


RENDER_TABLE_WORD_STYLE =(
                    'position: absolute; left: {w_left_position_in_pixels:.2f}px; top: {w_top_position_in_pixels:.2f}px; '
                    'transform-origin: top left; transform: rotate({angle:.2f}deg); '
                    'font-size: {font_size_in_pixels:.2f}px; line-height: {word_height_in_pixels:.2f}px; white-space: nowrap;'
                )

RENDER_TABLE_STYLE = '<div class="table-container" style="position: absolute; left: {left:.2f}px; top: {top:.2f}px; width: {width:.2f}px;"><table border="1">'

CELL_STYLE = (
                'position: relative; width: {cell_width_px:.2f}px; height: {cell_height_px:.2f}px; '
                'padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; '
                'text-align: left; border: 1px solid black;'
            )

EMPTY_CELL_STYLE = (
                'position: relative; min-width: {cell_width_px:.2f}px; min-height: {cell_height_px:.2f}px; '
                'padding: 4px; box-sizing: border-box; overflow: hidden; vertical-align: top; '
                'text-align: left; border: 1px solid black;'
            )

CELL_HTML = '<div style="width:100%; height:100%; overflow:hidden; text-overflow:ellipsis;">{in_flow_text}</div>'

# --- Blob Storage ---
BLOB_SUFFIX_TIMESTAMP_FORMAT = "%H%M%S"       # time in hhmmss
BLOB_SUFFIX_UUID_LENGTH = 6                   # short uuid length

# --- CLI Messages ---
CLI_INIT_MSG = "Initializing document converter in '{mode}' mode..."
CLI_NO_PAGES_WARNING = "Warning: No pages were rendered. The input JSON might be empty or invalid."
CLI_SAVE_SUCCESS = "Successfully saved {file_path}"
CLI_SAVE_ERROR = "Error: Could not write to file {file_path}: {error}"
CLI_RENDER_COMPLETE = "\nRendering complete. {count} pages saved in '{out_dir}'."
CLI_INPUT_FILE_NOT_FOUND = "Error: Input file not found at '{input_path}'"
CLI_INPUT_FILE_INVALID = "Error: Could not decode JSON from '{input_path}'. Please check the file format."
CLI_OUTPUT_DIR_ERROR = "Error: Could not create output directory at '{out_dir}': {error}"

# --- Testing ---
TEST_INVALID_API_KEY = "this-is-a-wrong-key"
TEST_DUMMY_FILE_CONTENT = b"This is a test document."
TEST_PDF_CONTENT_TYPE = "application/pdf"
