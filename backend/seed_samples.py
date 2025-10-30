"""Utility to generate sample job and resume PDFs for quick demos."""

from __future__ import annotations

import argparse
import json
import os
import pathlib
from dataclasses import dataclass
from typing import List

import requests
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas


@dataclass
class ResumeSpec:
    filename: str
    full_name: str
    email: str
    phone: str
    summary: str
    skills: List[str]
    experience: List[str]
    education: str


RESUMES = [
    ResumeSpec(
        filename="cv_ml_backend.pdf",
        full_name="Avery Johnson",
        email="avery.johnson@example.com",
        phone="(555) 555-1100",
        summary="Machine learning engineer shipping NLP systems at scale.",
        skills=[
            "Python",
            "PyTorch",
            "Transformers",
            "Docker",
            "Kubernetes",
            "MLflow",
            "AWS",
            "Jenkins",
        ],
        experience=[
            "Built BERT-based intent models improving accuracy by 18%",
            "Productionised training pipelines with MLflow and GitHub Actions",
            "Led migration to EKS using Terraform and Helm",
        ],
        education="M.S. Computer Science, Georgia Tech (2018)",
    ),
    ResumeSpec(
        filename="cv_data_platform.pdf",
        full_name="Jordan Patel",
        email="jordan.patel@example.com",
        phone="(555) 555-2200",
        summary="Data platform engineer focusing on Spark and real-time analytics.",
        skills=[
            "Python",
            "Scala",
            "Spark",
            "Kafka",
            "Airflow",
            "Docker",
            "GCP",
            "BigQuery",
        ],
        experience=[
            "Designed Kafka to BigQuery ingestion with 99.95% uptime",
            "Optimised Spark jobs cutting costs by 25%",
            "Implemented RBAC and OAuth2 controls across data platform",
        ],
        education="B.S. Electrical Engineering, UIUC (2016)",
    ),
    ResumeSpec(
        filename="cv_fullstack_ai.pdf",
        full_name="Morgan Lee",
        email="morgan.lee@example.com",
        phone="(555) 555-3300",
        summary="Full-stack engineer blending React, Flask, and ML APIs.",
        skills=[
            "JavaScript",
            "TypeScript",
            "React",
            "Flask",
            "FastAPI",
            "TensorFlow",
            "Redis",
            "Postgres",
        ],
        experience=[
            "Shipped resume parsing UI with React, Tailwind, and shadcn/ui",
            "Deployed FastAPI inference service on Azure Kubernetes Service",
            "Implemented CI/CD with GitHub Actions and pytest",
        ],
        education="B.S. Software Engineering, University of Waterloo (2017)",
    ),
]

JOB_DESCRIPTION = {
    "filename": "job_ml_engineer.pdf",
    "title": "Machine Learning Engineer",
    "description": (
        "We are hiring an ML engineer to build NLP applications with Python, "
        "PyTorch, Transformers, and MLOps tooling (Docker, Kubernetes, MLflow). "
        "Production experience on AWS and mentorship mindset preferred."
    ),
}

DEFAULT_BACKEND = "http://localhost:8000"


def write_pdf(path: pathlib.Path, header: str, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=LETTER)
    width, height = LETTER
    y = height - 72
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, header)
    y -= 32
    c.setFont("Helvetica", 11)
    for line in lines:
        if not line:
            y -= 16
            continue
        c.drawString(72, y, line)
        y -= 16
        if y < 72:
            c.showPage()
            y = height - 72
            c.setFont("Helvetica", 11)
    c.save()


def generate_samples(output_dir: pathlib.Path) -> List[pathlib.Path]:
    created: List[pathlib.Path] = []
    for resume in RESUMES:
        resume_path = output_dir / resume.filename
        lines = [
            resume.full_name,
            resume.email,
            resume.phone,
            "",
            "Summary:",
            resume.summary,
            "",
            "Skills: " + ", ".join(resume.skills),
            "",
            "Experience:",
        ] + resume.experience + ["", "Education:", resume.education]
        write_pdf(resume_path, resume.full_name, lines)
        created.append(resume_path)

    job_path = output_dir / JOB_DESCRIPTION["filename"]
    write_pdf(
        job_path,
        JOB_DESCRIPTION["title"],
        [
            JOB_DESCRIPTION["title"],
            "",
            JOB_DESCRIPTION["description"],
        ],
    )
    created.append(job_path)
    return created


def upload_to_backend(base_url: str, samples_dir: pathlib.Path) -> None:
    job_payload = {
        "title": JOB_DESCRIPTION["title"],
        "description": JOB_DESCRIPTION["description"],
    }
    resp = requests.post(f"{base_url}/jobs", json=job_payload, timeout=30)
    resp.raise_for_status()
    job_id = resp.json()["job_id"]
    print(f"Created job {job_id}")

    for resume in RESUMES:
        path = samples_dir / resume.filename
        with path.open("rb") as fh:
            up_resp = requests.post(
                f"{base_url}/resumes", files={"file": (resume.filename, fh, "application/pdf")}, timeout=60
            )
        up_resp.raise_for_status()
        data = up_resp.json()
        print(f"Uploaded {resume.filename} -> candidate {data['candidate_id']}")

    rank_resp = requests.get(f"{base_url}/rankings", params={"job_id": job_id, "k": 5, "epsilon": 0.0}, timeout=30)
    rank_resp.raise_for_status()
    print("Top candidates: ")
    for item in rank_resp.json().get("candidates", []):
        print(f"  - {item['full_name']} (score={item['score']:.3f})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate demo PDFs and optionally upload them")
    parser.add_argument(
        "--output",
        type=pathlib.Path,
        default=pathlib.Path(__file__).parent / "samples",
        help="Directory to store generated PDFs",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload generated PDFs to the running backend",
    )
    parser.add_argument(
        "--backend",
        default=DEFAULT_BACKEND,
        help="Backend base URL when using --upload (default: http://localhost:8000)",
    )
    args = parser.parse_args()

    created = generate_samples(args.output)
    print("Generated files:")
    for path in created:
        print(f"  - {path}")

    if args.upload:
        upload_to_backend(args.backend.rstrip("/"), args.output)


if __name__ == "__main__":
    main()
