# Docker Setup Guide

## Prerequisites

### 1. Configure environment variables

Docker Compose reads from your `.env` file. Make sure you have one:

```bash
# Copy the example
cp .env.example .env

# Edit .env and set your credentials:
# POSTGRES_USER=postgres
# POSTGRES_PASSWORD=your_password
# POSTGRES_DB=citation_generator_db
```

**Important:** The `.env` file is gitignored - your credentials stay local!

## Quick Start

### 1. Start the application with Docker Compose

```bash
docker-compose up --build
```

This will:
- Build the backend and frontend Docker images
- Start PostgreSQL database
- Run migrations automatically
- Start the FastAPI backend on http://localhost:8000
- Start the React frontend on http://localhost:3000

### 2. Access the application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

### 3. Stop the application

```bash
docker-compose down
```

To also remove volumes (database data):
```bash
docker-compose down -v
```

## Common Commands

```bash
# Build without starting
docker-compose build

# Start in detached mode (background)
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Run tests inside container
docker-compose exec backend pytest tests/ -v

# Access backend shell
docker-compose exec backend bash

# Access frontend shell
docker-compose exec frontend sh

# Run migrations manually
docker-compose exec backend alembic upgrade head

# Restart a service
docker-compose restart backend
docker-compose restart frontend
```

## How Environment Variables Work

### Development (docker-compose.yml)

Docker Compose reads from your `.env` file:

```env
# .env (NOT committed to git)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=citation_generator_db
ENVIRONMENT=development
```

The `docker-compose.yml` uses these with fallback defaults:

```yaml
POSTGRES_USER: ${POSTGRES_USER:-postgres}
POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-postgres}
```

This means:
- ✅ Uses value from `.env` if set
- ✅ Falls back to `postgres` if not set (for quick testing)
- ✅ **Your credentials are NOT hardcoded in docker-compose.yml**
- ✅ **Safe to commit docker-compose.yml to git**

### Production

For production, use a separate `.env.docker` file:

```bash
cp .env.docker.example .env.docker
# Edit with production credentials
docker-compose --env-file .env.docker up -d
```

## Troubleshooting

### Port already in use
If port 5432 or 8000 is already in use:
```bash
# Change ports in docker-compose.yml
ports:
  - "5433:5432"  # Use 5433 on host instead
```

### Database connection issues
```bash
# Check postgres is healthy
docker-compose ps

# View postgres logs
docker-compose logs postgres
```

### Rebuild from scratch
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

## Production Deployment

For production, use a separate docker-compose file:

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

Remember to:
- Use strong passwords
- Enable SSL for PostgreSQL
- Configure proper health checks
- Set up backup strategies
- Use secrets management
