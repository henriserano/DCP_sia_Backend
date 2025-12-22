from __future__ import annotations

from fastapi import Depends

from app.core.security import require_api_key

# Utilisation:
# router = APIRouter(dependencies=[Depends(auth_guard)])
def auth_guard():
    return Depends(require_api_key)