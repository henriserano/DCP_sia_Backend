from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.models.schemas import DetectTextRequest, DetectTextResponse, DetectStructuredRequest
from app.services.pipeline_text import TextPipeline
from app.services.pipeline_structured import StructuredPipeline

router = APIRouter(prefix="/detect", tags=["detect"], dependencies=[Depends(require_api_key)])

text_pipeline = TextPipeline()
structured_pipeline = StructuredPipeline()


@router.post("/text", response_model=DetectTextResponse)
def detect_text(req: DetectTextRequest):
    try:
        spans, by_detector, summary, errors = text_pipeline.detect(
            text=req.text,
            language=req.language,
            detectors=req.detectors,
            min_score=req.min_score,
            merge_overlaps=req.merge_overlaps,
            return_text=req.return_text,
            best_effort=req.best_effort,
        )
        return DetectTextResponse(spans=spans, by_detector=by_detector, summary=summary, errors=errors)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/structured")
def detect_structured(req: DetectStructuredRequest):
    # Retour libre (détaillé par champ)
    try:
        return structured_pipeline.detect_object(
            obj=req.obj,
            language=req.language,
            detectors=req.detectors,
            min_score=req.min_score,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))