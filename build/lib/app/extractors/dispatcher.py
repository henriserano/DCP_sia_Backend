from __future__ import annotations

import mimetypes
from typing import List, Optional

from app.extractors.base import BaseExtractor, ExtractResult


class ExtractorDispatcher:
    """Select the best extractor for a given file path."""

    def __init__(self, extractors: Optional[List[BaseExtractor]] = None):
        # default registry
        from app.extractors.text_extractor import TextExtractor
        from app.extractors.pdf_extractor import PdfExtractor
        from app.extractors.docx_extractor import DocxExtractor
        from app.extractors.xlsx_extractor import XlsxExtractor
        from app.extractors.ocr_extractor import ImageOcrExtractor

        self.extractors: List[BaseExtractor] = extractors or [
            PdfExtractor(),
            DocxExtractor(),
            XlsxExtractor(),
            ImageOcrExtractor(),
            TextExtractor(),  # keep last as fallback for .txt/.md/.csv/.json etc.
        ]

    def extract(self, path: str) -> ExtractResult:
        for ex in self.extractors:
            if ex.can_extract(path):
                res = ex.extract(path)
                if not res.mime:
                    res.mime = mimetypes.guess_type(path)[0]
                return res
        raise RuntimeError(f"No extractor found for: {path}")