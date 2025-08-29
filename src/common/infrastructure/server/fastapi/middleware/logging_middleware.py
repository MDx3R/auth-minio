import logging
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, logger: logging.Logger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request_id = str(uuid.uuid4())

        start_time = time.time()
        extra: dict[str, Any] = {
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "path_params": request.path_params,
            "query_params": dict(request.query_params),
        }

        self.logger.info("incoming request", extra={"extra": extra})

        try:
            response: Response = await call_next(request)
            process_time = (time.time() - start_time) * 1000
            extra.update(
                {
                    "status_code": response.status_code,
                    "process_time_ms": f"{process_time:.2f}",
                }
            )
            self.logger.info("request completed", extra={"extra": extra})
            return response

        except Exception as e:
            extra["exception"] = str(e)
            self.logger.exception(
                "unhandled exception", extra={"extra": extra}
            )
            raise
