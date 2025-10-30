# Repository Guidelines

## Project Structure & Module Organization
The repository is still being scaffolded; as you add code, adopt the layout below and update this guide if the structure evolves.
- `src/` contains the Python package `resume_selector`. Place ingestion helpers under `src/resume_selector/ingest/`, scoring heuristics under `src/resume_selector/scoring/`, and orchestration logic in `src/resume_selector/pipelines/`.
- `tests/` mirrors the package layout. Co-locate fixtures in `tests/fixtures/` and keep golden files in `tests/data/`.
- `data/` stores anonymised sample resumes and job descriptions used in demos. Never commit PII; scrub metadata before pushing.
- `assets/` gathers UI wireframes, prompt templates, and reference screenshots.
- `scripts/` hosts repeatable maintenance tasks (dataset refresh, batch scoring) with executable permissions.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` creates and activates an isolated environment.
- `pip install -r requirements.txt` installs pinned runtime and tooling dependencies.
- `python -m resume_selector.cli --resume-dir data/resumes --job data/jobs/sample.json` runs the selector locally against sample inputs.
- `pytest` executes the full automated test suite; prefer `pytest tests/pipelines` for focused runs.

## Coding Style & Naming Conventions
Use Python 3.11+, four-space indentation, and comprehensive type hints. Run `black src tests` (88 character line length) and `ruff check src tests` before committing. Adopt snake_case for modules and functions, PascalCase for classes, and suffix abstract strategy classes with `Strategy`. Keep prompt files in Markdown with the naming pattern `prompt_<topic>.md`.

## Testing Guidelines
Write fast unit tests for scoring rules and slower integration tests for pipeline orchestration. Name files `test_<module>.py`, and prefer `Test<ClassName>` test classes. Achieve ≥90% line coverage reported via `pytest --cov=resume_selector --cov-report=term-missing`. Store reusable fixtures under `tests/fixtures/conftest.py` and document dataset assumptions alongside golden files.

## Commit & Pull Request Guidelines
Follow Conventional Commits (e.g., `feat:` for new scoring logic, `fix:` for bug fixes, `chore:` for build updates). Limit commits to a single logical change and include brief context in the body when touching data or prompts. Pull requests should describe the change, link relevant issues, attach before/after CLI output or screenshots, and note any follow-up tasks. Ensure CI green and lint/tests executed locally before requesting review.

## Security & Configuration Tips
Keep credentials and API keys in a local `.env` file and load them via environment variables; add `.env` to `.gitignore` the moment it is created. Sanitize sample resumes before sharing and prefer hashed identifiers over emails. Validate third-party model prompts in isolated branches before merging to main.
