FROM python:3.11-slim

# 1. Performance and Log optimizations
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/root/.local/bin:$PATH"
# Fixes the 'Read operation timed out' error
ENV POETRY_HTTP_TIMEOUT=300

# 2. Install minimal system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libmagic1 \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# 3. Install Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

WORKDIR /app

# 4. Install Python dependencies
COPY pyproject.toml poetry.lock* ./

# Optimization: Increase workers and disable keyring for headless Docker builds
RUN poetry config virtualenvs.create false \
    && poetry config installer.max-workers 10 \
    && poetry config keyring.enabled false \
    && poetry install --no-root --no-interaction --no-ansi

# 5. Copy application code
COPY . .

# 6. Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]