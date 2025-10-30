from __future__ import annotations

import json
import random
from typing import Dict, List

import numpy as np

from ..database import db_connection
from ..services.feature_service import ensure_features
from ..services.model_service import get_weights
from ..utils.vectors import feature_vector


def fetch_rankings(job_id: int, k: int, epsilon: float) -> Dict:
    with db_connection() as conn:
        ensure_features(conn, job_id)
        rows = conn.execute(
            '''
            SELECT f.*, c.full_name, c.email, c.phone, c.skills, c.years_exp, c.edu_level
            FROM features f
            JOIN candidates c ON c.id = f.candidate_id
            WHERE f.job_id = ?
            ''',
            (job_id,),
        ).fetchall()
        weights = get_weights(conn)

    candidates: List[Dict] = []
    for row in rows:
        features = {
            'sem_sim': float(row['sem_sim']),
            'skill_overlap': float(row['skill_overlap']),
            'jaccard': float(row['jaccard']),
            'years': float(row['years']),
            'edu': float(row['edu']),
        }
        vec = feature_vector(features)
        score = float(np.dot(weights, vec))
        candidates.append(
            {
                'candidate_id': int(row['candidate_id']),
                'full_name': row['full_name'],
                'email': row['email'],
                'phone': row['phone'],
                'skills': json.loads(row['skills']),
                'years_exp': float(row['years_exp']),
                'edu_level_raw': int(row['edu_level']),
                **features,
                'score': score,
            }
        )

    explore = False
    if candidates:
        rng = random.Random()
        if len(candidates) > k and rng.random() < max(0.0, min(1.0, epsilon)):
            explore = True
            rng.shuffle(candidates)
            candidates = candidates[:k]
        else:
            candidates.sort(key=lambda item: item['score'], reverse=True)
            candidates = candidates[:k]

    for candidate in candidates:
        candidate['explore'] = explore

    return {
        'weights': weights.tolist(),
        'candidates': candidates,
    }
