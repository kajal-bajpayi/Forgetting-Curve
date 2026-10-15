# Forgetting Curve

A personal knowledge-retention application that helps users
remember what they learn through active recall and spaced repetition.

## Current milestone

Milestone 1: API skeleton and health endpoint.

- FastAPI application factory
- GET /health endpoint
- Automatically generated OpenAPI documentation
- Automated tests

## Technology stack

- Python
- FastAPI
- Pydantic
- pytest and HTTPX

Planned additions:

- PostgreSQL
- SQLAlchemy
- Alembic
- JWT authentication
- Adaptive review scheduling
- React and TypeScript frontend
- Docker and deployment

## Prerequisites

- Python 3.12 or 3.13
- pip

## Setup

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install the application and test dependencies:

```bash
python -m pip install -e ".[test]"
```

## Run the application

```bash
uvicorn app.main:app --reload
```

Health endpoint:

http://127.0.0.1:8000/health

Swagger UI:

http://127.0.0.1:8000/docs

## Run tests

```bash
pytest
```

## Current limitations

The database, authentication, concepts, review scheduler, analytics,
frontend, and deployment are not implemented yet.