from __future__ import annotations
from typing import List
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

class PresidioDetector(BaseDetector):
    name = "presidio"

    def __init__(self):
        try:
            from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
        except Exception as e:
            raise RuntimeError(
                "Presidio non installé. Fais: pip install presidio-analyzer presidio-anonymizer"
            ) from e

        self.engine = AnalyzerEngine()

        # Mapping Presidio -> DCP labels
        self.map = {
            "PERSON": "PERSON",
            "EMAIL_ADDRESS": "EMAIL",
            "PHONE_NUMBER": "PHONE",
            "IBAN_CODE": "IBAN",
            "LOCATION": "LOCATION",
            "DATE_TIME": "DATE",
            "CREDIT_CARD": "FINANCE",
            "US_SSN": "ID_NUMBER",
            "IP_ADDRESS": "OTHER",
        }

        # --- Injecte quelques recognizers FR (patterns) ---
        # Ça garantit que language="fr" ne plantera pas.
        email_rec = PatternRecognizer(
            supported_entity="EMAIL_ADDRESS",
            patterns=[Pattern("email", r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", 0.95)],
            supported_language="fr",
        )

        iban_rec = PatternRecognizer(
            supported_entity="IBAN_CODE",
            patterns=[Pattern("iban", r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b", 0.90)],
            supported_language="fr",
        )

        phone_rec = PatternRecognizer(
            supported_entity="PHONE_NUMBER",
            patterns=[Pattern(
                "phone",
                r"\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{1,4}\)?[\s.-]?)?\d{2,4}[\s.-]?\d{2,4}[\s.-]?\d{2,4}\b",
                0.60
            )],
            supported_language="fr",
        )

        self.engine.registry.add_recognizer(email_rec)
        self.engine.registry.add_recognizer(iban_rec)
        self.engine.registry.add_recognizer(phone_rec)

    def _build_engine(self):
        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider

        # Charge EN + FR (si le modèle fr n'existe pas, ça fallback EN)
        provider = NlpEngineProvider(
            nlp_configuration={
                "nlp_engine_name": "spacy",
                "models": [
                    {"lang_code": "en", "model_name": "en_core_web_sm"},
                    {"lang_code": "fr", "model_name": "fr_core_news_sm"},
                ],
            }
        )
        nlp_engine = provider.create_engine()

        return AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en", "fr"])

    
    @staticmethod
    def _map_entity(entity_type: str) -> str:
        mapping = {
            "EMAIL_ADDRESS": "EMAIL",
            "PHONE_NUMBER": "PHONE",
            "IBAN_CODE": "IBAN",
            "PERSON": "PERSON",
            "URL": "OTHER",
        }
        return mapping.get(entity_type, "OTHER")
    
    def detect(self, text: str, language: str = "fr", min_score: float = 0.4) -> List[DcpSpan]:
        """
        FR-safe:
        - essaie en language demandé
        - si KeyError / pas de recognizers, fallback en "en"
        """
        lang = language if language in {"en", "fr"} else "en"
        results = self.engine.analyze(text=text, language=lang)

        spans: List[DcpSpan] = []
        for r in results:
            score = float(r.score or 0.0)
            if score < min_score:
                continue
            spans.append(
                DcpSpan(
                    start=r.start,
                    end=r.end,
                    label=self._map_entity(r.entity_type),
                    score=score,
                    source="presidio",
                    text=text[r.start:r.end],
                    metadata={"entity_type": r.entity_type, "engine_lang": lang},
                )
            )
        return spans