########################
# 1) BUILDER
########################
FROM python:3.12-slim AS builder
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    HF_HUB_DISABLE_TELEMETRY=1 \
    TOKENIZERS_PARALLELISM=false

# Utilise les wheels CPU de torch (évite les downloads CUDA énormes)
ARG TORCH_CPU_INDEX=https://download.pytorch.org/whl/cpu
ENV PIP_EXTRA_INDEX_URL=${TORCH_CPU_INDEX}

# (optionnel) désactive le check de version pip
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Copier le code avant l'install pour que le package soit détecté
COPY app /app/app
COPY pyproject.toml /app/

# Install deps Python (layer stable)
RUN pip install -U pip && pip install --no-cache-dir . \
 && pip uninstall -y opencv-python opencv-contrib-python opencv-python-headless || true \
 && pip install --no-cache-dir "opencv-python-headless<4.9"

# Scripts nécessaires au download
COPY scripts /app/scripts

# Caches modèles (dans une zone dédiée)
ENV HF_HOME=/models/.hf \
    TRANSFORMERS_CACHE=/models/transformers \
    SENTENCE_TRANSFORMERS_HOME=/models/sentence_transformers

RUN mkdir -p /models

ARG PRELOAD_MODELS=0
# Pré-download HF models (optionnel : PRELOAD_MODELS=1)
RUN if [ "$PRELOAD_MODELS" = "1" ]; then python scripts/download_models.py; fi

# spaCy models (build-time)
RUN if [ "$PRELOAD_MODELS" = "1" ]; then \
      python -m spacy download en_core_web_sm && \
      python -m spacy download fr_core_news_sm; \
    fi


########################
# 2) RUNTIME
########################
FROM python:3.12-slim AS runtime
WORKDIR /app

# ✅ Réduction RAM / CPU au runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app \
    HF_HOME=/models/.hf \
    TRANSFORMERS_CACHE=/models/transformers \
    SENTENCE_TRANSFORMERS_HOME=/models/sentence_transformers \
    HF_HUB_DISABLE_TELEMETRY=1 \
    TOKENIZERS_PARALLELISM=false \
    # Torch / OpenMP: limite threads => moins de RAM + startup plus stable
    OMP_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    TORCH_NUM_THREADS=1

# Librairies système nécessaires pour PaddleOCR/OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    libglx-mesa0 \
    libglu1-mesa \
    libgomp1 \
 && rm -rf /var/lib/apt/lists/*

# Copier uniquement l'env python installé + modèles
COPY --from=builder /usr/local /usr/local
COPY --from=builder /models /models

# Copier le code (change souvent)
COPY app /app
COPY pyproject.toml /app/

# (Optionnel) healthcheck container-level (Cloud Run fait déjà ses checks HTTP)
# HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import socket; s=socket.socket(); s.connect(('127.0.0.1', int(__import__('os').environ.get('PORT','8080')))); s.close()"

EXPOSE 8080

# ✅ 1 worker, pas de reload, pas de trucs "dev"
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080} --workers 1 --timeout-keep-alive 5"]
