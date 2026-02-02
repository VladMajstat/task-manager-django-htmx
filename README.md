# Task Manager

Simple task/project manager built with Django, HTMX, Alpine.js, and Bootstrap.

## Requirements

- Python 3.13
- PostgreSQL 13+ (local) OR Docker (recommended)

## Quick start (Docker)

```bash
docker compose up --build
```

The app will be available at http://localhost:8000

## Quick start (Local)

1) Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate
```

2) Install dependencies

```bash
pip install -r requirements.txt
```

3) Configure environment variables (PowerShell example)

```powershell
$env:DJANGO_SECRET_KEY = "change-me"
$env:DJANGO_DEBUG = "1"
$env:DJANGO_ALLOWED_HOSTS = "*"
$env:DB_NAME = "task"
$env:DB_USER = "task"
$env:DB_PASSWORD = "task"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"
```

4) Run migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| DJANGO_SECRET_KEY | change-me | Django secret key |
| DJANGO_DEBUG | 1 | Debug mode (1 or 0) |
| DJANGO_ALLOWED_HOSTS | * | Comma-separated allowed hosts |
| DB_NAME | task | Database name |
| DB_USER | task | Database user |
| DB_PASSWORD | task | Database password |
| DB_HOST | localhost | Database host |
| DB_PORT | 5432 | Database port |

## Linting

Ruff is configured via pre-commit.

```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

## Notes

- SQL answers are in SQL.md
- Docker uses Postgres 16 by default
