# Environment Setup Guide

## Database Configuration

This project uses PostgreSQL for the database. Follow these steps to set up your local environment:

### 1. Install PostgreSQL

Download and install PostgreSQL from: https://www.postgresql.org/download/

### 2. Create Database

```bash
# Using psql
psql -U postgres -c "CREATE DATABASE citation_generator_db;"
```

Or use pgAdmin GUI to create a database named `citation_generator_db`.

### 3. Configure Environment Variables

Copy the `.env.example` file to `.env` in both the root and backend directories:

```bash
# Root directory
cp .env.example .env

# Backend directory
cp backend/.env.example backend/.env
```

Then edit the `.env` files and update with your PostgreSQL credentials:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/citation_generator_db
ENVIRONMENT=development
```

**IMPORTANT:** Never commit your `.env` file to git. It's already in `.gitignore`.

### 4. Install Dependencies

```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

If you encounter encoding issues on Windows, you can use:

```bash
python -c "from alembic.config import Config; from alembic import command; import os; os.environ['DATABASE_URL'] = 'your_connection_string'; cfg = Config('alembic.ini'); cfg.set_main_option('sqlalchemy.url', os.environ['DATABASE_URL']); command.upgrade(cfg, 'head')"
```

### 6. Verify Setup

Test the database connection:

```bash
cd backend
python -c "from db.database import engine; from sqlalchemy import text; conn = engine.connect(); result = conn.execute(text('SELECT COUNT(*) FROM citations')); print(f'Connection successful! Citations: {result.scalar()}'); conn.close()"
```

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/dbname` |
| `ENVIRONMENT` | Application environment | `development`, `production`, `test` |

## Security Notes

- ✅ `.env` files are in `.gitignore` and will not be committed
- ✅ Use `.env.example` as a template for new developers
- ✅ Never hardcode credentials in source code
- ✅ In production, use environment variables or secret management services
