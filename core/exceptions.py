"""Domain exceptions and FastAPI HTTP mappings."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from services.football_data_client import FootballDataError as _FdClientError
from services.football_service import FootballAPIError

# Re-export for clean imports from core layer.
FootballDataError = _FdClientError


class AnalysisError(Exception):
    """Raised when deterministic analysis cannot produce a result."""

    def __init__(self, message: str, *, code: str = "analysis_error"):
        super().__init__(message)
        self.code = code


def _error_body(message: str, code: str, status: int) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"detail": message, "code": code},
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach domain exception handlers to the FastAPI app."""

    @app.exception_handler(FootballDataError)
    async def _football_data_error(_: Request, exc: FootballDataError) -> JSONResponse:
        status = 429 if exc.status_code == 429 else 502
        return _error_body(str(exc), "football_data_error", status)

    @app.exception_handler(FootballAPIError)
    async def _football_api_error(_: Request, exc: FootballAPIError) -> JSONResponse:
        status = 429 if exc.status_code == 429 else 502
        return _error_body(str(exc), "football_api_error", status)

    @app.exception_handler(AnalysisError)
    async def _analysis_error(_: Request, exc: AnalysisError) -> JSONResponse:
        return _error_body(str(exc), exc.code, 422)
