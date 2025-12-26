from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import require_api_key
from app.services.orchestrator import Orchestrator

router = APIRouter(prefix="/meta", tags=["meta"], dependencies=[Depends(require_api_key)])

orc = Orchestrator()


class WarmupRequest(BaseModel):
    detectors: list[str] | None = None


@router.get("/detectors")
def list_detectors():
    """Expose la liste des détecteurs disponibles et ceux déjà instanciés."""
    return {
        "available": sorted(list(orc.registry.keys())),
        "loaded": sorted(list(orc._instances.keys())),
    }


@router.post("/detectors/warmup")
def warmup_detectors(req: WarmupRequest):
    """Permet de précharger certains détecteurs à la demande."""
    status = orc.warmup(req.detectors)
    return {"status": status}
