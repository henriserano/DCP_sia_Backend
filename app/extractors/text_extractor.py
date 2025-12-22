from __future__ import annotations

import mimetypes
from pathlib import Path

from app.extractors.base import BaseExtractor, ExtractResult, normalize_path


class TextExtractor:
    name = "text"
    supported_suffixes = {".txt", ".md", ".log", ".csv", ".json", ".yaml", ".yml"}

    def can_extract(self, path: str) -> bool:
        p = normalize_path(path)
        return p.is_file() and p.suffix.lower() in self.supported_suffixes

    def extract(self, path: str) -> ExtractResult:
        p = normalize_path(path)
        text = p.read_text(encoding="utf-8", errors="ignore")
        return ExtractResult(
            text=text,
            source_path=str(p),
            mime=mimetypes.guess_type(str(p))[0],
            metadata={"extractor": self.name},
        )