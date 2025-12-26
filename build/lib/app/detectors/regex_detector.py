from __future__ import annotations
import re
from typing import List
from app.detectors.base import BaseDetector
from app.models.schemas import DcpSpan

EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)

# IBAN (simple, robuste pour FR/EU; tu peux renforcer avec checksum ensuite)
IBAN = re.compile(r"\b[A-Z]{2}\d{2}[A-Z0-9]{11,30}\b")

PHONE = re.compile(r"""
\b(?:\+?\d{1,3}[\s.-]?)?(?:\(?\d{1,4}\)?[\s.-]?)?\d{2,4}[\s.-]?\d{2,4}[\s.-]?\d{2,4}\b
""", re.VERBOSE)

class RegexDetector(BaseDetector):
    name = "regex"

    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        spans: List[DcpSpan] = []

        for m in EMAIL.finditer(text):
            spans.append(
                DcpSpan(
                    start=m.start(),
                    end=m.end(),
                    label="EMAIL",
                    score=0.95,
                    source=self.name,
                    text=m.group(0),
                )
            )

        for m in IBAN.finditer(text):
            spans.append(
                DcpSpan(
                    start=m.start(),
                    end=m.end(),
                    label="IBAN",
                    score=0.90,
                    source=self.name,
                    text=m.group(0),
                )
            )

        return spans