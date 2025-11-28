# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for PostgreSQL and curl for healthcheck
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    python3-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run app (tables are created automatically in main.py when ENVIRONMENT != ci)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
