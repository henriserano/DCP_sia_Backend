from __future__ import annotations
from typing import List
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class SpacyDetector(BaseDetector):
    name = "spacy"

    def __init__(self, model: str = "fr_core_news_sm"):
        try:
            import spacy
        except Exception as e:
            raise RuntimeError("spaCy non installé. Fais: pip install spacy") from e

        self.nlp = spacy.load(model)

        # mapping spaCy labels -> DCP labels (best-effort)
        self.map = {
            "PER": "PERSON",
            "PERSON": "PERSON",
            "LOC": "LOCATION",
            "GPE": "LOCATION",
            "ORG": "ORG",
            "DATE": "DATE",
            "TIME": "DATE",
            "MONEY": "FINANCE",
        }

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        doc = self.nlp(text)
        spans: List[DcpSpan] = []
        for ent in doc.ents:
            label = self.map.get(ent.label_, "OTHER")
            # spaCy ne donne pas un "score" standard par entité → heuristique
            spans.append(
                DcpSpan(
                    start=ent.start_char,
                    end=ent.end_char,
                    label=label,      # type: ignore
                    score=0.55,
                    source=self.name,
                    text=ent.text,
                    metadata={"spacy_label": ent.label_},
                )
            )
        return spans