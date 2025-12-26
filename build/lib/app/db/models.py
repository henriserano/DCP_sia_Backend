from __future__ import annotations

import datetime as dt
import json
import uuid
from typing import Any, Dict, Optional

from sqlalchemy import DateTime, String, Text, Index
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class JobResult(Base):
    """Persisted job/result record for detections/benchmarks/anonymization.

    We store payload as JSON text to keep SQLite compatibility simple.
    On Postgres, you can switch to JSONB easily.
    """

    __tablename__ = "job_results"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: uuid.uuid4().hex)
    kind: Mapped[str] = mapped_column(String(32), index=True)  # detect_text | bench_text | anonymize | detect_file ...
    status: Mapped[str] = mapped_column(String(16), default="done")  # queued|running|done|error
    created_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc))
    updated_at: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), default=lambda: dt.datetime.now(dt.timezone.utc))

    # Optional metadata fields for filtering
    language: Mapped[Optional[str]] = mapped_column(String(8), nullable=True)
    detectors: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)  # comma-separated

    # JSON payload stored as Text
    payload_json: Mapped[str] = mapped_column(Text, default="{}")
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    __table_args__ = (
        Index("ix_job_results_kind_created_at", "kind", "created_at"),
    )

    def set_payload(self, payload: Dict[str, Any]) -> None:
        self.payload_json = json.dumps(payload, ensure_ascii=False)

    def get_payload(self) -> Dict[str, Any]:
        try:
            return json.loads(self.payload_json or "{}")
        except Exception:
            return {}