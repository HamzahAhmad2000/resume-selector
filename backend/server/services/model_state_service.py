from __future__ import annotations

from ..database import db_connection
from .model_service import get_model_payload


def fetch_model_state() -> dict:
    with db_connection() as conn:
        return get_model_payload(conn)
