# Development Guide

## Prerequisites
- Python 3.12+
- `uv` package manager
- Node.js 18+

## Setup
1. Backend: `cd backend && uv sync`
2. Frontend: `cd frontend && npm install`

## Running Locally
- Backend: `uv run uvicorn app.main:app --reload`
- Frontend: `npm run dev`

## Tests
- Run backend tests: `pytest`

## Code Style
- Use `ruff` for linting and formatting Python code.
- Run: `ruff check .` and `ruff format .`

## Database Migrations
- Use Alembic for schema changes.
- Generate: `alembic revision --autogenerate -m "description"`
- Apply: `alembic upgrade head`
