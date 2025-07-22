FROM python:3.10.12-slim

WORKDIR /app/

ARG POETRY_VERSION=1.8.1
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=0 \
    PIP_NO_CACHE_DIR=1 \ 
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DEFAULT_TIMEOUT=3000

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir poetry==${POETRY_VERSION}

COPY pyproject.toml poetry.lock ./

RUN poetry install --only main --no-root --no-cache

COPY src .

EXPOSE 8000
