FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Install uv dari image resmi Astral
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install dependencies terlebih dahulu untuk caching layer Docker
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache

# Salin seluruh kode aplikasi
COPY . .

# Jalankan collectstatic pada saat build image
RUN uv run python manage.py collectstatic --noinput

# Buat user non-root untuk keamanan kontainer
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/media /app/staticfiles && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

# Jalankan dengan Gunicorn mendengarkan port dari $PORT (default 8000)
CMD ["sh", "-c", "uv run gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers 3"]
