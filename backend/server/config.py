import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / 'uploads'
DB_PATH = Path(os.environ.get('RESUME_SELECTOR_DB_PATH', BASE_DIR / 'db.sqlite3'))
EMBEDDER_MODE = os.environ.get('RESUME_SELECTOR_EMBEDDER', 'transformer')
ALLOWED_ORIGINS = ['http://localhost:5173']
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
