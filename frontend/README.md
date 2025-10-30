# Frontend Client

React + Vite dashboard for the resume selector. Provides flows to create jobs, upload PDF resumes, review Top-K rankings, and send preference feedback.

## Prerequisites

- Node.js 20+
- Backend running locally on `http://localhost:8000`

## Install & Run

```powershell
cd frontend
npm ci
npm run dev
```

Then open http://localhost:5173 in the browser.

## Testing

```powershell
cd frontend
npm test
```

Vitest runs a smoke test that renders the ranking workflow with mocked API calls.

## Build

```powershell
cd frontend
npm run build
```

Static assets are emitted to `dist/` and can be served with `npm run preview`.

## Docker

```powershell
cd frontend
docker build -t resume-frontend .
docker run --rm -p 5173:5173 resume-frontend
```

The container serves the Vite preview server on port 5173.
