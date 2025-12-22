from __future__ import annotations

from typing import List, Tuple, Dict, Any

from app.services.orchestrator import Orchestrator

# Singleton au module scope (1 seule fois par process)
_ORCH = Orchestrator()


class ImagePipeline:
    def __init__(self):
        # rien à faire ici (ou garde juste des options si tu veux)
        pass

    def ocr(self, image_path: str) -> str:
        import pytesseract
        from PIL import Image, ImageOps

        img = Image.open(image_path)
        img = ImageOps.exif_transpose(img)

        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        return pytesseract.image_to_string(img)

    def detect_image(
        self,
        image_path: str,
        language: str,
        detectors: List[str],
        min_score: float,
        merge_overlaps: bool = True,
        return_text: bool = True,
        best_effort: bool = True,
    ):
        text = self.ocr(image_path)

        # ⚠️ ici on utilise le singleton _ORCH
        return _ORCH.detect_text(
            text=text,
            language=language,
            detectors=detectors,
            min_score=min_score,
            merge_overlaps=merge_overlaps,
            return_text=return_text,
            best_effort=best_effort,
        )