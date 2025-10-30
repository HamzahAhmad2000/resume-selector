FROM python:3.11-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV RESUME_SELECTOR_DB_PATH=/app/db.sqlite3 \
    RESUME_SELECTOR_EMBEDDER=transformer

EXPOSE 8000
CMD ["python", "app.py"]
