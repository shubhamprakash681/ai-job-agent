from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    def __init__(self, status_code: int, detail: str, error_code: str):
        self.status_code = status_code
        self.detail = detail
        self.error_code = error_code


class NotFoundError(AppError):
    def __init__(self, detail: str = "Not Found", error_code: str = "NOT_FOUND"):
        super().__init__(status_code=404, detail=detail, error_code=error_code)


class AuthenticationError(AppError):
    def __init__(self, detail: str = "Authentication failed", error_code: str = "AUTHENTICATION_ERROR"):
        super().__init__(status_code=401, detail=detail, error_code=error_code)


class AuthorizationError(AppError):
    def __init__(self, detail: str = "Permission denied", error_code: str = "AUTHORIZATION_ERROR"):
        super().__init__(status_code=403, detail=detail, error_code=error_code)


class ValidationError(AppError):
    def __init__(self, detail: str = "Validation error", error_code: str = "VALIDATION_ERROR"):
        super().__init__(status_code=422, detail=detail, error_code=error_code)


class ExternalServiceError(AppError):
    def __init__(self, detail: str = "External service error", error_code: str = "EXTERNAL_SERVICE_ERROR"):
        super().__init__(status_code=502, detail=detail, error_code=error_code)


class RateLimitError(AppError):
    def __init__(self, detail: str = "Rate limit exceeded", error_code: str = "RATE_LIMIT_ERROR"):
        super().__init__(status_code=429, detail=detail, error_code=error_code)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.error_code, "message": exc.detail}},
        )
