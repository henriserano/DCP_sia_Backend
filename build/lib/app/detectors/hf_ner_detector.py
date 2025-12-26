from __future__ import annotations
from typing import List, Dict
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class HFNerDetector(BaseDetector):
    name = "hf"

    def __init__(self, model: str = "Jean-Baptiste/camembert-ner", revision: str | None = None):
        """
        Tu peux remplacer par un modèle NER FR différent.
        """
        try:
            from transformers import pipeline
        except Exception as e:
            raise RuntimeError("Transformers non installé. Fais: pip install transformers torch") from e

        self.pipe = pipeline(
            "token-classification",
            model=model,
            revision=revision,                 # optionnel mais recommandé
            aggregation_strategy="simple",
            device=-1,                         # CPU (évite surprises)
            local_files_only=True,             # ✅ interdit tout download
        )

        # mapping BIO/NER -> DCP labels (best-effort)
        self.map: Dict[str, str] = {
            "PER": "PERSON",
            "LOC": "LOCATION",
            "ORG": "ORG",
            "MISC": "OTHER",
        }

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        out = self.pipe(text)
        spans: List[DcpSpan] = []
        for r in out:
            ent = r.get("entity_group") or r.get("entity") or "OTHER"
            label = self.map.get(ent, "OTHER")
            score = float(r.get("score", 0.5))
            start, end = int(r["start"]), int(r["end"])
            spans.append(
                DcpSpan(
                    start=start,
                    end=end,
                    label=label,  # type: ignore
                    score=score,
                    source=self.name,
                    text=text[start:end],
                    metadata={"hf_entity": ent},
                )
            )
        return spans