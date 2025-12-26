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
        raise RuntimeError(f"Missing dependency: paddleocr. Install with: pip install paddleocr paddlepaddle==2.6.1 ({e})") from e

    # use_angle_cls improves orientation; keep defaults for det/rec.
    return PaddleOCR(use_angle_cls=True, lang=lang)


def _paddle_ocr(image_path: str, lang: str) -> str:
    ocr = _get_paddleocr(lang=lang)
    result = ocr.ocr(image_path, cls=True)
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
    """OCR helper with backend selection + graceful fallback."""
    settings = get_settings()
    backend = os.getenv("OCR_BACKEND", settings.ocr_backend).lower()
    lang = os.getenv("OCR_LANG", "fr")

    if backend in {"auto", "paddleocr"}:
        try:
            text = _paddle_ocr(image_path, lang=lang)
            if text:
                return text
        except Exception as e:  # pragma: no cover
            if backend == "paddleocr":
                raise
            logger.warning("paddleocr failed, falling back to tesseract", exc_info=e)

    # Fallback to pytesseract
    try:
        import pytesseract
        from PIL import Image, ImageOps
    except Exception as e:  # pragma: no cover
        raise RuntimeError("Missing OCR backend. Install: pip install paddleocr paddlepaddle==2.6.1 or pytesseract; ensure tesseract-ocr binary is present.") from e

    # Try to set TESSDATA_PREFIX automatically (common locations)
    if "TESSDATA_PREFIX" not in os.environ:
        for path in ("/usr/share/tesseract-ocr/5/tessdata", "/usr/share/tesseract-ocr/4.00/tessdata", "/usr/share/tesseract-ocr/tessdata"):
            if os.path.exists(path):
                os.environ["TESSDATA_PREFIX"] = path
                break

    # Map lang to tesseract code when needed
    tess_lang = {"fr": "fra", "en": "eng"}.get(lang, lang)

    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    try:
        return pytesseract.image_to_string(img, lang=tess_lang)
    except Exception:
        # Last resort: force english
        return pytesseract.image_to_string(img, lang="eng")
