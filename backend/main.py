import time
import uuid
from datetime import datetime, timezone

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.api.v1.router import api_router
from backend.config import settings
from backend.core.exceptions import NyayaSetuBaseError
from backend.core.logging import configure_logging
from backend.core.rate_limiter import limiter

configure_logging()
logger = structlog.get_logger()

app = FastAPI(
    title="NyayaSetu API",
    version="1.0.0",
    docs_url="/api/docs" if settings.APP_ENV == "development" else None,
    redoc_url=None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

if settings.APP_ENV == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["nyayasetu.in", "www.nyayasetu.in", "api.nyayasetu.in", "localhost"],
    )

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.monotonic()
    structlog.contextvars.bind_contextvars(request_id=request_id)

    response = await call_next(request)

    duration_ms = (time.monotonic() - start_time) * 1000
    logger.info(
        "http_request",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=round(duration_ms, 2),
    )

    structlog.contextvars.clear_contextvars()
    response.headers["X-Request-ID"] = request_id
    return response


STATUS_MAP = {
    "EMAIL_ALREADY_EXISTS": 409,
    "INVALID_CREDENTIALS": 401,
    "ACCOUNT_NOT_VERIFIED": 403,
    "INVALID_TOKEN": 401,
    "FREE_TIER_EXHAUSTED": 429,
    "QUERY_NOT_FOUND": 404,
    "ACCESS_DENIED": 403,
    "PAYMENT_REQUIRED": 402,
    "INVALID_SIGNATURE": 400,
    "PAYMENT_ALREADY_VERIFIED": 409,
    "PIPELINE_ERROR": 500,
    "INSUFFICIENT_PERMISSIONS": 403,
}


@app.exception_handler(NyayaSetuBaseError)
async def nyayasetu_exception_handler(request: Request, exc: NyayaSetuBaseError):
    status_code = STATUS_MAP.get(exc.code, 400)
    extra = {}
    if hasattr(exc, "reset_at"):
        extra["reset_at"] = exc.reset_at
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "data": None,
            "error": {"code": exc.code, "message": exc.message, **extra},
            "meta": {
                "request_id": str(uuid.uuid4()),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "version": "1.0",
            },
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "data": None,
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred.",
            },
        },
    )


app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
