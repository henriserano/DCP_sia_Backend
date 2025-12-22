from __future__ import annotations

from typing import Any, Dict, List, Tuple

from app.models.schemas import DcpSpan
from app.services.orchestrator import Orchestrator


class TextPipeline:
    """High-level API for text detection & benchmark."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orc = orchestrator or Orchestrator()

    def detect(
        self,
        *,
        text: str,
        language: str = "fr",
        detectors: List[str] | None = None,
        min_score: float = 0.4,
        merge_overlaps: bool = True,
        return_text: bool = True,
        best_effort: bool = True,
    ) -> Tuple[List[DcpSpan], Dict[str, List[DcpSpan]], Dict[str, int], Dict[str, str]]:
        detectors = detectors or ["regex", "presidio", "spacy", "hf"]
        return self.orc.detect_text_multi(
            text=text,
            language=language,
            detectors=detectors,
            min_score=min_score,
            merge_overlaps=merge_overlaps,
            return_text=return_text,
            best_effort=best_effort,
        )

    def bench(
        self,
        *,
        text: str,
        language: str = "fr",
        detectors: List[str] | None = None,
        min_score: float = 0.4,
    ) -> Dict[str, Any]:
        detectors = detectors or ["regex", "presidio", "spacy", "hf"]
        return self.orc.bench_text_multi(text=text, language=language, detectors=detectors, min_score=min_score)