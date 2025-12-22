from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from app.core.security import require_api_key
from app.jobs.queue import JobQueue
from app.jobs.worker import JobWorker
from app.models.schemas import BenchTextRequest, ScanRequest
from app.services.pipeline_text import TextPipeline
from app.services.scan_service import ScanService  # ci-dessous

router = APIRouter(prefix="/jobs", tags=["jobs"], dependencies=[Depends(require_api_key)])

queue = JobQueue()
worker = JobWorker(queue, max_workers=2)

pipeline = TextPipeline()
scan_service = ScanService()


@router.post("/bench")
def create_bench_job(req: BenchTextRequest):
    job = queue.create(kind="bench_text", meta={"detectors": req.detectors, "language": req.language})

    def run():
        report = pipeline.bench(
            text=req.text,
            language=req.language,
            detectors=req.detectors,
            min_score=req.min_score,
        )
        return {"report": report}

    worker.submit(job_id=job.id, fn=run)
    return {"job_id": job.id}


@router.post("/scan")
def create_scan_job(req: ScanRequest):
    job = queue.create(kind="scan", meta={"root": req.root, "connector": req.connector})

    def run():
        return scan_service.scan(
            connector=req.connector,
            root=req.root,
            recursive=req.recursive,
            language=req.language,
            detectors=req.detectors,
            min_score=req.min_score,
            limit=req.limit,
        )

    worker.submit(job_id=job.id, fn=run)
    return {"job_id": job.id}


@router.get("/{job_id}")
def get_job(job_id: str):
    job = queue.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job_not_found")
    return job