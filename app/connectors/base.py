from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Optional, Protocol


@dataclass(frozen=True)
class Resource:
    """A generic resource handled by connectors."""
    uri: str               # e.g. file:///... or s3://bucket/key or db://table/...
    kind: str              # file | image | document | record
    metadata: Dict[str, str] = None  # optional small metadata


class BaseConnector(Protocol):
    """Protocol for connectors (duck-typed)."""

    def list(self, root: str, *, recursive: bool = True) -> Iterable[Resource]:
        ...

    def read_bytes(self, uri: str) -> bytes:
        ...

    def read_text(self, uri: str, *, encoding: str = "utf-8") -> str:
        ...

    def write_bytes(self, uri: str, data: bytes) -> None:
        ...