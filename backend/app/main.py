from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging import setup_logging, get_logger
from app.core.errors import register_error_handlers
from app.api.router import api_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan: startup and shutdown logic."""
    setup_logging(log_level=settings.LOG_LEVEL, environment=settings.ENVIRONMENT)
    logger = get_logger(__name__)
    logger.info("Starting AI Job Agent API...")

    # Initialize database tables and ensure default variants exist
    try:
        from app.db.session import init_db
        await init_db()

        from app.db.init_db import init_db as seed_db
        await seed_db()
        logger.info("Database initialized and verified successfully.")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}", exc_info=True)

    logger.info("AI Job Agent API started successfully.")
    yield

    logger.info("Shutting down AI Job Agent API...")


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description="Personal AI-powered job search and application platform",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(api_router, prefix="/api")


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "name": settings.APP_NAME,
        "version": "0.1.0",
        "status": "running",
    }
