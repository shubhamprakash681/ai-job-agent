# Security Documentation

## Secret Management
- All sensitive information (API keys, passwords, tokens) must be stored in `.env` files.
- `.env` files are ignored by git.
- Do not log sensitive data.

## Authentication
- Endpoints should be protected via JWT authentication.
- Users must authenticate to view dashboard and approve applications.

## Data Protection
- Candidate PII (Personally Identifiable Information) must be handled carefully.
- Limit access to the `/candidate` directory.

## Prohibited Actions
- Bypassing CAPTCHAs is strictly forbidden.
- Automated web scraping that violates terms of service (e.g., LinkedIn) is blocked by design.
