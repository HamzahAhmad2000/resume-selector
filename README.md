# Resume Selector MVP

End-to-end MVP that ingests PDF resumes, scores them against a job description using hybrid embeddings + hand-engineered features, and updates model weights online from recruiter feedback. The stack targets local Windows development with a Flask backend, SQLite persistence, and a Vite + React frontend styled with Tailwind and shadcn/ui.

## Architecture

- **Backend (Flask)**
  - PDF ingestion via `pypdf`, skill/year/education extraction, MiniLM embeddings, feature computation, and epsilon-greedy Top-K ranking.
  - Online pairwise logistic updates to model weights stored in SQLite along with resume/job metadata.
  - Endpoints for job creation, resume upload, ranking, feedback, and weight inspection with CORS for `http://localhost:5173` only.
- **Frontend (React + Vite + Tailwind + shadcn/ui)**
  - Workflows to create jobs, upload resumes, review ranked candidates with per-feature contributions, and send feedback.
  - Displays live model weights, supports epsilon control, and toasts for success/error states.
- **Data**
  - `backend/seed_samples.py` generates synthetic resumes and a JD PDF using `reportlab`, optionally posting them to the API.
  - Uploads are stored under `backend/uploads` (gitignored) and served via `/uploads/<filename>`.

## Repository Layout

```
.
├─ README.md
├─ docker-compose.yml
├─ backend/
│  ├─ app.py
│  ├─ requirements.txt
│  ├─ seed_samples.py
│  ├─ uploads/
│  ├─ tests/
│  │  └─ test_api_smoke.py
│  ├─ Dockerfile
│  └─ README.md
└─ frontend/
   ├─ index.html
   ├─ vite.config.ts
   ├─ tsconfig.json
   ├─ package.json
   ├─ postcss.config.js
   ├─ tailwind.config.ts
   ├─ src/
   │  ├─ main.tsx
   │  ├─ App.tsx
   │  ├─ lib/axios.ts
   │  ├─ components/
   │  ├─ pages/
   │  └─ __tests__/
   ├─ Dockerfile
   └─ README.md
```

## Features

- Semantic embeddings (MiniLM) + skill overlap + Jaccard + experience + education features.
- Preference-based reinforcement learning using pairwise logistic updates with persistence.
- Epsilon-greedy exploration in rankings and transparent per-feature contributions surfaced in the UI.
- Windows-friendly tooling, deterministic dependency versions, backend/ frontend Dockerfiles, and compose stack.

## Run Instructions (verbatim as requested)

- Prereqs: Python 3.10+, Node 20+, Windows 10/11.
- Backend:
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python app.py

nginx
Copy code
Backend runs at http://localhost:8000
- Frontend:
cd frontend
npm ci
npm run dev

java
Copy code
Frontend at http://localhost:5173

## Sample Workflow

1. Create a job via the backend form or API.
2. Upload one or more PDF resumes (≤10MB) to `/resumes`.
3. Fetch `/rankings?job_id=<id>&k=5&epsilon=0.1` to view candidates with feature attributions.
4. Select the best candidate from the UI (or via `/feedback`) to update weights in real time.

## CURL DEMO (verbatim)

1) Create Job
curl -X POST http://localhost:8000/jobs -H "Content-Type: application/json" -d "{"title":"ML Engineer","description":"We need an ML/AI engineer with Python, PyTorch, MLOps (Docker, K8s), and NLP experience. Prefer Masters+."}"

Copy code
2) Upload PDFs
curl -F "file=@samples/cv1.pdf" http://localhost:8000/resumes
curl -F "file=@samples/cv2.pdf" http://localhost:8000/resumes
curl -F "file=@samples/cv3.pdf" http://localhost:8000/resumes

sql
Copy code
3) Get rankings
curl "http://localhost:8000/rankings?job_id=1&k=5&epsilon=0.1"

Copy code
4) Feedback
curl -X POST http://localhost:8000/feedback -H "Content-Type: application/json" -d "{"job_id":1,"shown_candidate_ids":[1,2,3],"chosen_candidate_id":2}"

sql
Copy code

## Seed Sample PDFs

```
cd backend
python seed_samples.py --output samples
python seed_samples.py --upload --backend http://localhost:8000
```

## Testing

- Backend: `cd backend && pytest`
- Frontend: `cd frontend && npm test`

## Docker Compose

```
docker-compose up --build
```

The compose stack launches the backend on port 8000 and the frontend preview server on port 5173.

## Environment Notes

- Set `RESUME_SELECTOR_EMBEDDER=stub` to run the backend with a deterministic hashing embedder (useful for CI or offline testing). Without the override, the real MiniLM model loads locally (no network calls once cached).
- PDFs without extractable text return `400`; OCR is intentionally out of scope for the MVP.

## Roadmap Ideas

- Expand text extraction to include experience range parsing and project metadata.
- Persist job-specific hyper-parameters and exploration rates.
- Package the MiniLM model alongside the repository for fully offline bootstrap.
