# Project Report

> This is a summarized version of the following report: https://docs.google.com/document/d/1av0LGTgIhklxdFjJpRRLfDk7mGfmiWWj6aHvWXK_MXE/edit?usp=sharing

---

## 1. Code Quality Improvements

Several refactors were completed to improve maintainability, readability, and compliance with SOLID principles:

### Refactored Conditional Logic

- Replaced large if/elif chains in the citation formatters with dictionary-based function maps.
- This improved extensibility, reduced duplication, and aligned with the Strategy pattern.

### Removed Duplication

- Extracted repeated author-cleaning logic into a `_clean_authors()` helper in the base formatter.
- Removed four duplicated code blocks while keeping behavior unchanged.

### Eliminated Hardcoded Constants

- Moved large sets of APA acronyms and MLA lowercase words into a new `formatter_constants.py` module.
- Improved readability and separation of concerns.

### Improved Configuration Handling

- Removed hardcoded database credentials and replaced them with environment variables.
- Updated `.env.example` for clarity and security.

### Added Pydantic Models

- Introduced Pydantic schemas for automatic validation.
- Simplified service-layer validation and centralized logic.

---

## 2. Testing Improvements

### Comprehensive Test Coverage

Extended the test suite with integration tests covering:

- Service and Repository interactions
- Service and Formatter interactions
- Service and Validator interactions

Combined with the existing unit tests from Part 1, the project now includes 356 tests.

### Coverage Achievement

- Achieved 97% test coverage, far above the required 70%.
- Coverage reports (HTML, XML, JUnit) included in the repository.

---

## 3. Continuous Integration (CI)

A full GitHub Actions CI pipeline was created to automate testing and build validation.

### Pipeline Features

- Runs on pushes to develop and feature branches, and on pull requests to main or develop.
- Executes the full test suite and enforces a 70% coverage threshold.
- Builds both backend and frontend after tests succeed.
- Performs security analysis using Safety, Bandit, and npm audit.
- Uploads coverage and test reports as artifacts.
- CI fails immediately if tests fail or coverage drops below the required threshold.

This ensures no untested or insecure code can be merged into main branches.

---

## 4. Deployment Automation (CD)

A dedicated CD pipeline deploys the application to Azure Web Apps for Containers.

### Azure Setup

- Backend deployed on Azure Linux Web App (citation-backend-cbr).
- Frontend deployed on Azure Linux Web App (citation-frontend-cbr).
- Azure Flexible PostgreSQL Database created and configured.
- Environment variables provided through both Azure App Settings and the CD pipeline.

### Dockerization

- **Backend container:** Python 3.11, PostgreSQL drivers, port 8000, with health checks.
- **Frontend container:** Node 18 multi-stage build, production-ready assets, served on port 3000.

### CD Workflow

- Triggered only on pushes to the main branch.
- Runs backend tests and coverage checks before deployment.
- Builds and pushes Docker images to GitHub Container Registry.
- Automatically retrieves the live backend URL from Azure.
- Injects environment variables (including DATABASE_URL, ALLOWED_ORIGINS, VITE_API_URL).
- Deploys both backend and frontend containers using azure/webapps-deploy.
- Performs live health checks post-deployment before confirming success.

### CORS Challenge

- CORS initially failed due to Azure's changing hostnames.
- Resolved by dynamically injecting correct origins through pipeline-provided environment variables.

---

## 5. Monitoring and Health Checks

### Health Endpoints

- Added a basic health endpoint to confirm the API is running.
- Added a detailed `/health` endpoint that verifies:
  - Database connectivity
  - API version
  - Supported formats and citation types
  - Environment mode

### Local Monitoring Stack

Prometheus and Grafana were not deployed to Azure. Instead, they run locally via Docker Compose:

- Prometheus scrapes metrics for request latency, error rates, and throughput.
- Grafana visualizes metrics through a custom dashboard.

Local monitoring helps diagnose issues and understand system performance without incurring cloud costs.