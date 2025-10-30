from __future__ import annotations

import json
from typing import Dict, List

import numpy as np

from ..embeddings import embed_text
from ..utils.extraction import jd_skills
from ..utils.vectors import blob_to_vector, feature_vector, normalize_skill_overlap, safe_cosine


def ensure_features(conn, job_id: int) -> List[Dict]:
    job = conn.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
    if job is None:
        return []

    job_embedding = blob_to_vector(job['embedding']) if job['embedding'] else embed_text(job['description'])
    job_skill_set = set(jd_skills(job['description']))

    candidates = conn.execute('SELECT * FROM candidates').fetchall()
    rows: List[Dict] = []
    for candidate in candidates:
        resume_embedding = blob_to_vector(candidate['embedding'])
        cosine = safe_cosine(job_embedding, resume_embedding)
        sem_sim = (cosine + 1.0) / 2.0
        skills = set(json.loads(candidate['skills']))
        overlap = float(len(job_skill_set & skills))
        union = len(job_skill_set | skills)
        jaccard = overlap / union if union else 0.0
        years_norm = min(float(candidate['years_exp']), 20.0) / 20.0
        edu_norm = min(max(int(candidate['edu_level']), 0), 4) / 4.0
        rows.append(
            {
                'job_id': job_id,
                'candidate_id': int(candidate['id']),
                'sem_sim': sem_sim,
                'skill_overlap_raw': overlap,
                'jaccard': jaccard,
                'years': years_norm,
                'edu': edu_norm,
            }
        )

    rows = normalize_skill_overlap(rows)
    for row in rows:
        conn.execute(
            '''
            INSERT INTO features (job_id, candidate_id, sem_sim, skill_overlap, jaccard, years, edu)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id, candidate_id) DO UPDATE SET
                sem_sim=excluded.sem_sim,
                skill_overlap=excluded.skill_overlap,
                jaccard=excluded.jaccard,
                years=excluded.years,
                edu=excluded.edu
            ''',
            (
                row['job_id'],
                row['candidate_id'],
                row['sem_sim'],
                row.get('skill_overlap', 0.0),
                row['jaccard'],
                row['years'],
                row['edu'],
            ),
        )
    conn.commit()
    return rows


def fetch_feature_vectors(conn, job_id: int, candidate_ids: List[int]) -> Dict[int, np.ndarray]:
    query_placeholders = ','.join(['?'] * len(candidate_ids))
    rows = conn.execute(
        f'SELECT candidate_id, sem_sim, skill_overlap, jaccard, years, edu FROM features WHERE job_id=? AND candidate_id IN ({query_placeholders})',
        (job_id, *candidate_ids),
    ).fetchall()
    vectors: Dict[int, np.ndarray] = {}
    for row in rows:
        vectors[int(row['candidate_id'])] = feature_vector(
            {
                'sem_sim': float(row['sem_sim']),
                'skill_overlap': float(row['skill_overlap']),
                'jaccard': float(row['jaccard']),
                'years': float(row['years']),
                'edu': float(row['edu']),
            }
        )
    return vectors
