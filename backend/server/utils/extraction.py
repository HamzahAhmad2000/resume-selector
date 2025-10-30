from __future__ import annotations

import re
from typing import Dict, List, Optional, Set, Tuple

from pypdf import PdfReader

SKILL_TERMS: Set[str] = {
    'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 'rust', 'sql',
    'flask', 'fastapi', 'django', 'node', 'node.js', 'express', 'graphql', 'rest', 'grpc',
    'nginx', 'redis', 'rabbitmq', 'kafka', 'pandas', 'numpy', 'scikit-learn', 'sklearn',
    'pytorch', 'tensorflow', 'transformers', 'nlp', 'cv', 'computer', 'computer-vision', 'yolo',
    'bert', 'docker', 'kubernetes', 'terraform', 'helm', 'aws', 'gcp', 'azure', 'spark', 'hadoop',
    'databricks', 'bigquery', 'snowflake', 'postgres', 'mysql', 'oauth2', 'jwt', 'rbac', 'git',
    'github', 'jenkins', 'github-actions', 'ci', 'cd', 'ansible', 'airflow', 'mlflow', 'mlops',
    'feature-engineering', 'powershell', 'bash', 'linux', 'prometheus', 'grafana'
}

PHRASE_SKILLS: Dict[str, str] = {
    'computer vision': 'computer',
    'feature engineering': 'feature-engineering',
    'github actions': 'github-actions',
    'integration testing': 'ci',
    'load testing': 'cd',
    'weights & biases': 'mlops',
    'machine learning ops': 'mlops',
    'node.js': 'node.js',
    'rest api': 'rest',
    'cloud watch': 'aws',
    'big query': 'bigquery'
}

SKILL_ALIASES: Dict[str, str] = {
    'c plus plus': 'c++',
    'c sharp': 'c#',
    'js': 'javascript',
    'ts': 'typescript',
    'postgresql': 'postgres',
    'google cloud': 'gcp',
    'amazon web services': 'aws',
    'microsoft azure': 'azure',
    'computervision': 'computer',
    'featureengineering': 'feature-engineering'
}

EDU_MAP = {
    'doctor': 4,
    'doctorate': 4,
    'phd': 4,
    'master': 3,
    'm.sc': 3,
    'msc': 3,
    'mtech': 3,
    'bachelor': 2,
    'bs': 2,
    'b.sc': 2,
    'bsc': 2,
    'btech': 2,
    'be': 2,
    'diploma': 1,
    'associate': 1
}


def read_pdf_text(path: str) -> str:
    try:
        reader = PdfReader(path)
        contents: List[str] = []
        for page in reader.pages:
            contents.append(page.extract_text() or '')
        return '\n'.join(contents)
    except Exception:
        return ''


def extract_years(text: str) -> float:
    years = 0.0
    lowered = text.lower()
    for match in re.finditer(r'(\d{1,2})\s*\+?\s*(?:years|yrs|y)\b', lowered):
        years = max(years, float(match.group(1)))
    span_years = re.findall(r'(19|20)\d{2}', lowered)
    if len(span_years) >= 2:
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
    email = ''
    phone = ''
    em = re.search(r'([\w\.-]+@[A-Za-z0-9\.-]+\.[A-Za-z]{2,})', text)
    if em:
        email = em.group(1).strip()
    ph = re.search(r'(\+?\d[\d\s\-]{7,}\d)', text)
    if ph:
        phone = ph.group(1).strip()
    return email, phone


def extract_name(text: str) -> str:
    for line in text.splitlines():
        clean = line.strip()
        if not clean or '@' in clean or len(clean) > 80:
            continue
        tokens = clean.split()
        if 1 <= len(tokens) <= 4 and all(tok and tok[0].isupper() for tok in tokens):
            return clean
    return 'Unknown'


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
