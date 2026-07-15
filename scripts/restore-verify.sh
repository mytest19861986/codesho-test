#!/usr/bin/env sh
set -eu

: "${VERIFY_DATABASE_URL:?VERIFY_DATABASE_URL is required}"
: "${BACKUP_FILE:?BACKUP_FILE is required}"

case "$VERIFY_DATABASE_URL" in
  *codesho_restore_verify*) ;;
  *) echo "VERIFY_DATABASE_URL must target a codesho_restore_verify database" >&2; exit 2 ;;
esac

pg_restore --clean --if-exists --no-owner --no-acl \
  --dbname "$VERIFY_DATABASE_URL" "$BACKUP_FILE"
psql "$VERIFY_DATABASE_URL" -v ON_ERROR_STOP=1 -c "SELECT 1;"
