#!/usr/bin/env sh
set -eu

: "${VERIFY_DATABASE_URL:?VERIFY_DATABASE_URL is required}"
: "${BACKUP_FILE:?BACKUP_FILE is required}"

case "$VERIFY_DATABASE_URL" in
  *codesho_restore_verify*) ;;
  *) echo "VERIFY_DATABASE_URL must target a codesho_restore_verify database" >&2; exit 2 ;;
esac

pg_restore --clean --if-exists \
  --dbname "$VERIFY_DATABASE_URL" "$BACKUP_FILE"
psql "$VERIFY_DATABASE_URL" -v ON_ERROR_STOP=1 -c "
  SELECT 1;
  DO \\$\$
  BEGIN
    IF NOT EXISTS (
      SELECT 1 FROM pg_tables WHERE schemaname = 'codesho' AND tableowner = 'codesho_migrator'
    ) THEN
      RAISE EXCEPTION 'restored tables are not owned by codesho_migrator';
    END IF;
    IF NOT has_table_privilege(
      'codesho_runtime', 'codesho.django_migrations', 'SELECT,INSERT,UPDATE,DELETE'
    ) THEN
      RAISE EXCEPTION 'codesho_runtime lacks restored Django table privileges';
    END IF;
  END
  \$\$;
"
