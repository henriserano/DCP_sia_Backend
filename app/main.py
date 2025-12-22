from __future__ import annotations

import os
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.logging import setup_logging, request_id_ctx, get_logger
from app.core.errors import AppError
from app.db.session import init_db

from app.api.routes_health import router as health_router
from app.api.routes_detect import router as detect_router
from app.api.routes_bench import router as bench_router
from app.api.routes_anonymize import router as anonymize_router
from app.api.routes_files import router as files_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_scan import router as scan_router

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()

    # Logging
    setup_logging(level="INFO", json_logs=True)

    # HuggingFace cache dir (avoid downloading each run)
    os.environ.setdefault("HF_HOME", settings.hf_home)

    # DB init (POC)
    init_db()

    # Optionnel: warmup au startup (charge modèles en RAM)
    try:
        from app.services.orchestrator import Orchestrator

        orc = Orchestrator()
        status = orc.warmup(settings.preload_detectors)
        logger.info(f"Warmup detectors: {status}")
    except Exception as e:
        logger.exception("Warmup failed")

    yield


app = FastAPI(
    title=get_settings().app_name,
    version=get_settings().app_version,
    lifespan=lifespan,
)

# CORS (utile si front)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # en prod, restreins !
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Middleware Request-ID (corrélation logs + debug) ---
@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    rid = request.headers.get("X-Request-Id") or uuid.uuid4().hex
    token = request_id_ctx.set(rid)
    try:
        response = await call_next(request)
        response.headers["X-Request-Id"] = rid
        return response
    finally:
        request_id_ctx.reset(token)


# --- Handler global AppError -> JSON propre ---
@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    from fastapi.responses import JSONResponse

    payload = {"error": {"code": exc.code, "message": exc.message, "details": exc.details}}
    return JSONResponse(status_code=exc.status_code, content=payload)


# --- Routes ---
app.include_router(health_router)
app.include_router(detect_router)
app.include_router(bench_router)
app.include_router(anonymize_router)
app.include_router(files_router)
app.include_router(jobs_router)
app.include_router(scan_router)