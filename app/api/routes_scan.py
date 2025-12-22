from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.models.schemas import ScanRequest, ScanResponse
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scan", tags=["scan"], dependencies=[Depends(require_api_key)])

scan_service = ScanService()


@router.post("", response_model=ScanResponse)
def scan(req: ScanRequest):
    try:
        result = scan_service.scan(
            connector=req.connector,
            root=req.root,
            recursive=req.recursive,
            language=req.language,
            detectors=req.detectors,
            min_score=req.min_score,
            limit=req.limit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))