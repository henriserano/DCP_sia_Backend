from __future__ import annotations

import hashlib
from typing import Dict, Iterable, Literal

from app.models.schemas import DcpSpan

Strategy = Literal["mask", "redact", "hash"]


class Anonymizer:
    """
    Simple anonymization utilities:
    - mask: keep length, replace chars with *
    - redact: replace with <LABEL>
    - hash: replace with stable hash token
    """

    def __init__(self, *, salt: str = "") -> None:
        self.salt = salt

    def anonymize(self, text: str, spans: Iterable[DcpSpan], *, strategy: Strategy = "redact") -> str:
        items = sorted(list(spans), key=lambda s: s.start, reverse=True)
        out = text
        for s in items:
            chunk = out[s.start : s.end]
            repl = self._replace(chunk, label=s.label, strategy=strategy)
            out = out[: s.start] + repl + out[s.end :]
        return out

    def _replace(self, chunk: str, *, label: str, strategy: Strategy) -> str:
        if strategy == "mask":
            return "*" * max(1, len(chunk))
        if strategy == "redact":
            return f"<{label}>"
        if strategy == "hash":
            h = hashlib.sha256((self.salt + chunk).encode("utf-8")).hexdigest()[:12]
            return f"<{label}:{h}>"
        return f"<{label}>"

    def count_by_label(self, spans: Iterable[DcpSpan]) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for s in spans:
            counts[s.label] = counts.get(s.label, 0) + 1
        return counts