FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies to system Python (no venv needed in Docker)
RUN uv pip install --system -r pyproject.toml

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run directly with system Python
CMD python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-8000}
