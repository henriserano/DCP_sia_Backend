FROM python:3.12-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_DISABLE_TELEMETRY=1

# Déps systèmes uniquement si nécessaires (git seulement si tu en as besoin pour pip)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
 && rm -rf /var/lib/apt/lists/*

# 1) Installer deps python d'abord (cache friendly)
COPY pyproject.toml /app/
# (si tu as un lock : poetry.lock / uv.lock / requirements.lock -> copie-le ici aussi)

# BuildKit cache pip (si BuildKit activé)
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -U pip && pip install .

# 2) Copier seulement scripts nécessaires au download
COPY scripts /app/scripts

# Emplacement modèles dans l'image
ENV HF_HOME=/models/.hf \
    TRANSFORMERS_CACHE=/models/transformers \
    SENTENCE_TRANSFORMERS_HOME=/models/sentence_transformers \
    TOKENIZERS_PARALLELISM=false

RUN mkdir -p /models

# Pré-download HF models
RUN --mount=type=cache,target=/models/.hf \
    python scripts/download_models.py

# spaCy models : les installer à build time
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m spacy download en_core_web_sm && \
    python -m spacy download fr_core_news_sm


########################
# 2) RUNTIME
########################
FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HOME=/models/.hf \
    TRANSFORMERS_CACHE=/models/transformers \
    SENTENCE_TRANSFORMERS_HOME=/models/sentence_transformers \
    HF_HUB_DISABLE_TELEMETRY=1 \
    TOKENIZERS_PARALLELISM=false

# Copier l'env python + modèles depuis builder
COPY --from=builder /usr/local /usr/local
COPY --from=builder /models /models

# Copier ton code en dernier (change souvent => n’invalide pas les layers lourds)
COPY app /app/app
COPY scripts /app/scripts
# Si tu as d'autres fichiers nécessaires au runtime :
COPY pyproject.toml /app/
# (évite COPY . /app si possible, ça embarque trop de choses)

EXPOSE 8080
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}"]