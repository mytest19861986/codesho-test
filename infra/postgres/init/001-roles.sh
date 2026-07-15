#!/usr/bin/env sh
set -eu

: "${CODESHO_MIGRATOR_PASSWORD:?CODESHO_MIGRATOR_PASSWORD is required}"
: "${CODESHO_RUNTIME_PASSWORD:?CODESHO_RUNTIME_PASSWORD is required}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<'SQL'
\getenv migrator_password CODESHO_MIGRATOR_PASSWORD
\getenv runtime_password CODESHO_RUNTIME_PASSWORD
SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOINHERIT',
    'codesho_migrator', :'migrator_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_migrator')
\gexec

SELECT format(
    'CREATE ROLE %I LOGIN PASSWORD %L NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE NOINHERIT',
    'codesho_runtime', :'runtime_password'
)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime')
\gexec

ALTER ROLE codesho_migrator PASSWORD :'migrator_password';
ALTER ROLE codesho_runtime PASSWORD :'runtime_password';
ALTER ROLE codesho_migrator SET search_path TO codesho, public;
ALTER ROLE codesho_runtime SET search_path TO codesho, public;
SQL
