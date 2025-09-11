# --- Core Imports ---
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

# --- Custom Imports ---
from app.core.config import settings
from app.api.endpoints import router as api_router
from app.utils.exceptions import ExceptionHandlers
from app.utils.logging import LoggingSetup

from contextlib import asynccontextmanager
from app.core.browser_manager import start_browser, stop_browser

playwright = None
browser = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    await start_browser()
    yield
    await stop_browser()

# --- Initialization ---
logging_setup = LoggingSetup()
exception_handlers = ExceptionHandlers()

# --- FastAPI App Initialization ---
app = FastAPI(
    title=settings.project_name,
    version=settings.project_version,
    lifespan=lifespan
)

app.middleware("http")(logging_setup.request_id_middleware)
# --- Exception Handlers ---
app.add_exception_handler(HTTPException, exception_handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, exception_handlers.validation_exception_handler)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key"],
)

# --- API Router ---
app.include_router(api_router)
