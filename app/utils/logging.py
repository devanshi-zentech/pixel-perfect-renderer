# app/core/logging_setup.py
import logging, sys, uuid
from loguru import logger
from fastapi import Request, Response

class LoggingSetup:
    def __init__(self):
        # Redirect std logging → loguru
        logging.basicConfig(handlers=[self.InterceptHandler()], level=0, force=True)

        # Configure Loguru sink
        logger.remove()
        logger.add(
            sys.stdout,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {extra[request_id]} | {message}",
            level="INFO",
        )

        # 🔑 Ensure all logs (even background ones) have request_id
        self._patch_logger()

    class InterceptHandler(logging.Handler):
        def emit(self, record):
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

    def _patch_logger(self):
        """
        Guarantee that every log record has a `request_id`.
        Background logs (e.g. Azure SDK) will get 'no-request-context'.
        """
        logger.configure(
            patcher=lambda record: record["extra"].setdefault("request_id", "-")
        )

    async def request_id_middleware(self, request: Request, call_next):
        request_id = str(uuid.uuid4())

        # Attach request_id for this request only
        with logger.contextualize(request_id=request_id):
            logger.info(f"Incoming {request.method} {request.url}")
            response: Response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            logger.info(f"Completed {request.method} {request.url} → {response.status_code}")
            return response
