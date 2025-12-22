FROM python:3.12-slim

WORKDIR /app

# (optionnel mais utile) deps système
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
# si tu as un lock (uv/poetry) adapte ici
RUN pip install -U pip && pip install .

COPY . /app

# Pré-download HF model dans l'image
ENV HF_HOME=/app/.hf_cache
RUN python scripts/download_models.py

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]