from __future__ import annotations

from ..database import db_connection
from ..embeddings import embed_text
from ..utils.time import now_iso
from ..utils.vectors import vector_to_blob


def create_job(title: str, description: str) -> int:
    embedding = embed_text(description)
    with db_connection() as conn:
        cur = conn.execute(
            'INSERT INTO jobs (title, description, embedding, created_at) VALUES (?, ?, ?, ?)',
            (title, description, vector_to_blob(embedding), now_iso()),
        )
        conn.commit()
        return int(cur.lastrowid)
