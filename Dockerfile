FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run with uv
CMD uv run python manage.py migrate && uv run gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
