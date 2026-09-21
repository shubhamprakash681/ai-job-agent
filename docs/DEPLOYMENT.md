# Deployment Guide

## Docker Compose
The easiest way to deploy is using Docker Compose:
`docker compose up -d`

## Environment Configuration
Ensure your `.env` file contains production-ready secrets:
- Secure `SECRET_KEY`
- Database credentials
- API Keys for AI providers

## HTTPS and Proxy
In a production setting, place the Docker Compose setup behind a reverse proxy like Nginx or Traefik to handle SSL/TLS termination.

## Backup
Use the provided `scripts/backup.sh` to periodically backup the PostgreSQL database and candidate/document files. Set up a cron job for automated backups.
