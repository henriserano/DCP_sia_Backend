from __future__ import annotations

import mimetypes
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

from app.connectors.base import Resource


class FileSystemConnector:
    """Local filesystem connector.

    root example:
      /Users/.../data
    uri format:
      file:///absolute/path
    """

    def list(self, root: str, *, recursive: bool = True) -> Iterable[Resource]:
        p = Path(root).expanduser().resolve()
        if not p.exists():
            return []

        files = p.rglob("*") if recursive else p.glob("*")
        out = []
        for f in files:
            if f.is_dir():
                continue
            uri = f"file://{str(f)}"
            kind = self._kind_from_suffix(f.suffix.lower())
            out.append(Resource(uri=uri, kind=kind, metadata={"name": f.name, "suffix": f.suffix}))
        return out

    def read_bytes(self, uri: str) -> bytes:
        path = self._to_path(uri)
        return path.read_bytes()

    def read_text(self, uri: str, *, encoding: str = "utf-8") -> str:
        path = self._to_path(uri)
        return path.read_text(encoding=encoding, errors="ignore")

    def write_bytes(self, uri: str, data: bytes) -> None:
        path = self._to_path(uri)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    @staticmethod
    def _to_path(uri: str) -> Path:
        if uri.startswith("file://"):
            uri = uri[len("file://") :]
        return Path(uri).expanduser().resolve()

    @staticmethod
    def _kind_from_suffix(suffix: str) -> str:
        if suffix in {".png", ".jpg", ".jpeg", ".webp", ".tiff"}:
            return "image"
        if suffix in {".pdf", ".docx", ".xlsx"}:
            return "document"
        if suffix in {".txt", ".md", ".log", ".csv", ".json"}:
            return "text"
        # fallback: try mimetypes
        mt, _ = mimetypes.guess_type("x" + suffix)
        if mt and mt.startswith("image/"):
            return "image"
        return "file"