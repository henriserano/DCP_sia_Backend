from __future__ import annotations
from typing import List
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class PIICodexDetector(BaseDetector):
    name = "pii_codex"

    def __init__(self):
        try:
            import pii_codex  # type: ignore
        except Exception as e:
            raise RuntimeError("PII-Codex non installé / import à ajuster.") from e
        self.engine = pii_codex  # placeholder

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        results = []
        spans: List[DcpSpan] = []
        for r in results:
            spans.append(DcpSpan(r["start"], r["end"], r.get("label", "OTHER"), float(r.get("score", 0.5)), self.name, text[r["start"]:r["end"]]))
        return spans