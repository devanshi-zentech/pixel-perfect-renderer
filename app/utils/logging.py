import logging
import sys
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
    def __init__(self, log_file: str = "app.log"):
        # Redirect std logging → loguru
        logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

        # Configure Loguru sinks
        logger.remove()
        # Console sink
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[request_id]} | {extra[ip]} | {message}",
            level="INFO",
        )

        # File sink
        logger.add(
            log_file,
            rotation="10 MB",      # Rotate when file grows too large
            retention="7 days",    # Keep logs for 7 days
            compression="zip",     # Compress old logs
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[request_id]} | {extra[ip]} | {message}",
            level="INFO",
            enqueue=True,          # Thread/process safe
        )

        # Ensure all logs (even background ones) have request_id and ip
        self._patch_logger()

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