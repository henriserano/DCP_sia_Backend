from __future__ import annotations

import time
from typing import Any, Dict, List, Tuple

from app.models.schemas import DcpSpan
from app.services.scoring import finalize_spans, summarize

from app.detectors.regex_detector import RegexDetector
from app.detectors.presidio_detector import PresidioDetector
from app.detectors.spacy_detector import SpacyDetector
from app.detectors.hf_ner_detector import HFNerDetector


class Orchestrator:
    """
    Runs selected detectors and returns per-detector + merged outputs.
    Designed for benchmarking multiple open-source solutions via the API body.
    """

    def __init__(self) -> None:
        # Lazy init factories
        self.registry = {
            "regex": lambda: RegexDetector(),
            "presidio": lambda: PresidioDetector(),
            "spacy": lambda: SpacyDetector(),
            "hf": lambda: HFNerDetector(),
        }
        self._instances: Dict[str, Any] = {}

    def get_detector(self, name: str) -> Any:
        if name not in self.registry:
            raise ValueError(f"Detector inconnu: {name}")
        if name not in self._instances:
            self._instances[name] = self.registry[name]()
        return self._instances[name]

    def warmup(self, detectors: List[str] | None = None) -> Dict[str, str]:
        """Best-effort warmup to preload models into RAM."""
        detectors = detectors or list(self.registry.keys())
        status: Dict[str, str] = {}
        for d in detectors:
            try:
                self.get_detector(d)
                status[d] = "ok"
            except Exception as e:
                status[d] = f"error: {e}"
        return status

    def detect_text_multi(
        self,
        *,
        text: str,
        language: str,
        detectors: List[str],
        min_score: float,
        merge_overlaps: bool,
        return_text: bool,
        best_effort: bool = True,
    ) -> Tuple[List[DcpSpan], Dict[str, List[DcpSpan]], Dict[str, int], Dict[str, str]]:
        """
        Run detectors; returns (merged_spans, by_detector, summary, errors).
        """

        by_detector: Dict[str, List[DcpSpan]] = {}
        errors: Dict[str, str] = {}
        all_spans: List[DcpSpan] = []

        for det_name in detectors:
            try:
                det = self.get_detector(det_name)
                spans: List[DcpSpan] = det.detect(text=text, language=language)

                spans = [s for s in spans if s.score >= min_score]
                if not return_text:
                    for s in spans:
                        s.text = None

                by_detector[det_name] = spans
                all_spans.extend(spans)

            except Exception as e:
                errors[det_name] = str(e)
                by_detector[det_name] = []
                if not best_effort:
                    raise

        merged = finalize_spans(
            all_spans,
            min_score=min_score,
            merge=merge_overlaps,
            merge_persons=True,
        )
        return merged, by_detector, summarize(merged), errors

    def bench_text_multi(
        self,
        *,
        text: str,
        language: str,
        detectors: List[str],
        min_score: float,
    ) -> Dict[str, Any]:
        """Benchmark each detector: duration + output size."""
        report: Dict[str, Any] = {}
        for det_name in detectors:
            start = time.perf_counter()
            try:
                det = self.get_detector(det_name)
                spans: List[DcpSpan] = det.detect(text=text, language=language)
                spans = [s for s in spans if s.score >= min_score]
                ok = True
                err = None
            except Exception as e:
                spans = []
                ok = False
                err = str(e)

            end = time.perf_counter()
            report[det_name] = {
                "ok": ok,
                "error": err,
                "time_ms": round((end - start) * 1000.0, 2),
                "entities": len(spans),
                "summary": summarize(spans),
            }
        return report
    def detect_text(
        self,
        text: str,
        language: str,
        detectors: List[str],
        min_score: float = 0.4,
        merge_overlaps: bool = True,
        return_text: bool = True,
        best_effort: bool = True,
    ) -> Tuple[List[DcpSpan], Dict[str, List[DcpSpan]], Dict[str, int], Dict[str, str]]:
        """
        API STABLE utilisée par routes_detect + pipelines (text/image/doc).
        Retourne: (spans_merged, by_detector, summary, errors)
        """
        by_detector: Dict[str, List[DcpSpan]] = {}
        errors: Dict[str, str] = {}

        for det_name in detectors:
            try:
                det = self._get_detector(det_name)
                spans = det.detect(text=text, language=language, min_score=min_score)
                # option: vider le texte si return_text=False
                if not return_text:
                    for s in spans:
                        s.text = ""
                by_detector[det_name] = spans
            except Exception as e:
                if not best_effort:
                    raise
                errors[det_name] = str(e)
                by_detector[det_name] = []

        # Merge + summary (si tu as déjà une util, branche-la ici)
        merged = self._merge_spans(sum(by_detector.values(), [])) if merge_overlaps else sum(by_detector.values(), [])

        summary: Dict[str, int] = {}
        for s in merged:
            summary[s.label] = summary.get(s.label, 0) + 1

        return merged, by_detector, summary, errors

    @staticmethod
    def _merge_spans(spans: List[DcpSpan]) -> List[DcpSpan]:
        if not spans:
            return []

        spans = sorted(spans, key=lambda s: (s.start, -s.end))
        out: List[DcpSpan] = []

        for s in spans:
            if not out:
                out.append(s)
                continue

            last = out[-1]
            if s.start <= last.end:  # overlap / touch
                # garder celui au score le + élevé
                if s.score > last.score:
                    out[-1] = s
                else:
                    # étendre si besoin (optionnel)
                    last.end = max(last.end, s.end)
                continue

            out.append(s)

        return out