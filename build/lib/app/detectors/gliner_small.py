from __future__ import annotations
from typing import List, Dict
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class GLiNERSmallDetector(BaseDetector):
    name = "gliner-small"

    def __init__(self, model: str = "vicgalle/gliner-small-pii"):
        """
        Modèle zéro-shot pour PII. Nécessite: pip install gliner
        """
        try:
            from gliner import GLiNER
        except Exception as e:
            raise RuntimeError("GLiNER non installé. Fais: pip install gliner") from e

        self.model = GLiNER.from_pretrained(model, load_tokenizer=True)
        
        # Labels PII à détecter (zéro-shot)
        self.labels = [
            "person", "company", "postal address", "phone number", "email", "SSN"
        ]
        
        # Mapping PII -> DCP labels
        self.map: Dict[str, str] = {
            "person": "PERSON",
            "company": "ORG",
            "postal address": "LOCATION",
            "phone number": "OTHER",  # Ou ajoute PHONE si ton schéma le supporte
            "email": "OTHER",
            "SSN": "OTHER",
        }

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        entities = self.model.predict_entities(text, self.labels, threshold=0.5)
        spans: List[DcpSpan] = []
        for ent in entities:
            label = self.map.get(ent["label"], "OTHER")
            score = float(ent.get("score", 0.5))
            start, end = int(ent["start"]), int(ent["end"])
            spans.append(
                DcpSpan(
                    start=start,
                    end=end,
                    label=label,
                    score=score,
                    source=self.name,
                    text=ent["text"],
                    metadata={"gliner_label": ent["label"]},
                )
            )
        return spans