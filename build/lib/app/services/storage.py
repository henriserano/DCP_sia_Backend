from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, Optional


class LocalStorage:
    """Minimal local filesystem storage for results (useful for POC/bench)."""

    def __init__(self, base_dir: str = "data/tmp") -> None:
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)

    def put_json(self, payload: Dict[str, Any], *, prefix: str = "job") -> str:
        job_id = f"{prefix}_{uuid.uuid4().hex}"
        path = self.base / f"{job_id}.json"
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return job_id

    def get_json(self, job_id: str) -> Optional[Dict[str, Any]]:
        path = self.base / f"{job_id}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))