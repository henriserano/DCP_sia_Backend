from __future__ import annotations

import os
from functools import lru_cache
from typing import Any

from app.core.logging import get_logger
from app.core.config import get_settings

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_paddleocr(lang: str = "fr"):
    """Load PaddleOCR once per process (CPU)."""
    os.environ.setdefault("DISABLE_MODEL_SOURCE_CHECK", "True")
    try:
        from paddleocr import PaddleOCR
    except Exception as e:  # pragma: no cover
        logger.error("paddleocr import failed", exc_info=e)
        raise RuntimeError(f"PaddleOCR import failed: {e}")

    # use_angle_cls improves orientation; keep defaults for det/rec.
    return PaddleOCR(use_angle_cls=True, lang=lang)


def _paddle_ocr(image_path: str, lang: str) -> str:
    ocr = _get_paddleocr(lang=lang)
    # API (paddleocr 3.3.x): cls est géré à l'init, pas en argument.
    result = ocr.ocr(image_path)
    texts = []
    for page in result:
        for line in page:
            if not line or len(line) < 2:
                continue
            txt = line[1][0]
            if isinstance(txt, str):
                texts.append(txt)
    return "\n".join(texts).strip()


def run_ocr(image_path: str) -> str:
    """OCR helper (PaddleOCR only)."""
    settings = get_settings()
    backend = os.getenv("OCR_BACKEND", settings.ocr_backend).lower()
    lang = os.getenv("OCR_LANG", "fr")

    if backend not in {"auto", "paddleocr"}:
        raise RuntimeError(f"OCR_BACKEND must be 'paddleocr' or 'auto', got {backend}")

    try:
        return _paddle_ocr(image_path, lang=lang)
    except Exception as e:
        logger.exception("PaddleOCR failed", exc_info=e)
        raise RuntimeError(f"PaddleOCR failed: {e}") from e
