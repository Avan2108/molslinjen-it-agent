"""FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    admin_router,
    chat_router,
    faqs_router,
    feedback_router,
    tickets_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown events."""
    # Startup
    settings = get_settings()
    print(f"Starting Molslinjen IT Support Agent API")
    print(f"CORS origins: {settings.CORS_ORIGINS}")

    yield

    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Molslinjen IT Support Agent",
    description="AI-powered IT support chatbot for Molslinjen employees",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(chat_router, prefix="/api/v1")
app.include_router(tickets_router, prefix="/api/v1")
app.include_router(feedback_router, prefix="/api/v1")
app.include_router(faqs_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/")
async def root() -> dict:
    """Root endpoint with API info."""
    return {
        "name": "Molslinjen IT Support Agent API",
        "version": "0.1.0",
        "docs": "/docs",
    }
