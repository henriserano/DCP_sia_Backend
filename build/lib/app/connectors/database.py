from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple


class DatabaseConnector:
    """DB connector (optional) using SQLAlchemy.

    You can use it to fetch rows for profiling / DCP detection.
    """

    def __init__(self, sqlalchemy_session):
        self.db = sqlalchemy_session

    def fetch(self, query: str, params: Optional[Dict[str, Any]] = None, limit: int = 1000) -> List[Dict[str, Any]]:
        from sqlalchemy import text

        res = self.db.execute(text(query), params or {})
        rows = res.fetchmany(limit)
        cols = res.keys()
        out: List[Dict[str, Any]] = []
        for r in rows:
            out.append({c: r[i] for i, c in enumerate(cols)})
        return out