# Multi-stage build for Django + Vite (Lovable) assets

# 1) Frontend build stage (Node)
FROM node:20-alpine AS frontend
WORKDIR /app
# Only copy frontend to leverage Docker layer cache
COPY landing/static/landing/lovable/package*.json ./
RUN npm ci
COPY landing/static/landing/lovable/ ./
# Build with Vite
RUN npm run build

# 2) Python base stage
FROM python:3.13-slim AS python-base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# System deps (psycopg2, Pillow, etc.)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project
COPY . /app

# 3) Final runtime image
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# Runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy installed site-packages from builder
COPY --from=python-base /usr/local /usr/local
# Copy app
COPY --from=python-base /app /app

# Copy built frontend assets into Django static path
# Lovable output is at landing/static/landing/lovable/dist/assets
# We serve via STATIC_URL=/static/ and collectstatic (optional)
COPY --from=frontend /app/dist/assets /app/landing/static/landing/dist-assets/assets

# Django settings
ENV DJANGO_SETTINGS_MODULE=basejango.settings

# Ensure staticfiles exist; if whitenoise is used, collectstatic can be enabled
# Uncomment if you want collectstatic in build or run stage
# RUN python manage.py collectstatic --noinput

# Expose port (gunicorn default 8000)
EXPOSE 8000

# Gunicorn command
# Adjust workers based on CPU (e.g., 2-4) and timeouts as needed
CMD ["gunicorn", "basejango.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "120"]
