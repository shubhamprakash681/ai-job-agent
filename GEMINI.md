# AI Job Agent - Project Context

## Project Architecture
- **Backend**: Python FastAPI, PostgreSQL (via asyncpg), Redis
- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Infrastructure**: Docker Compose

## Coding Conventions
- **Python**: Type hints everywhere, async/await for DB operations, pydantic for validation, structlog for logging.
- **Frontend**: Strict TypeScript, modular React components, Tailwind for styling.
- **General**: SOLID principles, DRY, KISS, clear docstrings, structured error handling.

## Candidate Facts
- Name: Shubham Prakash
- Experience: 3+ years
- Skills: Java, Spring Boot, React
- Location: Mumbai
- Current/Past Employer: Accenture

## Forbidden Assumptions & Actions
- NEVER invent facts or hallucinate experience.
- NEVER scrape LinkedIn.
- NEVER attempt to bypass CAPTCHAs.
- NEVER embed secrets in code.

## AI Provider Strategy
- **Gemini**: Used for high-level reasoning (resume tailoring, cover letters, complex validation).
- **Groq**: Used for fast/free operations (extraction, classification, initial scoring).
- **Local LLM**: Fallback when cloud providers are unavailable.

## Testing & Security Rules
- Real tests only; no testing against live production sites.
- Use JWT for authentication.
- All secrets go in `.env` files.

## Job Source & Application Rules
- Respect `robots.txt` on all job boards.
- No automated scraping of LinkedIn.
- Fallback to manual entry when needed.
- **Safety First**: Human approval is required before submission.
- Default to `DRY_RUN=true`.
- Enforce a daily application limit.

## Deployment Instructions
- Local testing and dev deployment utilize Docker Compose to easily orchestrate PostgreSQL, Redis, Backend, and Frontend.
