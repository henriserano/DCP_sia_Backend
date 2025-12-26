from __future__ import annotations
from typing import List, Dict, Optional
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class PiiranhaDetector(BaseDetector):
    name = "piiranha"

    def __init__(
        self,
        model: str = "iiiorg/piiranha-v1-detect-personal-information",
        label_map: Optional[Dict[str, str]] = None,
        device: int = -1,  # cpu par défaut (Cloud Run)
    ):
        try:
            from transformers import pipeline
        except Exception as e:
            raise RuntimeError("Transformers non installé. Fais: pip install transformers torch") from e

        self.pipe = pipeline(
            "token-classification",
            model=model,
            aggregation_strategy="simple",
            device=device,
        )

        self.map = label_map or {
            "GIVENNAME": "PERSON",
            "SURNAME": "PERSON",
            "PERSON": "PERSON",
            "LOCATION": "LOCATION",
            "ORGANIZATION": "ORG",
            "EMAIL": "OTHER",
            "TELEPHONENUM": "OTHER",
            "SSN": "OTHER",
        }

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        out = self.pipe(text)
        spans: List[DcpSpan] = []
        for r in out:
            ent = r.get("entity_group") or r.get("entity") or "OTHER"
            label = self.map.get(ent, "OTHER")
            start, end = int(r["start"]), int(r["end"])
            spans.append(
                DcpSpan(
                    start=start,
                    end=end,
                    label=label,
                    score=float(r.get("score", 0.5)),
                    source=self.name,
                    text=text[start:end],
                    metadata={"pii_type": ent},  # <-- granularité conservée ici
                )
            )
        return spans