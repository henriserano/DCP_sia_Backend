from __future__ import annotations

from app.extractors.base import BaseExtractor, ExtractResult, normalize_path


class ImageOcrExtractor:
    """OCR extractor for images.

    Requires:
      pip install pillow pytesseract
    And system install:
      - macOS: brew install tesseract
      - ubuntu: apt-get install tesseract-ocr
    """

    name = "image_ocr"
    supported_suffixes = {".png", ".jpg", ".jpeg", ".webp", ".tiff", ".bmp"}

    def can_extract(self, path: str) -> bool:
        p = normalize_path(path)
        return p.is_file() and p.suffix.lower() in self.supported_suffixes

    def extract(self, path: str) -> ExtractResult:
        p = normalize_path(path)
        try:
            import pytesseract
            from PIL import Image
        except Exception as e:
            raise RuntimeError("OCR deps missing. Install: pip install pillow pytesseract") from e

        img = Image.open(str(p))
        text = pytesseract.image_to_string(img)

        return ExtractResult(
            text=(text or "").strip(),
            source_path=str(p),
            mime="image/*",
            metadata={"extractor": self.name},
        )