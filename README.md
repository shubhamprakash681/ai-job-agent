# AI Job Search & Application Agent

An intelligent, full-stack AI agent that automates the job search and application process.

## Features
- Automated job search across platforms
- AI-driven resume tailoring and cover letter generation
- Intelligent job scoring based on candidate profile
- Automated form filling (with human approval fallback)
- Application tracking and analytics dashboard

## Tech Stack
- **Backend:** Python, FastAPI, PostgreSQL, Redis
- **Frontend:** Next.js, TypeScript, Tailwind CSS
- **AI Models:** Gemini (Reasoning), Groq (Fast tasks)
- **Infrastructure:** Docker, Docker Compose

## Prerequisites
- Docker and Docker Compose
- Node.js (for local frontend dev)
- Python 3.12+ (for local backend dev)

## Quick Start (Docker Compose)
1. Copy `.env.example` to `.env` and configure your API keys.
2. Run `docker compose up -d`
3. Access the frontend at http://localhost:3000 and the backend API at http://localhost:8000.

## Local Development
Detailed development guides are available in the `/docs` directory.
- `cd backend && uv sync`
- `cd frontend && npm install`

## Configuration
Configure API keys, application limits, and safety mechanisms in the `.env` file.

## Project Structure
- `/backend`: FastAPI backend application
- `/frontend`: Next.js frontend application
- `/candidate`: Candidate facts and resume data
- `/prompts`: LLM prompts
- `/documents`: Generated documents (resumes, cover letters)
- `/scripts`: Utility scripts (backup, restore)
- `/docs`: Documentation (architecture, security, deployment)

## Development Phases
Refer to internal tracking artifacts for development phase milestones.

## License
MIT License
