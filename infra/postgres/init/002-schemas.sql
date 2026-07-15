CREATE SCHEMA IF NOT EXISTS codesho AUTHORIZATION codesho_migrator;
CREATE SCHEMA IF NOT EXISTS audit AUTHORIZATION codesho_migrator;
CREATE SCHEMA IF NOT EXISTS analytics AUTHORIZATION codesho_migrator;
CREATE SCHEMA IF NOT EXISTS platform AUTHORIZATION codesho_migrator;

GRANT CONNECT ON DATABASE codesho TO codesho_migrator, codesho_runtime;
GRANT USAGE ON SCHEMA public, codesho TO codesho_runtime;
GRANT USAGE, CREATE ON SCHEMA public, codesho TO codesho_migrator;

ALTER DEFAULT PRIVILEGES FOR ROLE codesho_migrator IN SCHEMA codesho
    GRANT SELECT, INSERT, UPDATE, DELETE, TRUNCATE ON TABLES TO codesho_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE codesho_migrator IN SCHEMA codesho
    GRANT USAGE, SELECT ON SEQUENCES TO codesho_runtime;
ALTER DEFAULT PRIVILEGES FOR ROLE codesho_migrator IN SCHEMA codesho
    GRANT EXECUTE ON FUNCTIONS TO codesho_runtime;
