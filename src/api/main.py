import time
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import os

from src.api.routes import datasets, pipelines, tasks, steps, exports
from src.services.database import get_db, init_db
from src.utils.config import settings

# Configure application
app = FastAPI(
    title="Data Preprocessing Pipeline API",
    description="A universal, production-ready, and scalable data preprocessing pipeline platform for AI/ML developers.",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins in development
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An unexpected error occurred"},
    )

# Include API routers
app.include_router(datasets.router, prefix="/api/datasets", tags=["Datasets"])
app.include_router(pipelines.router, prefix="/api/pipelines", tags=["Pipelines"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["ML Tasks"])
app.include_router(steps.router, prefix="/api/steps", tags=["Pipeline Steps"])
app.include_router(exports.router, prefix="/api/exports", tags=["Exports"])

# Health check endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    return {"status": "ok", "version": app.version}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up API server")
    # Initialize database
    await init_db()
    logger.info("Database initialized")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down API server")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 