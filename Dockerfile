FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Déps système (à ajuster selon tes libs: ex poppler, tesseract, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# Copie d'abord les métadonnées + le code minimal requis pour installer (cache Docker)
COPY pyproject.toml /app/
COPY app /app/app
COPY scripts /app/scripts

RUN pip install -U pip && pip install .

# Puis le reste (si tu as d'autres fichiers: README, configs, etc.)
COPY . /app

# Cache HF dans le conteneur (NE PAS versionner côté git)
ENV HF_HOME=/app/.hf_cache

# Pré-download HF model(s) dans l’image (si tu assumes la taille)
RUN python scripts/download_models.py
# Installer spaCy models (pas via pyproject)
RUN python -m spacy download en_core_web_sm \
 && python -m spacy download fr_core_news_sm
# Cloud Run injecte PORT (8080 par défaut) : ton process doit écouter dessus
# (0.0.0.0 obligatoire)
# ...
EXPOSE 8080
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]