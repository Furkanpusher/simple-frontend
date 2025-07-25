# Dockerfile POETRY VE PYPROJECT.TOML İLE TÜM KÜTÜPHANELERİ İNDİRMEYE ÇALIŞIR


FROM python:3.10.0-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=1
ENV POETRY_CACHE_DIR=/tmp/poetry_cache

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy Poetry files
COPY pyproject.toml poetry.lock* ./

# Configure Poetry and install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root \
    && rm -rf $POETRY_CACHE_DIR

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs 

# bu porta ulaşabilmemizi sağlar
EXPOSE 8001

# Sağlık kontrolü her 30 saniyede bir olur, 5 saniyede bir alır ve 3 kez başarısız olursa iptal eder
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8001/health || exit 1


# FASTAPI Serveri başlatıyorum 8001. portta
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001", "--reload"]