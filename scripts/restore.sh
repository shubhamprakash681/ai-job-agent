#!/bin/bash
# Restore script for AI Job Agent
set -euo pipefail

if [ -z "${1:-}" ]; then
    echo "Usage: ./scripts/restore.sh <backup_dir>"
    echo "Example: ./scripts/restore.sh ./backups/20260920_103000"
    exit 1
fi

BACKUP_DIR="$1"

if [ ! -d "$BACKUP_DIR" ]; then
    echo "Backup directory not found: $BACKUP_DIR"
    exit 1
fi

echo "Restoring PostgreSQL..."
if [ -f "$BACKUP_DIR/database.sql" ]; then
    docker compose exec -T postgres psql -U jobagent -d jobagent < "$BACKUP_DIR/database.sql"
    echo "Database restored."
else
    echo "No database backup found."
fi

echo "Restoring candidate data..."
if [ -d "$BACKUP_DIR/candidate" ]; then
    cp -r "$BACKUP_DIR/candidate" ./candidate
    echo "Candidate data restored."
fi

echo "Restoring documents..."
if [ -d "$BACKUP_DIR/documents" ]; then
    cp -r "$BACKUP_DIR/documents" ./documents
    echo "Documents restored."
fi

echo "Restore completed from: $BACKUP_DIR"
