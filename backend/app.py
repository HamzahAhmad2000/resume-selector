import datetime
import json
import math
import os
import random
import re
import sqlite3
import time
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
from pypdf import PdfReader

MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024
APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("RESUME_SELECTOR_DB_PATH", os.path.join(APP_DIR, "db.sqlite3"))
UPLOAD_DIR = os.path.join(APP_DIR, "uploads")
MODEL_MODE = os.environ.get("RESUME_SELECTOR_EMBEDDER", "transformer")

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)


@dataclass
class Embedder:
    """Wrapper to produce normalized sentence embeddings."""

    name: str

    def encode(self, texts: Iterable[str]) -> np.ndarray:
        raise NotImplementedError


def load_embedder() -> Embedder:
    mode = MODEL_MODE.lower()
    if mode == "stub":
        class Stub(Embedder):
            dim = 384

            def __init__(self) -> None:
                super().__init__(name="stub")

            def encode(self, texts: Iterable[str]) -> np.ndarray:
                vecs: List[np.ndarray] = []
                for text in texts:
                    tokens = re.findall(r"[a-z0-9]+", text.lower())
                    bucket = np.zeros(self.dim, dtype=np.float32)
                    for tok in tokens:
                        idx = hash(tok) % self.dim
                        bucket[idx] += 1.0
                    norm = np.linalg.norm(bucket)
                    if norm > 0:
                        bucket = bucket / norm
                    vecs.append(bucket)
                if not vecs:
                    return np.zeros((0, self.dim), dtype=np.float32)
                return np.stack(vecs, axis=0)

        return Stub()

    from sentence_transformers import SentenceTransformer

    class STEmbedder(Embedder):
        def __init__(self) -> None:
            super().__init__(name="sentence-transformers/all-MiniLM-L6-v2")
            self.model = SentenceTransformer(
                "sentence-transformers/all-MiniLM-L6-v2",
                device="cpu",
            )

        def encode(self, texts: Iterable[str]) -> np.ndarray:
            enc = self.model.encode(
                list(texts),
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
            return enc.astype(np.float32)

    return STEmbedder()


EMBEDDER = load_embedder()

SKILL_TERMS = {
    "python",
    "javascript",
    "typescript",
    "java",
    "c++",
    "c#",
    "go",
    "rust",
    "sql",
    "flask",
    "fastapi",
    "django",
    "node",
    "node.js",
    "express",
    "graphql",
    "rest",
    "grpc",
    "nginx",
    "redis",
    "rabbitmq",
    "kafka",
    "pandas",
    "numpy",
    "scikit-learn",
    "sklearn",
    "pytorch",
    "tensorflow",
    "transformers",
    "nlp",
    "cv",
    "computer",
    "computer-vision",
    "yolo",
    "bert",
    "docker",
    "kubernetes",
    "terraform",
    "helm",
    "aws",
    "gcp",
    "azure",
    "spark",
    "hadoop",
    "databricks",
    "bigquery",
    "snowflake",
    "postgres",
    "mysql",
    "oauth2",
    "jwt",
    "rbac",
    "git",
    "github",
    "jenkins",
    "github-actions",
    "ci",
    "cd",
    "ansible",
    "airflow",
    "mlflow",
    "mlops",
    "feature-engineering",
    "powershell",
    "bash",
    "linux",
    "prometheus",
    "grafana",
}

PHRASE_SKILLS: Dict[str, str] = {
    "computer vision": "computer",
    "feature engineering": "feature-engineering",
    "github actions": "github-actions",
    "integration testing": "ci",
    "load testing": "cd",
    "weights & biases": "mlops",
    "machine learning ops": "mlops",
    "node.js": "node.js",
    "rest api": "rest",
    "cloud watch": "aws",
    "big query": "bigquery",
}

SKILL_ALIASES: Dict[str, str] = {
    "c plus plus": "c++",
    "c sharp": "c#",
    "js": "javascript",
    "ts": "typescript",
    "postgresql": "postgres",
    "google cloud": "gcp",
    "amazon web services": "aws",
    "microsoft azure": "azure",
    "github actions": "github-actions",
    "computervision": "computer",
    "featureengineering": "feature-engineering",
}

EDU_MAP = {
    "doctor": 4,
    "doctorate": 4,
    "phd": 4,
    "master": 3,
    "m.sc": 3,
    "msc": 3,
    "mtech": 3,
    "bachelor": 2,
    "bs": 2,
    "b.sc": 2,
    "bsc": 2,
    "btech": 2,
    "be": 2,
    "diploma": 1,
    "associate": 1,
}


def now_iso() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_db()
    cur = conn.cursor()
    cur.executescript(
        """
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
    )
    existing = cur.execute("SELECT COUNT(*) AS c FROM model_weights").fetchone()["c"]
    if existing == 0:
        cur.execute(
            """
            INSERT INTO model_weights (id, w_sem, w_overlap, w_jaccard, w_years, w_edu, lr, l2, updated_at)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (0.50, 0.18, 0.10, 0.17, 0.05, 0.10, 1e-4, now_iso()),
        )
    conn.commit()
    conn.close()


def vector_to_blob(vec: np.ndarray) -> bytes:
    return vec.astype(np.float32).tobytes()


def blob_to_vector(blob: bytes) -> np.ndarray:
    return np.frombuffer(blob, dtype=np.float32)


def embed_text(text: str) -> np.ndarray:
    vec = EMBEDDER.encode([text])
    if vec.ndim == 1:
        return vec.astype(np.float32)
    return vec[0].astype(np.float32)


def safe_cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0:
        return 0.0
    val = float(np.dot(a, b) / denom)
    return max(-1.0, min(1.0, val))


def read_pdf_text(path: str) -> str:
    try:
        reader = PdfReader(path)
        chunks: List[str] = []
        for page in reader.pages:
            extracted = page.extract_text() or ""
            chunks.append(extracted)
        return "\n".join(chunks)
    except Exception:
        return ""


def extract_years(text: str) -> float:
    years = 0.0
    lowered = text.lower()
    for match in re.finditer(r"(\d{1,2})\s*\+?\s*(?:years|yrs|y)\b", lowered):
        years = max(years, float(match.group(1)))
    spans = re.findall(r"(19|20)\d{2}", lowered)
    if len(spans) >= 2:
        years = max(years, 20.0)
    return min(years, 20.0)


def extract_edu_level(text: str) -> int:
    lowered = text.lower()
    best = 0
    for key, value in EDU_MAP.items():
        if key in lowered:
            best = max(best, value)
    return best


def extract_contact(text: str) -> Tuple[str, str]:
    email = ""
    phone = ""
    em = re.search(r"([\w\.-]+@[A-Za-z0-9\.-]+\.[A-Za-z]{2,})", text)
    if em:
        email = em.group(1).strip()
    ph = re.search(r"(\+?\d[\d\s\-]{7,}\d)", text)
    if ph:
        phone = ph.group(1).strip()
    return email, phone


def extract_name(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip()
        if not clean:
            continue
        if "@" in clean:
            continue
        if len(clean) > 80:
            continue
        tokens = clean.split()
        if 1 <= len(tokens) <= 4 and all(tok[0].isupper() for tok in tokens if tok):
            return clean
    return "Unknown"


def tokenize(text: str) -> List[str]:
    return re.findall(r"[a-z0-9\+#\.\-]+", text.lower())


def normalise_skill(raw: str) -> Optional[str]:
    cleaned = raw.strip().lower()
    if cleaned in SKILL_TERMS:
        return cleaned
    if cleaned in SKILL_ALIASES:
        return SKILL_ALIASES[cleaned]
    return None


def extract_skills(text: str) -> List[str]:
    lowered = text.lower()
    found: List[str] = []
    for phrase, canonical in PHRASE_SKILLS.items():
        if phrase in lowered:
            found.append(canonical)

    tokens = set(tokenize(text))
    for token in tokens:
        skill = normalise_skill(token)
        if skill:
            found.append(skill)
    return sorted(set(found))


def jd_skills(description: str) -> List[str]:
    return extract_skills(description)


def normalize_skill_overlap(rows: List[Dict[str, float]]) -> List[Dict[str, float]]:
    if not rows:
        return rows
    min_val = min(row["skill_overlap_raw"] for row in rows)
    max_val = max(row["skill_overlap_raw"] for row in rows)
    denom = max(1.0, max_val - min_val)
    for row in rows:
        row["skill_overlap"] = (row["skill_overlap_raw"] - min_val) / denom
    return rows


def feature_vector(row: Dict[str, float]) -> np.ndarray:
    return np.array([
        row["sem_sim"],
        row["skill_overlap"],
        row["jaccard"],
        row["years"],
        row["edu"],
    ], dtype=np.float32)


def get_weights(conn: sqlite3.Connection) -> np.ndarray:
    row = conn.execute(
        "SELECT w_sem, w_overlap, w_jaccard, w_years, w_edu FROM model_weights WHERE id=1"
    ).fetchone()
    return np.array([
        float(row["w_sem"]),
        float(row["w_overlap"]),
        float(row["w_jaccard"]),
        float(row["w_years"]),
        float(row["w_edu"]),
    ], dtype=np.float32)


def get_hyperparams(conn: sqlite3.Connection) -> Tuple[float, float]:
    row = conn.execute("SELECT lr, l2 FROM model_weights WHERE id=1").fetchone()
    return float(row["lr"]), float(row["l2"])


def set_weights(conn: sqlite3.Connection, weights: np.ndarray) -> None:
    conn.execute(
        """
        UPDATE model_weights
        SET w_sem = ?, w_overlap = ?, w_jaccard = ?, w_years = ?, w_edu = ?, updated_at = ?
        WHERE id = 1
        """,
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


def ensure_features(job_id: int) -> List[Dict[str, float]]:
    conn = get_db()
    job = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    if job is None:
        conn.close()
        return []

    job_embedding = blob_to_vector(job["embedding"]) if job["embedding"] else embed_text(job["description"])
    job_skill_set = set(jd_skills(job["description"]))

    candidates = conn.execute("SELECT * FROM candidates").fetchall()
    rows: List[Dict[str, float]] = []
    for cand in candidates:
        cand_embedding = blob_to_vector(cand["embedding"])
        raw_cos = safe_cosine(job_embedding, cand_embedding)
        sem_sim = (raw_cos + 1.0) / 2.0
        skills = json.loads(cand["skills"])
        skill_overlap_raw = float(len(job_skill_set & set(skills)))
        union = len(job_skill_set | set(skills))
        jaccard = skill_overlap_raw / union if union else 0.0
        years_norm = min(float(cand["years_exp"]), 20.0) / 20.0
        edu_norm = min(max(int(cand["edu_level"]), 0), 4) / 4.0
        rows.append(
            {
                "job_id": job_id,
                "candidate_id": int(cand["id"]),
                "sem_sim": sem_sim,
                "skill_overlap_raw": skill_overlap_raw,
                "jaccard": jaccard,
                "years": years_norm,
                "edu": edu_norm,
            }
        )

    rows = normalize_skill_overlap(rows)
    for row in rows:
        conn.execute(
            """
            INSERT INTO features (job_id, candidate_id, sem_sim, skill_overlap, jaccard, years, edu)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(job_id, candidate_id) DO UPDATE SET
                sem_sim = excluded.sem_sim,
                skill_overlap = excluded.skill_overlap,
                jaccard = excluded.jaccard,
                years = excluded.years,
                edu = excluded.edu
            """,
            (
                row["job_id"],
                row["candidate_id"],
                row["sem_sim"],
                row.get("skill_overlap", 0.0),
                row["jaccard"],
                row["years"],
                row["edu"],
            ),
        )
    conn.commit()
    conn.close()
    return rows


def get_feature_rows(job_id: int) -> List[Dict[str, float]]:
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM features WHERE job_id=?",
        (job_id,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


class FeedbackPayload(BaseModel):
    job_id: int
    shown_candidate_ids: List[int]
    chosen_candidate_id: int


class JobPayload(BaseModel):
    title: str
    description: str


app = Flask(__name__)
CORS(app, origins=["http://localhost:5173"], supports_credentials=False)


@app.errorhandler(ValidationError)
def on_validation_error(err: ValidationError):
    return jsonify({"error": err.errors()}), 400


@app.route("/health", methods=["GET"])
def health() -> Tuple[str, int]:
    return jsonify({"ok": True}), 200


@app.route("/jobs", methods=["POST"])
def create_job() -> Tuple[str, int]:
    payload = JobPayload(**request.json)
    embedding = embed_text(payload.description)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO jobs (title, description, embedding, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (payload.title, payload.description, vector_to_blob(embedding), now_iso()),
    )
    job_id = cur.lastrowid
    conn.commit()
    conn.close()
    return jsonify({"job_id": int(job_id)}), 200


@app.route("/resumes", methods=["POST"])
def upload_resume() -> Tuple[str, int]:
    storage = request.files.get("file")
    if storage is None:
        return jsonify({"error": "file is required"}), 400
    if storage.mimetype not in {"application/pdf", "application/x-pdf", "binary/octet-stream"}:
        return jsonify({"error": "only PDF files are accepted"}), 400
    stream = storage.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    if size > MAX_FILE_SIZE_BYTES:
        return jsonify({"error": "file too large (10MB limit)"}), 400
    timestamp = int(time.time() * 1000)
    safe_name = re.sub(r"[^A-Za-z0-9_.-]", "_", storage.filename or "resume.pdf")
    filename = f"{timestamp}_{safe_name}"
    path = os.path.join(UPLOAD_DIR, filename)
    storage.save(path)

    text = read_pdf_text(path)
    if not text.strip():
        os.remove(path)
        return jsonify({"error": "could not extract text from PDF"}), 400

    email, phone = extract_contact(text)
    name = extract_name(text)
    years_exp = extract_years(text)
    edu_level = extract_edu_level(text)
    skills = extract_skills(text)
    embedding = embed_text(text)

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO candidates (full_name, email, phone, pdf_path, text, embedding, years_exp, edu_level, skills, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            email,
            phone,
            path,
            text,
            vector_to_blob(embedding),
            years_exp,
            edu_level,
            json.dumps(skills),
            now_iso(),
        ),
    )
    candidate_id = cur.lastrowid
    conn.commit()
    conn.close()

    return (
        jsonify(
            {
                "candidate_id": int(candidate_id),
                "full_name": name,
                "email": email,
                "phone": phone,
                "skills": skills,
                "years_exp": years_exp,
                "edu_level": edu_level,
            }
        ),
        200,
    )


def expand_features(job_id: int) -> List[Dict[str, float]]:
    ensure_features(job_id)
    conn = get_db()
    rows = conn.execute(
        """
        SELECT f.*, c.full_name, c.email, c.phone, c.skills, c.years_exp, c.edu_level
        FROM features f
        JOIN candidates c ON f.candidate_id = c.id
        WHERE f.job_id = ?
        """,
        (job_id,),
    ).fetchall()
    conn.close()
    expanded: List[Dict[str, float]] = []
    for row in rows:
        data = dict(row)
        skills = json.loads(data.pop("skills"))
        expanded.append(
            {
                "candidate_id": int(data["candidate_id"]),
                "sem_sim": float(data["sem_sim"]),
                "skill_overlap": float(data["skill_overlap"]),
                "jaccard": float(data["jaccard"]),
                "years": float(data["years"]),
                "edu": float(data["edu"]),
                "full_name": data["full_name"],
                "email": data["email"],
                "phone": data["phone"],
                "skills": skills,
                "years_exp": float(data["years_exp"]),
                "edu_level_raw": int(data["edu_level"]),
            }
        )
    return expanded


@app.route("/rankings", methods=["GET"])
def rankings() -> Tuple[str, int]:
    job_id = request.args.get("job_id")
    if job_id is None:
        return jsonify({"error": "job_id is required"}), 400
    try:
        job_id_int = int(job_id)
    except ValueError:
        return jsonify({"error": "job_id must be an integer"}), 400

    k = int(request.args.get("k", 5))
    epsilon = float(request.args.get("epsilon", 0.1))
    ensure_features(job_id_int)
    conn = get_db()
    feature_rows = conn.execute(
        """
        SELECT f.*, c.full_name, c.email, c.phone, c.skills, c.years_exp, c.edu_level
        FROM features f
        JOIN candidates c ON c.id = f.candidate_id
        WHERE f.job_id = ?
        """,
        (job_id_int,),
    ).fetchall()

    weights = get_weights(conn)
    conn.close()

    candidates: List[Dict[str, object]] = []
    for row in feature_rows:
        skills = json.loads(row["skills"])
        features = {
            "sem_sim": float(row["sem_sim"]),
            "skill_overlap": float(row["skill_overlap"]),
            "jaccard": float(row["jaccard"]),
            "years": float(row["years"]),
            "edu": float(row["edu"]),
        }
        vector = feature_vector(features)
        score = float(np.dot(weights, vector))
        candidates.append(
            {
                "candidate_id": int(row["candidate_id"]),
                "full_name": row["full_name"],
                "email": row["email"],
                "phone": row["phone"],
                "skills": skills,
                "years_exp": float(row["years_exp"]),
                "edu_level_raw": int(row["edu_level"]),
                "sem_sim": features["sem_sim"],
                "skill_overlap": features["skill_overlap"],
                "jaccard": features["jaccard"],
                "years": features["years"],
                "edu": features["edu"],
                "score": score,
            }
        )

    rng = random.Random()
    explore = False
    if candidates:
        if len(candidates) > k and rng.random() < max(0.0, min(1.0, epsilon)):
            explore = True
            rng.shuffle(candidates)
            candidates = candidates[:k]
        else:
            candidates.sort(key=lambda item: item["score"], reverse=True)
            candidates = candidates[:k]
    for cand in candidates:
        cand["explore"] = explore

    return jsonify({"job_id": job_id_int, "weights": weights.tolist(), "candidates": candidates}), 200


@app.route("/feedback", methods=["POST"])
def feedback() -> Tuple[str, int]:
    payload = FeedbackPayload(**request.json)
    ensure_features(payload.job_id)

    if not payload.shown_candidate_ids:
        return jsonify({"error": "shown_candidate_ids must contain at least one id"}), 400
    if payload.chosen_candidate_id not in payload.shown_candidate_ids:
        return jsonify({"error": "chosen_candidate_id must be among shown_candidate_ids"}), 400

    conn = get_db()
    rows = conn.execute(
        "SELECT candidate_id, sem_sim, skill_overlap, jaccard, years, edu FROM features WHERE job_id=? AND candidate_id IN (%s)"
        % ",".join(["?"] * len(payload.shown_candidate_ids)),
        (payload.job_id, *payload.shown_candidate_ids),
    ).fetchall()
    feature_map: Dict[int, np.ndarray] = {}
    for row in rows:
        feature_map[int(row["candidate_id"])] = feature_vector({
            "sem_sim": float(row["sem_sim"]),
            "skill_overlap": float(row["skill_overlap"]),
            "jaccard": float(row["jaccard"]),
            "years": float(row["years"]),
            "edu": float(row["edu"]),
        })

    if len(feature_map) != len(payload.shown_candidate_ids):
        conn.close()
        return jsonify({"error": "missing feature vectors for provided candidate ids"}), 400

    weights = get_weights(conn)
    lr, l2 = get_hyperparams(conn)
    winner_vec = feature_map[payload.chosen_candidate_id]
    updates = 0

    for cid in payload.shown_candidate_ids:
        if cid == payload.chosen_candidate_id:
            continue
        loser_vec = feature_map[cid]
        delta = winner_vec - loser_vec
        logit = float(np.dot(weights, delta))
        prob = 1.0 / (1.0 + math.exp(-logit))
        gradient = (1.0 - prob) * delta - l2 * weights
        weights = weights + lr * gradient
        conn.execute(
            """
            INSERT INTO pairwise_prefs (job_id, winner_candidate_id, loser_candidate_id, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (payload.job_id, payload.chosen_candidate_id, cid, now_iso()),
        )
        updates += 1

    set_weights(conn, weights)
    conn.commit()
    conn.close()
    return jsonify({"updated_pairs": updates, "new_weights": weights.tolist()}), 200


@app.route("/models", methods=["GET"])
def get_model_weights() -> Tuple[str, int]:
    conn = get_db()
    row = conn.execute("SELECT * FROM model_weights WHERE id=1").fetchone()
    conn.close()
    return (
        jsonify(
            {
                "weights": [
                    float(row["w_sem"]),
                    float(row["w_overlap"]),
                    float(row["w_jaccard"]),
                    float(row["w_years"]),
                    float(row["w_edu"]),
                ],
                "lr": float(row["lr"]),
                "l2": float(row["l2"]),
                "updated_at": row["updated_at"],
            }
        ),
        200,
    )


@app.route("/uploads/<path:filename>", methods=["GET"])
def serve_upload(filename: str):
    return send_from_directory(UPLOAD_DIR, filename, as_attachment=False)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
