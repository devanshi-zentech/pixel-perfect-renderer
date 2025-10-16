import logging
import sys
import os
import tempfile
import uuid
from loguru import logger
from fastapi import Request, Response

class InterceptHandler(logging.Handler):
    """Redirects standard logging records to Loguru."""

    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())


class LoggingSetup:
    def __init__(self, log_file: str | None = None):
        # Redirect std logging → loguru
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        # Configure Loguru sinks
        logger.remove()

        self._patch_logger()

        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[request_id]} | {extra[ip]} | {message}",
            level="INFO",
        )
        candidate = os.path.join(os.getcwd(), "app.log")

        try:
            # Ensure parent directory exists for user-specified paths.
            parent = os.path.dirname(candidate) or "."
            if parent and not os.path.exists(parent):
                os.makedirs(parent, exist_ok=True)

            # Attempt to open the file for append to ensure it's writable.
            with open(candidate, "a"):
                pass

            logger.add(
                candidate,
                rotation="10 MB",
                retention="7 days",
                compression="zip",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[request_id]} | {extra[ip]} | {message}",
                level="INFO",
                enqueue=True,
            )
        except Exception:
            # If file path is not writable, skip file sink and rely on stdout.
            logger.warning(f"Log file {candidate} not writable; writing logs to stdout only.")

    def _patch_logger(self):
        """
        Guarantee that every log record has `request_id` and `ip`.
        Background logs (e.g. Azure SDK) will get defaults.
        """
        logger.configure(
            patcher=lambda record: (
                record["extra"].setdefault("request_id", "-"),
                record["extra"].setdefault("ip", "-"),
            )
        )

    async def request_id_middleware(self, request: Request, call_next):
        """Middleware to add a unique request_id and client IP to logs."""
        request_id = str(uuid.uuid4())

        # Extract client IP (use X-Forwarded-For if behind proxy)
        forwarded = request.headers.get("x-forwarded-for")
        client_ip = forwarded.split(",")[0] if forwarded else request.client.host

        with logger.contextualize(request_id=request_id, ip=client_ip):
            logger.info(f"Incoming {request.method} {request.url}")
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            logger.info(f"Completed {request.method} {request.url} → {response.status_code}")
            return response
