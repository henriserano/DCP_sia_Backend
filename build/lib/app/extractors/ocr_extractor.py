from __future__ import annotations

from app.extractors.base import BaseExtractor, ExtractResult, normalize_path


class ImageOcrExtractor:
    """OCR extractor for images.

    Requires:
      pip install olmocr
    """

    name = "image_ocr"
    supported_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}

    def can_extract(self, path: str) -> bool:
        p = normalize_path(path)
        return p.is_file() and p.suffix.lower() in self.supported_suffixes

    def extract(self, path: str) -> ExtractResult:
        p = normalize_path(path)
        from app.services.ocr import run_ocr

        text = run_ocr(str(p))

        return ExtractResult(
            text=(text or "").strip(),
            source_path=str(p),
            mime="image/*",
            metadata={"extractor": self.name},
        )
