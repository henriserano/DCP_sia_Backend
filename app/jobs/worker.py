from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable, Dict, Optional

from app.jobs.queue import JobQueue
from app.core.logging import get_logger

logger = get_logger(__name__)


class JobWorker:
    """Executes jobs in background threads (in-process POC)."""

    def __init__(self, queue: JobQueue, max_workers: int = 2):
        self.queue = queue
        self.pool = ThreadPoolExecutor(max_workers=max_workers)

    def submit(self, *, job_id: str, fn: Callable[[], Dict[str, Any]]) -> None:
        """Submit a no-arg function that returns a dict result."""
        self.queue.set_running(job_id)

        def _run():
            try:
                res = fn()
                self.queue.set_done(job_id, res)
            except Exception as e:
                logger.exception("Job failed", extra={"job_id": job_id})
                self.queue.set_error(job_id, str(e))

        self.pool.submit(_run)