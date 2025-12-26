from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List
from app.models.schemas import DcpSpan

class BaseDetector(ABC):
    name: str

    @abstractmethod
    def detect(self, text: str, language: str = "fr") -> List[DcpSpan]:
        raise NotImplementedError