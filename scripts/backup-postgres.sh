#!/usr/bin/env sh
set -eu

: "${DATABASE_URL:?DATABASE_URL is required}"
: "${BACKUP_DIR:?BACKUP_DIR is required}"

timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$BACKUP_DIR"
umask 077
pg_dump --format=custom --no-owner --no-acl "$DATABASE_URL" \
  --file "$BACKUP_DIR/codesho-$timestamp.dump"
