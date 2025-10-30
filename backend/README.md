# Backend Service

Flask API providing resume ingestion, feature extraction, ranking, and online preference learning. The service persists to SQLite and exposes REST endpoints under port 8000.

## Quickstart

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The app stores uploads in `backend/uploads`, creates `backend/db.sqlite3`, and exposes `http://localhost:8000`.

Set `RESUME_SELECTOR_EMBEDDER=stub` to run with a lightweight hashing embedder (useful for tests or when the transformer model is unavailable). Leave unset for the real `sentence-transformers/all-MiniLM-L6-v2` model (requires one-time download).

## Seed Synthetic PDFs

```powershell
cd backend
python seed_samples.py --output samples
python seed_samples.py --upload --backend http://localhost:8000
```

The script generates three synthetic resumes plus a job description under `backend/samples/`. With `--upload` it creates a job, uploads the resumes, and prints the ranking response.

## API Surface

- `GET /health` – service heartbeat
- `POST /jobs` – create a job (`{title, description}`)
- `POST /resumes` – upload a PDF resume (`multipart/form-data`)
- `GET /rankings` – compute rankings (`job_id`, optional `k`, `epsilon`)
- `POST /feedback` – update weights from recruiter choice
- `GET /models` – inspect current weights
- `GET /uploads/<filename>` – retrieve uploaded PDF

## Testing

```powershell
cd backend
pytest
```

Tests run against an isolated SQLite file and stub embeddings.

## Docker

```powershell
cd backend
docker build -t resume-backend .
docker run --rm -p 8000:8000 resume-backend
```

The Docker image runs `python app.py` with port 8000 exposed.
