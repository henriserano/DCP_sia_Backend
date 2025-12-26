from __future__ import annotations

from functools import lru_cache
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_olmocr(model_id: str = "allenai/olmOCR-2-7B-1025"):
    """Load olmOCR once per process (CPU by default)."""
    try:
        from olmocr import OLMOCR
    except Exception as e:  # pragma: no cover
        logger.error("olmocr import failed", exc_info=e)
        raise RuntimeError(f"Missing dependency: olmocr. Install with: pip install olmocr ({e})") from e

    # CPU-first to stay Cloud Run friendly; dtype auto for safety.
    try:
        return OLMOCR.from_pretrained(model_id, device="cpu", dtype="auto")
    except TypeError:
        # Fallback if this signature changes.
        return OLMOCR.from_pretrained(model_id)


def run_ocr(image_path: str) -> str:
    """OCR helper that normalizes output to plain text."""
    model = _get_olmocr()
    out: Any = model.process_image(image_path)
    if isinstance(out, str):
        return out
    if isinstance(out, dict):
        for key in ("text", "output", "content"):
            if key in out and isinstance(out[key], str):
                return out[key]
    return str(out or "").strip()
