from __future__ import annotations
from typing import List
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class PIICatcherDetector(BaseDetector):
    name = "piicatcher"

    def __init__(self):
        """
        Ajuste l'import selon la lib réelle.
        Exemple possible:
            from piicatcher import PIICatcher
            self.engine = PIICatcher(...)
        """
        try:
            import piicatcher  # type: ignore
        except Exception as e:
            raise RuntimeError("PIICatcher non installé / import à ajuster.") from e

        self.engine = piicatcher  # placeholder

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        # À adapter à l’API de PIICatcher.
        # Exemple hypothétique: self.engine.detect(text) -> [{"start":..,"end":..,"label":..,"score":..}]
        results = []
        spans: List[DcpSpan] = []
        for r in results:
            spans.append(DcpSpan(r["start"], r["end"], r.get("label", "OTHER"), float(r.get("score", 0.5)), self.name, text[r["start"]:r["end"]]))
        return spans