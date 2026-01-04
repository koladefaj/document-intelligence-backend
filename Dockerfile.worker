FROM python:3.11-slim

# 1. Performance and Log optimizations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"
ENV POETRY_HTTP_TIMEOUT=300

# 2. Install dependencies + OLLAMA
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libmagic1 \
    poppler-utils \
    && curl -fsSL https://ollama.com/install.sh | sh \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# 4. Install Python dependencies
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-root --no-interaction --no-ansi

# 5. Copy application code
COPY . .

# 6. The "Magic" Command
# Starts Ollama, waits 5 seconds, pulls a tiny model, then starts your app
CMD sh -c "ollama serve & sleep 5 && ollama pull tinyllama && uvicorn app.main:app --host 0.0.0.0 --port 8000"