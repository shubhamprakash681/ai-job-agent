#!/bin/bash
# Backup script for AI Job Agent
set -euo pipefail

BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "Backing up PostgreSQL..."
docker compose exec -T postgres pg_dump -U jobagent jobagent > "$BACKUP_DIR/database.sql"

echo "Backing up candidate data..."
cp -r ./candidate "$BACKUP_DIR/candidate" 2>/dev/null || echo "No candidate directory"

echo "Backing up documents..."
cp -r ./documents "$BACKUP_DIR/documents" 2>/dev/null || echo "No documents directory"

echo "Backing up prompts..."
cp -r ./prompts "$BACKUP_DIR/prompts" 2>/dev/null || echo "No prompts directory"

echo "Backup completed: $BACKUP_DIR"
