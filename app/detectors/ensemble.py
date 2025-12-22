from __future__ import annotations
from typing import List
from app.models.schemas import DcpSpan

def merge_spans(spans: List[DcpSpan]) -> List[DcpSpan]:
    """
    Merge overlaps by keeping the "best" span.
    Heuristic: prefer higher score, then longer span.
    """
    spans = sorted(spans, key=lambda s: (s.start, -s.end, -s.score))
    out: List[DcpSpan] = []
    for s in spans:
        if not out:
            out.append(s)
            continue

        last = out[-1]
        if s.start <= last.end:  # overlap
            last_len = last.end - last.start
            s_len = s.end - s.start
            best = s if (s.score, s_len) > (last.score, last_len) else last
            out[-1] = best
        else:
            out.append(s)
    return out