"""Background jobs for scanning/benchmarking/anonymization.

Default implementation uses an in-process thread pool (POC-friendly).
Can be swapped for Redis/Celery/RQ later with the same interface.
"""

from app.jobs.queue import JobQueue, JobStatus, JobRecord

__all__ = ["JobQueue", "JobStatus", "JobRecord"]