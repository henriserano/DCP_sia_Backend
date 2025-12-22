from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.models.schemas import AnonymizeTextRequest, AnonymizeTextResponse
from app.services.pipeline_text import TextPipeline
from app.services.anonymizer import Anonymizer

router = APIRouter(prefix="/anonymize", tags=["anonymize"], dependencies=[Depends(require_api_key)])

pipeline = TextPipeline()
anonymizer = Anonymizer(salt="dcp_eval_salt")  # en prod: env var


@router.post("/text", response_model=AnonymizeTextResponse)
def anonymize_text(req: AnonymizeTextRequest):
    try:
        spans, _, summary, _ = pipeline.detect(
            text=req.text,
            language=req.language,
            detectors=req.detectors,
            min_score=req.min_score,
            merge_overlaps=req.merge_overlaps,
            return_text=True,
            best_effort=True,
        )
        anon = anonymizer.anonymize(req.text, spans, strategy=req.strategy)
        return AnonymizeTextResponse(anonymized_text=anon, spans=spans, summary=summary)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))