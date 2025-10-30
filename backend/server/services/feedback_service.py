from __future__ import annotations

import math
from typing import Dict, List

import numpy as np

from ..database import db_connection
from ..services.feature_service import ensure_features, fetch_feature_vectors
from ..services.model_service import get_hyperparams, get_weights, set_weights
from ..utils.time import now_iso


def apply_feedback(job_id: int, shown_ids: List[int], chosen_id: int) -> Dict:
    if not shown_ids:
        raise ValueError('shown_candidate_ids must contain at least one id')
    if chosen_id not in shown_ids:
        raise ValueError('chosen_candidate_id must be among shown_candidate_ids')

    with db_connection() as conn:
        ensure_features(conn, job_id)
        feature_map = fetch_feature_vectors(conn, job_id, shown_ids)
        if len(feature_map) != len(shown_ids):
            missing = sorted(set(shown_ids) - set(feature_map))
            raise ValueError(f'missing feature vectors for candidates {missing}')

        weights = get_weights(conn)
        lr, l2 = get_hyperparams(conn)
        winner_vec = feature_map[chosen_id]
        updates = 0

        for cid in shown_ids:
            if cid == chosen_id:
                continue
            loser_vec = feature_map[cid]
            delta = winner_vec - loser_vec
            logit = float(np.dot(weights, delta))
            prob = 1.0 / (1.0 + math.exp(-logit))
            gradient = (1.0 - prob) * delta - l2 * weights
            weights = weights + lr * gradient
            conn.execute(
                'INSERT INTO pairwise_prefs (job_id, winner_candidate_id, loser_candidate_id, created_at) VALUES (?, ?, ?, ?)',
                (job_id, chosen_id, cid, now_iso()),
            )
            updates += 1

        set_weights(conn, weights)
        conn.commit()

    return {
        'updated_pairs': updates,
        'new_weights': weights.tolist(),
    }
