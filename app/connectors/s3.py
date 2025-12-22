from __future__ import annotations

from typing import Iterable
from app.connectors.base import Resource


class S3Connector:
    """S3 connector (optional).
    uri format: s3://bucket/key
    """

    def __init__(self, *, region: str | None = None):
        try:
            import boto3
        except Exception as e:
            raise RuntimeError("Missing boto3. Install with: pip install boto3") from e
        self.s3 = boto3.client("s3", region_name=region)

    def list(self, root: str, *, recursive: bool = True) -> Iterable[Resource]:
        # root example: s3://my-bucket/prefix/
        bucket, prefix = self._parse(root)
        paginator = self.s3.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                key = obj["Key"]
                if key.endswith("/"):
                    continue
                yield Resource(uri=f"s3://{bucket}/{key}", kind="file", metadata={"key": key})

    def read_bytes(self, uri: str) -> bytes:
        bucket, key = self._parse(uri)
        obj = self.s3.get_object(Bucket=bucket, Key=key)
        return obj["Body"].read()

    def read_text(self, uri: str, *, encoding: str = "utf-8") -> str:
        return self.read_bytes(uri).decode(encoding, errors="ignore")

    def write_bytes(self, uri: str, data: bytes) -> None:
        bucket, key = self._parse(uri)
        self.s3.put_object(Bucket=bucket, Key=key, Body=data)

    @staticmethod
    def _parse(uri: str) -> tuple[str, str]:
        if not uri.startswith("s3://"):
            raise ValueError("S3 uri must start with s3://")
        rest = uri[len("s3://") :]
        bucket, _, key = rest.partition("/")
        return bucket, key