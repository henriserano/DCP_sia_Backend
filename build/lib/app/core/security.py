from __future__ import annotations

import secrets
from typing import Optional

from fastapi import Depends, Header

from app.core.config import Settings, get_settings
from app.core.errors import Unauthorized


def _is_enabled(settings: Settings) -> bool:
    return bool(settings.enable_api_key and settings.api_keys)


def require_api_key(
    x_api_key: Optional[str] = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    """Optional API key guard.

    - Disabled by default.
    - Enable by setting:
        ENABLE_API_KEY=true
        API_KEYS='["my-secret-key"]'

    Note: Header name can be customized via settings.api_key_header, but keeping
    a single default simplifies client usage.
    """

    if not _is_enabled(settings):
        return

    if not x_api_key:
        raise Unauthorized("Missing API key")

    # constant-time comparison
    for k in settings.api_keys:
        if secrets.compare_digest(x_api_key, k):
            return

    raise Unauthorized("Invalid API key")