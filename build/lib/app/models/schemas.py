from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Literal, Optional

DcpType = Literal[
    "PERSON", "EMAIL", "PHONE", "IBAN", "ADDRESS", "LOCATION",
    "ID_NUMBER", "DATE", "FINANCE", "HEALTH", "ORG", "OTHER"
]


class DcpSpan(BaseModel):
    start: int
    end: int
    label: DcpType
    score: float = Field(ge=0, le=1)
    source: str
    text: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DetectTextRequest(BaseModel):
    text: str
    language: str = "fr"
    detectors: List[str] = Field(default_factory=lambda: ["regex", "presidio", "spacy", "hf"])
    min_score: float = 0.4
    return_text: bool = True
    merge_overlaps: bool = True
    best_effort: bool = True


class DetectTextResponse(BaseModel):
    spans: List[DcpSpan]
    by_detector: Dict[str, List[DcpSpan]]
    summary: Dict[str, int]
    errors: Dict[str, str] = Field(default_factory=dict)


class BenchTextRequest(BaseModel):
    text: str
    language: str = "fr"
    detectors: List[str] = Field(default_factory=lambda: ["regex", "presidio", "spacy", "hf"])
    min_score: float = 0.4


class AnonymizeTextRequest(BaseModel):
    text: str
    language: str = "fr"
    detectors: List[str] = Field(default_factory=lambda: ["regex", "presidio", "spacy", "hf"])
    min_score: float = 0.4
    merge_overlaps: bool = True
    strategy: Literal["mask", "redact", "hash"] = "redact"


class AnonymizeTextResponse(BaseModel):
    anonymized_text: str
    spans: List[DcpSpan]
    summary: Dict[str, int]


class DetectStructuredRequest(BaseModel):
    obj: Any
    language: str = "fr"
    detectors: List[str] = Field(default_factory=lambda: ["regex", "presidio", "spacy", "hf"])
    min_score: float = 0.4


class ScanRequest(BaseModel):
    # Pour l’instant on supporte surtout le filesystem local (POC)
    connector: Literal["filesystem"] = "filesystem"
    root: str
    recursive: bool = True
    language: str = "fr"
    detectors: List[str] = Field(default_factory=lambda: ["regex", "presidio", "spacy", "hf"])
    min_score: float = 0.4
    limit: int = 200  # limite POC


class ScanResponse(BaseModel):
    scanned: int
    results: List[Dict[str, Any]]
    summary: Dict[str, int]