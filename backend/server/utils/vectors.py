from __future__ import annotations

import numpy as np


def vector_to_blob(vec: np.ndarray) -> bytes:
    return vec.astype(np.float32).tobytes()


def blob_to_vector(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def safe_cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    value = float(np.dot(a, b) / denom)
    return max(-1.0, min(1.0, value))


def feature_vector(row: dict) -> np.ndarray:
    return np.array([
        row['sem_sim'],
        row['skill_overlap'],
        row['jaccard'],
        row['years'],
        row['edu'],
    ], dtype=np.float32)


def normalize_skill_overlap(rows: list[dict]) -> list[dict]:
    if not rows:
        return rows
    min_val = min(row['skill_overlap_raw'] for row in rows)
    max_val = max(row['skill_overlap_raw'] for row in rows)
    denom = max(1.0, max_val - min_val)
    for row in rows:
        row['skill_overlap'] = (row['skill_overlap_raw'] - min_val) / denom
    return rows
