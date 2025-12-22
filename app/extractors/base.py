from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional, Protocol


@dataclass
class ExtractResult:
    """Standard output of any extractor."""
    text: str
    source_path: str
    mime: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)


class BaseExtractor(Protocol):
    """Extractor contract (duck-typed)."""

    name: str
    supported_suffixes: set[str]

    def can_extract(self, path: str) -> bool:
        ...

    def extract(self, path: str) -> ExtractResult:
        ...


def normalize_path(path: str) -> Path:
    return Path(path).expanduser().resolve()