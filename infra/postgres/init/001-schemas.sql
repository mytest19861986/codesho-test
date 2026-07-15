CREATE SCHEMA IF NOT EXISTS codesho;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS platform;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_app') THEN
        CREATE ROLE codesho_app LOGIN PASSWORD 'codesho';
    END IF;
END
$$;

GRANT CONNECT ON DATABASE codesho TO codesho_app;
GRANT USAGE, CREATE ON SCHEMA codesho TO codesho_app;
GRANT USAGE ON SCHEMA public TO codesho_app;
ALTER ROLE codesho_app SET search_path TO codesho, public;
