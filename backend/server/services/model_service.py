from __future__ import annotations

from typing import Tuple

import numpy as np

from ..utils.time import now_iso


def get_weights(conn) -> np.ndarray:
    row = conn.execute(
        'SELECT w_sem, w_overlap, w_jaccard, w_years, w_edu FROM model_weights WHERE id=1'
    ).fetchone()
    return np.array([
        float(row['w_sem']),
        float(row['w_overlap']),
        float(row['w_jaccard']),
        float(row['w_years']),
        float(row['w_edu']),
    ], dtype=np.float32)


def get_hyperparams(conn) -> Tuple[float, float]:
    row = conn.execute('SELECT lr, l2 FROM model_weights WHERE id=1').fetchone()
    return float(row['lr']), float(row['l2'])


def set_weights(conn, weights: np.ndarray) -> None:
    conn.execute(
        'UPDATE model_weights SET w_sem=?, w_overlap=?, w_jaccard=?, w_years=?, w_edu=?, updated_at=? WHERE id=1',
        (
            float(weights[0]),
            float(weights[1]),
            float(weights[2]),
            float(weights[3]),
            float(weights[4]),
            now_iso(),
        ),
    )
    conn.commit()


def get_model_payload(conn) -> dict:
    row = conn.execute('SELECT * FROM model_weights WHERE id=1').fetchone()
    return {
        'weights': [
            float(row['w_sem']),
            float(row['w_overlap']),
            float(row['w_jaccard']),
            float(row['w_years']),
            float(row['w_edu']),
        ],
        'lr': float(row['lr']),
        'l2': float(row['l2']),
        'updated_at': row['updated_at'],
    }
