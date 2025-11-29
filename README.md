# Citation Generator

A full-stack web application for generating bibliographic citations in APA and MLA formats. Built with FastAPI (Python), React (TypeScript), PostgreSQL, and includes monitoring with Prometheus and Grafana.

## Quick Start (Docker - Recommended)

### Prerequisites
- Docker and Docker Compose installed

### Run the Application

```bash
# 1. Clone the repository
git clone https://github.com/catebros/citation-generator.git
cd citation-generator

# 2. Copy environment file
cp .env.example .env

# 3. Start all services (backend, frontend, database, monitoring)
docker-compose up -d

# 4. Access the application
# - Frontend:        http://localhost:3000
# - Backend API:     http://localhost:8000
# - API Docs:        http://localhost:8000/docs
# - Grafana:         http://localhost:3001 (admin/admin)
# - Prometheus:      http://localhost:9090
```

### Stop the Application

```bash
# Stop all containers
docker-compose down

# Stop and remove all data (database, metrics)
docker-compose down -v
```

---

## Architecture

### Tech Stack
- **Backend**: FastAPI (Python 3.11), SQLAlchemy, Alembic
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **Database**: PostgreSQL 15
- **Monitoring**: Prometheus, Grafana
- **Deployment**: Docker, Azure App Service, GitHub Actions

### Services

| Service | Port | Description |
|---------|------|-------------|
| Frontend | 3000 | React application |
| Backend | 8000 | FastAPI REST API |
| PostgreSQL | 5432 | Database |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Metrics visualization |

---

## Development

### Project Structure

```
citation-generator/
├── backend/                    # FastAPI backend
│   ├── alembic/               # Database migrations
│   ├── config/                # Configuration
│   ├── db/                    # Database setup
│   ├── models/                # SQLAlchemy models
│   ├── repositories/          # Data access layer
│   ├── routers/               # API routes
│   ├── services/              # Business logic
│   ├── tests/                 # Test suite
│   └── main.py                # Application entry point
├── frontend/                   # React frontend
│   ├── src/
│   │   ├── api/              # API client
│   │   ├── components/       # React components
│   │   ├── hooks/            # Custom hooks
│   │   ├── pages/            # Page components
│   │   └── types/            # TypeScript types
│   └── public/               # Static assets
├── monitoring/                # Monitoring configuration
│   ├── grafana/              # Grafana dashboards
│   └── prometheus/           # Prometheus config
├── .github/workflows/        # CI/CD pipelines
├── docker-compose.yml        # Local development
└── README.md                 # This file
```

### Local Development Commands

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec postgres psql -U postgres -d citation_generator_db

# Check service health
docker-compose ps
curl http://localhost:8000/health
```

---

## Testing

### Run Backend Tests

```bash
# Run all tests with coverage
docker-compose exec backend pytest tests/ -v --cov=. --cov-report=term

# Run specific test file
docker-compose exec backend pytest tests/test_citation_service.py -v

# Check coverage threshold (70% minimum)
docker-compose exec backend coverage report --fail-under=70
```

**Note**: Always use `pytest` to run tests. The test suite uses `conftest.py` fixtures for database isolation. Running tests individually with `python test_xxx.py` will bypass these fixtures.

---

## Database Management

### Migrations with Alembic

Alembic is properly configured and runs automatically when you start the Docker containers.

```bash
# Check current migration version
docker-compose exec backend alembic current

# View migration history
docker-compose exec backend alembic history

# Create new migration (after model changes)
docker-compose exec backend alembic revision --autogenerate -m "Description"

# Apply migrations manually
docker-compose exec backend alembic upgrade head

# Rollback one migration
docker-compose exec backend alembic downgrade -1
```

**How it works**:
- On startup, backend runs `alembic upgrade head` automatically ([docker-compose.yml](docker-compose.yml) line 40)
- Migration files are in `backend/alembic/versions/`
- Current version: `20251127022614` - Initial migration with all tables

### Database Operations

```bash
# List all tables
docker-compose exec postgres psql -U postgres -d citation_generator_db -c "\dt"

# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d

# Backup database
docker-compose exec postgres pg_dump -U postgres citation_generator_db > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U postgres -d citation_generator_db
```

---

## Monitoring

### Grafana Dashboard

1. Open http://localhost:3001
2. Login: `admin` / `admin`
3. Navigate to **Dashboards** → **Citation Generator API Metrics**

**Available Metrics**:
- Request rate (requests/second)
- Latency percentiles (p50, p95, p99)
- Error rates (4xx, 5xx)
- Request distribution by endpoint
- Response times

### Prometheus Queries

Access http://localhost:9090 and try these queries:

```promql
# Request rate
rate(http_requests_total[1m])

# p95 latency
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))

# Error rate
rate(http_requests_total{status=~"5.."}[1m])
```

### Health Checks

```bash
# API health
curl http://localhost:8000/health

# Metrics endpoint
curl http://localhost:8000/metrics

# Prometheus targets
curl http://localhost:9090/targets
```

---

## Deployment

### Azure Deployment (Production)

The application is automatically deployed to Azure App Service on every push to `main` via GitHub Actions.

**CI/CD Pipeline** ([.github/workflows/cd.yml](.github/workflows/cd.yml)):
1. Runs backend tests (must pass with 70% coverage)
2. Builds Docker images for backend and frontend
3. Pushes images to GitHub Container Registry
4. Deploys to Azure App Service
5. Runs health checks

**Required GitHub Secrets**:
- `AZURE_CREDENTIALS` - Azure service principal
- `AZURE_RESOURCE_GROUP` - Azure resource group name
- `AZURE_WEBAPP_BACKEND` - Backend app service name
- `AZURE_WEBAPP_FRONTEND` - Frontend app service name
- `DATABASE_URL` - Production PostgreSQL connection string

**Production URLs**:
- Backend: Set in Azure App Service
- Frontend: Set in Azure App Service
- API Docs: `https://{backend-url}/docs`

### Environment Variables

**Local Development** ([.env](.env)):
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/citation_generator_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=citation_generator_db
ENVIRONMENT=development
```

**Production** (Azure App Service):
- `DATABASE_URL` - PostgreSQL connection string
- `ALLOWED_ORIGINS` - Comma-separated frontend URLs (configured in CD pipeline)
- `ENVIRONMENT=production`

---

## Monitoring in Production

**Important**: Grafana and Prometheus are **NOT deployed to production**. They run only locally for development monitoring.

**Why?**
- Azure App Service provides built-in monitoring and metrics
- Cost optimization (no need for separate monitoring containers)
- Production uses Azure Application Insights for observability

**Local Monitoring Only**:
- ✅ Grafana dashboard for local development
- ✅ Prometheus metrics collection
- ✅ Pre-configured dashboards and queries

**Production Monitoring**:
- Azure App Service metrics (built-in)
- `/health` endpoint for health checks
- `/metrics` endpoint still available for Prometheus-compatible scrapers

---

## API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

**Main Endpoints**:
- `GET /health` - Health check with database status
- `GET /metrics` - Prometheus metrics
- `GET /projects` - List all projects
- `POST /projects` - Create a project
- `GET /citations` - List all citations
- `POST /citations` - Create a citation
- `POST /citations/{id}/format` - Generate formatted citation (APA/MLA)

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
# Windows
netstat -ano | findstr :5432

# Stop conflicting service or change port in docker-compose.yml
```

### Database Connection Issues

```bash
# Check PostgreSQL is healthy
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U postgres -c "SELECT 1"
```

### Backend Not Starting

```bash
# View detailed logs
docker-compose logs backend

# Rebuild backend
docker-compose build backend
docker-compose up -d backend
```

### Grafana Dashboard Empty

```bash
# Generate some traffic first
curl http://localhost:8000/health
curl http://localhost:8000/projects

# Check Prometheus targets (should show backend as UP)
open http://localhost:9090/targets

# Verify metrics endpoint
curl http://localhost:8000/metrics
```

### Rebuild Everything

```bash
# Nuclear option: remove everything and rebuild
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## Configuration Files

- [.env.example](.env.example) - Environment variables template
- [docker-compose.yml](docker-compose.yml) - Local development services
- [backend/alembic.ini](backend/alembic.ini) - Alembic configuration
- [backend/alembic/env.py](backend/alembic/env.py) - Alembic environment setup
- [monitoring/prometheus/prometheus.yml](monitoring/prometheus/prometheus.yml) - Prometheus config
- [monitoring/grafana/](monitoring/grafana/) - Grafana dashboards and datasources

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`docker-compose exec backend pytest tests/ -v`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Support

For issues and questions:
- Check the [Troubleshooting](#troubleshooting) section
- Review logs: `docker-compose logs -f`
- Check health: `curl http://localhost:8000/health`