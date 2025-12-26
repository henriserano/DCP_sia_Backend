"""Connectors provide a unified way to access data sources (filesystems, S3, DB...)."""

from app.connectors.base import BaseConnector, Resource
from app.connectors.filesystem import FileSystemConnector

__all__ = ["BaseConnector", "Resource", "FileSystemConnector"]