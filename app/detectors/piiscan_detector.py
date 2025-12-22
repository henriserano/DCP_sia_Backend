from __future__ import annotations
from typing import List
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class PIIScanDetector(BaseDetector):
    name = "piiscan"

    def __init__(self):
        """
        Slide: 'piiscan' (souvent lié à des scans sur data structurée)
        -> selon le package réel, l’adapter à .scan(text) ou profiling.
        """
        try:
            import piiscan  # type: ignore
        except Exception as e:
            raise RuntimeError("piiscan non installé / import à ajuster.") from e
        self.engine = piiscan  # placeholder

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        return []