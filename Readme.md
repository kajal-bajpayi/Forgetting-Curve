# Forgetting Curve

Forgetting Curve is a personal learning and spaced-repetition API designed to help users capture knowledge, review concepts systematically, and retain information over time through structured recall cycles.

The project combines a FastAPI backend, SQLAlchemy models, and a SQLite-first development setup to support a clean and testable foundation for a future learning platform.

## Why this project exists

Most learning tools focus on capturing notes, but not on the retention strategy required to move information from short-term memory into long-term memory. Forgetting Curve addresses this by providing a foundation for:

- creating structured learning concepts
- storing knowledge in a searchable, user-owned format
- authenticating users with secure JWT tokens
- preparing the system for adaptive review scheduling and recall-based learning workflows

## Core features

### Current implementation

- FastAPI application factory and API routing
- JWT-based authentication with password hashing
- user registration and login flows
- concept creation, listing, retrieval, update, and deletion
- per-user data isolation using foreign-key relationships
- automatic OpenAPI schema generation via FastAPI
- SQLite-backed local development database
- Alembic migration support for schema evolution
- automated tests for auth, security, configuration, and database behavior

### Planned features

- adaptive spaced repetition scheduling
- concept review sessions and retention metrics
- deeper search and filter capabilities
- PostgreSQL support for production deployments
- analytics dashboards for learning progress
- frontend experience for concept review workflows
- deployment automation with Docker and CI/CD

## Tech stack

- Python 3.12+
- FastAPI
- Pydantic v2
- SQLAlchemy 2.0
- Alembic
- SQLite (default) / PostgreSQL-ready configuration
- JWT authentication via PyJWT
- Argon2 password hashing via pwdlib
- pytest and HTTPX for automated testing

## Project structure

```text
.
├── app/
│   ├── api/
│   │   ├── deps.py
│   │   └── v1/
│   │       └── endpoints/
│   │           ├── auth.py
│   │           └── concept.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── concept.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── concept.py
│   │   └── user.py
│   ├── services/
│   │   └── scheduler.py
│   ├── __init__.py
│   └── main.py
├── migrations/
│   ├── versions/
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── tests/
│   ├── test_auth_api.py
│   ├── test_config.py
│   ├── test_database.py
│   ├── test_health.py
│   ├── test_security.py
│   ├── test_user_model.py
│   └── test_user_schema.py
├── .gitignore
├── alembic.ini
├── app.py
├── forgetting_curve.db
├── pyproject.toml
├── Readme.md
└── requirements.txt (if present in your environment)
```

## Getting started

### Prerequisites

- Python 3.12 or 3.13
- pip
- Git

### Clone the repository

```bash
git clone https://github.com/your-username/forgetting-curve.git
cd forgetting-curve
```

### Create a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### Install dependencies

This project exposes a `dev` extra in `pyproject.toml`, so the correct install command is:

```bash
python -m pip install -e ".[dev]"
```

If you prefer to install only the runtime dependencies, you can use:

```bash
python -m pip install -e .
```

## Runtime configuration

The application uses environment-based configuration through `pydantic-settings`. The default settings are defined in `app/core/config.py`.

A typical `.env` file for local development looks like this:

```env
APP_ENV=development
DATABASE_URL=sqlite:///./forgetting_curve.db
JWT_SECRET_KEY=change-me-in-production-use-a-long-random-value
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Important notes:

- `APP_ENV=production` requires a JWT secret of at least 32 characters.
- The default database is SQLite for local onboarding and development.
- Do not use the development-only default secret in a production environment.

## Run the application

Start the API with Uvicorn:

```bash
uvicorn app.main:app --reload
```

The application will be available at:

- Application root: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/health
- Swagger UI: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## API surface

All endpoints are under the `/api/v1` prefix.

### Authentication

#### `POST /api/v1/auth/register`
Creates a new user account.

Request body:

```json
{
  "email": "user@example.com",
  "password": "strong-password-123"
}
```

#### `POST /api/v1/auth/login`
Authenticates a user and returns a bearer token.

Request body:

```json
{
  "email": "user@example.com",
  "password": "strong-password-123"
}
```

Response:

```json
{
  "access_token": "<jwt-token>",
  "token_type": "bearer"
}
```

#### `GET /api/v1/auth/me`
Returns the profile of the authenticated user.

Authorization header:

```http
Authorization: Bearer <token>
```

### Concepts

#### `POST /api/v1/concepts`
Creates a concept for the authenticated user.

Request body:

```json
{
  "title": "What is a hash function?",
  "question": "How does a hash function help with data integrity?",
  "answer": "It transforms input data into a fixed-size value used for verification and indexing.",
  "subject": "computer-science",
  "tags": ["security", "algorithms"]
}
```

#### `GET /api/v1/concepts`
Lists concepts belonging to the authenticated user.

Supports query parameters including:

- `q` for text search on title/question
- `subject` for subject-based filtering
- `archived` for archived/non-archived concepts
- `offset` and `limit` for pagination

#### `GET /api/v1/concepts/{concept_id}`
Retrieves one concept by ID for the authenticated user.

#### `PATCH /api/v1/concepts/{concept_id}`
Updates a concept or toggles `is_archived`.

#### `DELETE /api/v1/concepts/{concept_id}`
Deletes a concept owned by the current user.

## Database and persistence

The project uses SQLAlchemy models with a SQLite database by default. Database sessions are managed centrally in `app/db/session.py`, and Alembic is prepared for future schema migrations.

Current data model includes:

- `users` table for authentication and account metadata
- `concepts` table for learning cards, questions, answers, tags, and archive status

## Security considerations

The project includes production-minded security defaults:

- password hashing with Argon2 via `pwdlib`
- JWT validation and expiration checks
- user-scoped access control for concept resources
- secret validation in production mode

Before production deployment, make sure to:

- configure a strong `JWT_SECRET_KEY`
- use a managed database such as PostgreSQL
- set environment variables securely
- enable HTTPS and reverse-proxy security measures
- validate token rotation and renewal flows

## Testing

Run the project test suite with:

```bash
pytest
```

The test suite currently covers:

- health endpoints
- authentication flows
- security utilities
- database behavior
- model validation
- configuration defaults

## Contributing

Contributions are welcome. A strong contribution flow for this project would include:

1. creating a feature branch
2. implementing the change with tests
3. running the relevant test suite
4. updating documentation when behavior changes
5. opening a clear pull request with a summary of the change

## Roadmap

The current codebase is a strong foundation for a larger learning system. The priority roadmap includes:

- adaptive review scheduling based on spaced repetition intervals
- richer concept metadata and learning progress tracking
- analytics on retention performance and weak areas
- PostgreSQL migration for production readiness
- frontend application for user interactions
- containerized deployment and operational monitoring

## Current project status

This repository is in an early but functional stage. The core API skeleton, authentication, and concept management flows are present and test-covered, while the higher-level retention engine and end-user learning experience are still being developed.


