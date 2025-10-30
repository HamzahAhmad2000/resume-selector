from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from .config import DB_PATH


def _now_iso() -> str:
    from datetime import datetime

    return datetime.utcnow().replace(microsecond=0).isoformat() + 'Z'

SCHEMA_SQL = """
PRAGMA journal_mode=WAL;
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    embedding BLOB NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT,
    email TEXT,
    phone TEXT,
    pdf_path TEXT NOT NULL,
    text TEXT NOT NULL,
    embedding BLOB NOT NULL,
    years_exp REAL NOT NULL,
    edu_level INTEGER NOT NULL,
    skills TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS features (
    job_id INTEGER NOT NULL,
    candidate_id INTEGER NOT NULL,
    sem_sim REAL NOT NULL,
    skill_overlap REAL NOT NULL,
    jaccard REAL NOT NULL,
    years REAL NOT NULL,
    edu REAL NOT NULL,
    PRIMARY KEY(job_id, candidate_id)
);
CREATE TABLE IF NOT EXISTS pairwise_prefs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER NOT NULL,
    winner_candidate_id INTEGER NOT NULL,
    loser_candidate_id INTEGER NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS model_weights (
    id INTEGER PRIMARY KEY CHECK(id=1),
    w_sem REAL NOT NULL,
    w_overlap REAL NOT NULL,
    w_jaccard REAL NOT NULL,
    w_years REAL NOT NULL,
    w_edu REAL NOT NULL,
    lr REAL NOT NULL,
    l2 REAL NOT NULL,
    updated_at TEXT NOT NULL
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_connection() -> Iterator[sqlite3.Connection]:
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    with db_connection() as conn:
        conn.executescript(SCHEMA_SQL)
        existing = conn.execute('SELECT COUNT(*) as c FROM model_weights').fetchone()['c']
        if existing == 0:
            conn.execute(
                'INSERT INTO model_weights (id, w_sem, w_overlap, w_jaccard, w_years, w_edu, lr, l2, updated_at) VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)',
                (0.50, 0.18, 0.10, 0.17, 0.05, 0.10, 1e-4, _now_iso()),
            )
            conn.commit()
