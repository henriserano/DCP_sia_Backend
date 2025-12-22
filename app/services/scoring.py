from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from app.models.schemas import DcpSpan


# Business priority by label: structured identifiers should win over generic NER.
LABEL_PRIORITY: Dict[str, int] = {
    "IBAN": 30,
    "EMAIL": 30,
    "PHONE": 25,
    "ID_NUMBER": 25,
    "FINANCE": 20,
    "HEALTH": 20,
    "ADDRESS": 18,
    "PERSON": 15,
    "ORG": 10,
    "LOCATION": 8,
    "DATE": 6,
    "OTHER": 0,
}

# Per-detector priority (tweak with empirical quality)
DETECTOR_PRIORITY: Dict[str, int] = {
    "regex": 30,
    "hf": 18,
    "spacy": 12,
    "presidio": 10,
}


@dataclass(frozen=True)
class MergeDecision:
    kept: DcpSpan
    dropped: DcpSpan
    reason: str


def _span_len(s: DcpSpan) -> int:
    return max(0, int(s.end) - int(s.start))


def better_span(a: DcpSpan, b: DcpSpan) -> DcpSpan:
    """Decide which span to keep when they overlap."""
    la = LABEL_PRIORITY.get(a.label, 1)
    lb = LABEL_PRIORITY.get(b.label, 1)
    if la != lb:
        return a if la > lb else b

    da = DETECTOR_PRIORITY.get(a.source, 1)
    db = DETECTOR_PRIORITY.get(b.source, 1)
    if da != db:
        return a if da > db else b

    if a.score != b.score:
        return a if a.score > b.score else b

    return a if _span_len(a) >= _span_len(b) else b


def merge_overlaps(spans: Iterable[DcpSpan]) -> List[DcpSpan]:
    """Merge overlapping spans using business-oriented priorities."""
    items = sorted(list(spans), key=lambda s: (s.start, -s.end, -s.score))
    out: List[DcpSpan] = []

    for s in items:
        if not out:
            out.append(s)
            continue
        last = out[-1]
        if s.start <= last.end:  # overlap
            out[-1] = better_span(last, s)
        else:
            out.append(s)
    return out


def merge_adjacent_persons(spans: Iterable[DcpSpan], max_gap: int = 1) -> List[DcpSpan]:
    """Merge adjacent PERSON entities (common with token-level NER fragmentation)."""
    items = sorted(list(spans), key=lambda s: (s.start, s.end))
    out: List[DcpSpan] = []

    for s in items:
        if (
            out
            and s.label == "PERSON"
            and out[-1].label == "PERSON"
            and s.start <= out[-1].end + max_gap
        ):
            prev = out[-1]
            merged_text: Optional[str]
            if prev.text is None or s.text is None:
                merged_text = None
            else:
                merged_text = prev.text + s.text

            out[-1] = DcpSpan(
                start=prev.start,
                end=s.end,
                label="PERSON",
                score=max(prev.score, s.score),
                source=prev.source
                if DETECTOR_PRIORITY.get(prev.source, 0) >= DETECTOR_PRIORITY.get(s.source, 0)
                else s.source,
                text=merged_text,
                metadata={**(prev.metadata or {}), **(s.metadata or {}), "merged": "adjacent_persons"},
            )
            continue

        out.append(s)

    return out


def suppress_known_false_positives(spans: Iterable[DcpSpan]) -> List[DcpSpan]:
    """Remove some common/obvious false positives seen in practice."""
    items = list(spans)
    ibans = [s for s in items if s.label == "IBAN"]

    def overlaps(a: DcpSpan, b: DcpSpan) -> bool:
        return a.start < b.end and b.start < a.end

    cleaned: List[DcpSpan] = []
    for s in items:
        # Example: Presidio EN can tag IBAN prefix as MEDICAL_LICENSE => OTHER in our mapping.
        if (
            s.source == "presidio"
            and s.label == "OTHER"
            and any(overlaps(s, i) and _span_len(i) > _span_len(s) for i in ibans)
        ):
            continue
        cleaned.append(s)

    return cleaned


def finalize_spans(
    spans: Iterable[DcpSpan],
    *,
    min_score: float = 0.0,
    merge: bool = True,
    merge_persons: bool = True,
) -> List[DcpSpan]:
    """End-to-end post-processing: filter, merge, cleanup."""
    items = [s for s in spans if s.score >= min_score]
    items = suppress_known_false_positives(items)
    if merge:
        items = merge_overlaps(items)
    if merge_persons:
        items = merge_adjacent_persons(items)
    return items


def summarize(spans: Iterable[DcpSpan]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for s in spans:
        out[s.label] = out.get(s.label, 0) + 1
    return out