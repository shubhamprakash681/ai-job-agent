# Architecture Overview

## System Diagram
(Next.js Frontend) <---> (FastAPI Backend) <---> (PostgreSQL Database)
                               |
                               +---> (Redis Cache / Task Queue)
                               |
                               +---> (AI Providers: Gemini / Groq)

## Components
1. **Frontend**: Next.js application handling the UI, dashboard, and manual application approvals.
2. **Backend**: FastAPI serving REST endpoints, orchestrating tasks, and handling AI interactions.
3. **Database**: PostgreSQL for storing jobs, applications, and configurations.
4. **Cache/Queue**: Redis for caching LLM responses and queuing background tasks.
5. **AI Services**: External APIs (Gemini, Groq) for NLP tasks.

## Data Flow
- Job listings are fetched/parsed and stored in PostgreSQL.
- The AI Agent scores jobs and flags them for the user.
- If approved, the Agent uses AI to tailor the resume and generate a cover letter.
- Generated documents are saved to the file system and DB.

## Technology Choices
- **Python/FastAPI**: Rapid development, native async support, extensive AI/ML ecosystem.
- **TypeScript/Next.js**: Robust frontend rendering and strong typing.
- **PostgreSQL**: Reliable relational data storage.
- **Redis**: High-performance in-memory cache and task queue management.
