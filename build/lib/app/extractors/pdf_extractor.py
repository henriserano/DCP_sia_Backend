from __future__ import annotations

from app.extractors.base import BaseExtractor, ExtractResult, normalize_path


class PdfExtractor:
    name = "pdf"
    supported_suffixes = {".pdf"}

    def can_extract(self, path: str) -> bool:
        p = normalize_path(path)
        return p.is_file() and p.suffix.lower() in self.supported_suffixes

    def extract(self, path: str) -> ExtractResult:
        p = normalize_path(path)
        try:
            import pdfplumber
        except Exception as e:
            raise RuntimeError("pdfplumber not installed. Install with: pip install pdfplumber") from e

        parts: list[str] = []
        with pdfplumber.open(str(p)) as pdf:
            for i, page in enumerate(pdf.pages):
                parts.append(page.extract_text() or "")

        return ExtractResult(
            text="\n".join(parts).strip(),
            source_path=str(p),
            mime="application/pdf",
            metadata={"extractor": self.name, "pages": str(len(parts))},
        )