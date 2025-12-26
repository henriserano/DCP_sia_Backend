from __future__ import annotations

import datetime as dt
import threading
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, Optional

from app.core.logging import get_logger
from app.db.models import JobResult
from app.db.session import SessionLocal

class JobStatus(str, Enum):
    queued = "queued"
    running = "running"
    done = "done"
    error = "error"


@dataclass
class JobRecord:
    id: str
    kind: str
    status: JobStatus = JobStatus.queued
    created_at: dt.datetime = field(default_factory=lambda: dt.datetime.now(dt.timezone.utc))
    started_at: Optional[dt.datetime] = None
    finished_at: Optional[dt.datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    meta: Dict[str, Any] = field(default_factory=dict)


class JobQueue:
    """Minimal in-memory job queue (POC).

    - Thread-safe
    - Stores results in memory
    - Designed to be replaced later by DB/Redis without changing API.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._jobs: Dict[str, JobRecord] = {}
        self._logger = get_logger(__name__)

    def create(self, *, kind: str, meta: Optional[Dict[str, Any]] = None) -> JobRecord:
        job_id = uuid.uuid4().hex
        rec = JobRecord(id=job_id, kind=kind, meta=meta or {})
        with self._lock:
            self._jobs[job_id] = rec
        self._persist(rec)
        return rec

    def get(self, job_id: str) -> Optional[JobRecord]:
        with self._lock:
            return self._jobs.get(job_id)

    def set_running(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = JobStatus.running
            job.started_at = dt.datetime.now(dt.timezone.utc)
        self._persist(job)

    def set_done(self, job_id: str, result: Dict[str, Any]) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = JobStatus.done
            job.result = result
            job.finished_at = dt.datetime.now(dt.timezone.utc)
        self._persist(job)

    def set_error(self, job_id: str, error: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = JobStatus.error
            job.error = error
            job.finished_at = dt.datetime.now(dt.timezone.utc)
        self._persist(job)

    def _persist(self, job: JobRecord) -> None:
        """Persist/refresh job record in the DB for durability."""
        try:
            with SessionLocal() as db:
                db_job = db.get(JobResult, job.id) or JobResult(id=job.id, kind=job.kind)
                db_job.status = job.status.value
                db_job.updated_at = dt.datetime.now(dt.timezone.utc)
                db_job.created_at = db_job.created_at or job.created_at

                # Optional metadata
                lang = job.meta.get("language") if job.meta else None
                detectors = job.meta.get("detectors") if job.meta else None
                if lang:
                    db_job.language = lang
                if detectors:
                    if isinstance(detectors, list):
                        db_job.detectors = ",".join(detectors)
                    else:
                        db_job.detectors = str(detectors)

                # Payload
                payload = job.result or job.meta or {}
                if job.error:
                    payload = {**payload, "error": job.error}
                db_job.set_payload(payload)

                db.add(db_job)
                db.commit()
        except Exception:
            self._logger.exception("Failed to persist job", extra={"job_id": job.id})
