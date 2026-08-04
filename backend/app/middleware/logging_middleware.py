import time

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from app.core.logger import setup_logger

logger = setup_logger("Middleware")


class LoggingMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):

        start = time.perf_counter()

        logger.info(
            f"{request.method} {request.url.path} - Requisição iniciada"
        )

        response = await call_next(request)

        elapsed = time.perf_counter() - start

        logger.info(
            f"{request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Tempo: {elapsed:.2f}s"
        )

        return response