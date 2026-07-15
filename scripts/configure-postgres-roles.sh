#!/usr/bin/env sh
set -eu

: "${POSTGRES_ADMIN_URL:?POSTGRES_ADMIN_URL is required}"
: "${CODESHO_MIGRATOR_PASSWORD:?CODESHO_MIGRATOR_PASSWORD is required}"
: "${CODESHO_RUNTIME_PASSWORD:?CODESHO_RUNTIME_PASSWORD is required}"

psql "$POSTGRES_ADMIN_URL" -v ON_ERROR_STOP=1 \
  --set=migrator_password="$CODESHO_MIGRATOR_PASSWORD" \
  --set=runtime_password="$CODESHO_RUNTIME_PASSWORD" <<'SQL'
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

CREATE SCHEMA IF NOT EXISTS codesho AUTHORIZATION codesho_migrator;
GRANT USAGE, CREATE ON SCHEMA codesho TO codesho_migrator;
GRANT USAGE ON SCHEMA codesho TO codesho_runtime;
SELECT format('GRANT CONNECT ON DATABASE %I TO codesho_migrator, codesho_runtime', current_database())
\gexec
ALTER DEFAULT PRIVILEGES FOR ROLE codesho_migrator IN SCHEMA codesho
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO codesho_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE codesho_migrator IN SCHEMA codesho
    GRANT USAGE, SELECT ON SEQUENCES TO codesho_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE codesho_migrator IN SCHEMA codesho
    GRANT EXECUTE ON FUNCTIONS TO codesho_runtime;
SQL
