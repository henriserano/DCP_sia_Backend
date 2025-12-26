from __future__ import annotations

from typing import Any, Dict, Iterable, List, Tuple

from app.models.schemas import DcpSpan
from app.services.orchestrator import Orchestrator


def _flatten(obj: Any, prefix: str = "") -> Iterable[Tuple[str, str]]:
    """Flatten dict/list structures into key-path -> string value."""
    if obj is None:
        return
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else str(k)
            yield from _flatten(v, p)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            p = f"{prefix}[{i}]"
            yield from _flatten(v, p)
    else:
        s = str(obj)
        if s.strip():
            yield (prefix or "value", s)


class StructuredPipeline:
    """Structured-data detection by running text detectors on values."""

    def __init__(self, orchestrator: Orchestrator | None = None) -> None:
        self.orc = orchestrator or Orchestrator()

    def detect_object(
        self,
        *,
        obj: Any,
        language: str = "fr",
        detectors: List[str] | None = None,
        min_score: float = 0.4,
    ) -> Dict[str, Any]:
        detectors = detectors or ["regex", "presidio", "spacy", "hf"]
        results: Dict[str, Any] = {"fields": {}, "summary": {}, "errors": {}}

        global_spans: List[DcpSpan] = []
        for path, value in _flatten(obj):
            spans, by_det, summary, errors = self.orc.detect_text_multi(
                text=value,
                language=language,
                detectors=detectors,
                min_score=min_score,
                merge_overlaps=True,
                return_text=True,
                best_effort=True,
            )

            results["fields"][path] = {
                "value": value,
                "spans": spans,
                "by_detector": by_det,
                "summary": summary,
                "errors": errors,
            }
            global_spans.extend(spans)
            results["errors"].update({f"{path}:{k}": v for k, v in errors.items()})

        out_sum: Dict[str, int] = {}
        for s in global_spans:
            out_sum[s.label] = out_sum.get(s.label, 0) + 1
        results["summary"] = out_sum
        return results