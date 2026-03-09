# llm-clean — reproducible research image
#
# Build:
#   docker build -t llm-clean .
#
# Run full reproduction (API key passed at runtime, never baked in):
#   docker run --rm \
#     -e OPENROUTER_API_KEY=sk-xxx \
#     -v $(pwd)/output:/app/output \
#     llm-clean
#
# Run a specific step only:
#   docker run --rm \
#     -e OPENROUTER_API_KEY=sk-xxx \
#     -v $(pwd)/output:/app/output \
#     llm-clean --multi-critic
#
# Interactive shell:
#   docker run --rm -it \
#     -e OPENROUTER_API_KEY=sk-xxx \
#     -v $(pwd)/output:/app/output \
#     llm-clean bash

FROM python:3.12-slim

# Reproducibility: pin uv version
ARG UV_VERSION=0.6.6

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src:/app \
    PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install pinned uv
RUN curl -LsSf "https://astral.sh/uv/${UV_VERSION}/install.sh" | sh

# Copy dependency manifests first (layer cache: only reinstalls when deps change)
COPY pyproject.toml uv.lock ./

# Install all dependencies from the lockfile (no network calls for packages)
RUN uv sync --frozen --no-dev

# Copy the rest of the project (source, scripts, data, resources)
# .dockerignore excludes .env, __pycache__, .git, etc.
COPY . .

# Ensure output directories exist
RUN mkdir -p data/raw output/ontologies output/experiments \
             output/analyzed_entities output/evaluation_results docs/reports

# Default: reproduce all steps (API key must be provided at runtime via -e)
ENTRYPOINT ["bash", "reproduce.sh"]
CMD ["--all"]
