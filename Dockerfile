# Use a slim Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy the project files
COPY . .

# Install dependencies using uv
RUN uv pip install --system -r requirements.txt

# Create necessary directories
RUN mkdir -p resources ontology experiment

# Default command: show help or list scripts
CMD ["python3", "-c", "print('llm-clean environment ready. Use docker run -it --env-file .env <image> bash to explore.')"]
