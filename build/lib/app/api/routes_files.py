from __future__ import annotations

import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from app.core.security import require_api_key
from app.core.config import get_settings
from app.services.pipeline_docs import DocumentPipeline
from app.services.pipeline_images import ImagePipeline

router = APIRouter(prefix="/files", tags=["files"], dependencies=[Depends(require_api_key)])

doc_pipeline = DocumentPipeline()
img_pipeline = ImagePipeline()


def _save_upload(upload: UploadFile) -> str:
    settings = get_settings()
    tmp_dir = Path(settings.storage_dir)
    tmp_dir.mkdir(parents=True, exist_ok=True)
    suffix = Path(upload.filename or "").suffix
    path = tmp_dir / f"upload_{uuid.uuid4().hex}{suffix}"
    with path.open("wb") as f:
        f.write(upload.file.read())
    return str(path)


@router.post("/detect/document")
def detect_document(
    file: UploadFile = File(...),
    language: str = "fr",
    detectors: str = "regex,presidio",
    min_score: float = 0.4,
):
    try:
        path = _save_upload(file)
        spans, by_det, summary, errors = doc_pipeline.detect_file(
            file_path=path,
            language=language,
            detectors=[d.strip() for d in detectors.split(",") if d.strip()],
            min_score=min_score,
            merge_overlaps=True,
            return_text=False,
        )
        return {"spans": spans, "by_detector": by_det, "summary": summary, "errors": errors, "file": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/detect/image")
def detect_image(
    file: UploadFile = File(...),
    language: str = "fr",
    detectors: str = "regex,presidio",
    min_score: float = 0.4,
):
    try:
        path = _save_upload(file)
        spans, by_det, summary, errors = img_pipeline.detect_image(
            image_path=path,
            language=language,
            detectors=[d.strip() for d in detectors.split(",") if d.strip()],
            min_score=min_score,
            merge_overlaps=True,
        )
        return {"spans": spans, "by_detector": by_det, "summary": summary, "errors": errors, "file": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
