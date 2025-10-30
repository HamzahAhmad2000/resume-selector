from __future__ import annotations

import json
import os
import re
import time
from typing import Dict

from werkzeug.datastructures import FileStorage

from ..config import MAX_FILE_SIZE_BYTES, UPLOAD_DIR
from ..database import db_connection
from ..embeddings import embed_text
from ..utils.extraction import (
    extract_contact,
    extract_edu_level,
    extract_name,
    extract_skills,
    extract_years,
    read_pdf_text,
)
from ..utils.time import now_iso
from ..utils.vectors import vector_to_blob

ALLOWED_MIME_TYPES = {'application/pdf', 'application/x-pdf', 'binary/octet-stream'}


def validate_file(storage: FileStorage) -> None:
    if storage.mimetype not in ALLOWED_MIME_TYPES:
        raise ValueError('only PDF files are accepted')
    stream = storage.stream
    stream.seek(0, os.SEEK_END)
    size = stream.tell()
    stream.seek(0)
    if size > MAX_FILE_SIZE_BYTES:
        raise ValueError('file too large (10MB limit)')


def _persist_file(storage: FileStorage) -> str:
    timestamp = int(time.time() * 1000)
    safe_name = re.sub(r'[^A-Za-z0-9_.-]', '_', storage.filename or 'resume.pdf')
    filename = f'{timestamp}_{safe_name}'
    path = UPLOAD_DIR / filename
    storage.save(path)
    return str(path)


def ingest_resume(storage: FileStorage) -> Dict:
    validate_file(storage)
    path = _persist_file(storage)
    text = read_pdf_text(path)
    if not text.strip():
        os.remove(path)
        raise ValueError('could not extract text from PDF')

    email, phone = extract_contact(text)
    full_name = extract_name(text)
    years_exp = extract_years(text)
    edu_level = extract_edu_level(text)
    skills = extract_skills(text)
    embedding = embed_text(text)

    with db_connection() as conn:
        cursor = conn.execute(
            '''
            INSERT INTO candidates (full_name, email, phone, pdf_path, text, embedding, years_exp, edu_level, skills, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                full_name,
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
        conn.commit()
        candidate_id = int(cursor.lastrowid)

    return {
        'candidate_id': candidate_id,
        'full_name': full_name,
        'email': email,
        'phone': phone,
        'skills': skills,
        'years_exp': years_exp,
        'edu_level': edu_level,
    }
