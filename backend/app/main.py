"""
SpamGuard API - Main FastAPI Application
Production-ready spam and fraud detection platform
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from prometheus_client import make_asgi_app, Counter, Histogram

from app.config import settings
from app.database import create_tables
from app.routes import api_router
from app.routes.graphql import graphql_app
from app.utils.logging_config import setup_logging

# Setup logging
setup_logging()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('http_request_duration_seconds', 'HTTP request latency', ['method', 'endpoint'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    # Startup
    logger = logging.getLogger(__name__)
    logger.info("Starting SpamGuard API...")

    # Create database tables
    await create_tables()

    # Load ML models
    # TODO: Initialize ML models

    logger.info("SpamGuard API started successfully")

    yield

    # Shutdown
    logger.info("Shutting down SpamGuard API...")

# Create FastAPI app
app = FastAPI(
    title="SpamGuard API",
    description="Production-ready spam and fraud detection platform with ML-powered predictions",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add Prometheus metrics middleware
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Request logging and metrics middleware
@app.middleware("http")
async def add_request_metrics(request: Request, call_next):
    """Middleware to track request metrics"""
    method = request.method
    endpoint = request.url.path

    with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
        response = await call_next(request)

    REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=response.status_code).inc()

    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Include GraphQL
app.include_router(graphql_app, prefix="/graphql")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to SpamGuard API",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )