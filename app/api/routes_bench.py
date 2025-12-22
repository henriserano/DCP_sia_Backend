from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.models.schemas import BenchTextRequest
from app.services.pipeline_text import TextPipeline

router = APIRouter(prefix="/bench", tags=["bench"], dependencies=[Depends(require_api_key)])

pipeline = TextPipeline()


@router.post("/text")
def bench_text(req: BenchTextRequest):
    try:
        return pipeline.bench(
            text=req.text,
            language=req.language,
            detectors=req.detectors,
            min_score=req.min_score,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))