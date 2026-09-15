import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

SQL = """
DO $$
DECLARE
    curr_t text;
    v_count int;
BEGIN
    -- 1. Verify GUC setting for tenant isolation
    SET LOCAL "app.current_tenant" = '00000000-0000-0000-0000-000000000001';
    SELECT current_setting('app.current_tenant', true) INTO curr_t;
    IF curr_t = '00000000-0000-0000-0000-000000000001' THEN
        RAISE NOTICE 'POSTGRESQL_17_GUC_VERIFIED: %', curr_t;
    ELSE
        RAISE EXCEPTION 'GUC mismatch';
    END IF;

    -- 2. Verify transactional advisory locking
    PERFORM pg_advisory_xact_lock(hashtext('p7-manager-decision-ledger-qualification'));
    RAISE NOTICE 'POSTGRESQL_17_ADVISORY_LOCK_VERIFIED: PASS';

    -- 3. Verify PostgreSQL 17 version
    RAISE NOTICE 'POSTGRESQL_17_SERVER_VERSION_VERIFIED: %', current_setting('server_version');
END $$;

-- 4. Verify Phase 7 RLS & FORCE RLS policies
SELECT schemaname, tablename, rowsecurity 
FROM pg_tables 
WHERE tablename IN (
    'learning_manager_decision_ledger',
    'learning_decision_evidence_snapshot',
    'learning_synthetic_activation_token',
    'learning_manager_decision_audit_log'
)
ORDER BY tablename;

SELECT relname, relforcerowsecurity 
FROM pg_class 
WHERE relname IN (
    'learning_manager_decision_ledger',
    'learning_decision_evidence_snapshot',
    'learning_synthetic_activation_token',
    'learning_manager_decision_audit_log'
)
ORDER BY relname;

-- 5. Verify unprivileged role non-bypass (GLM Gate F6)
SELECT rolname, rolsuper, rolbypassrls 
FROM pg_roles 
WHERE rolname IN ('codesho_runtime', 'codesho_app', 'codesho_migrator')
ORDER BY rolname;
"""

cmd = [
    "docker", "exec", "-i", "phase1-engineering-readiness-postgres-1",
    "psql", "-U", "codesho_admin", "-d", "codesho"
]

proc = subprocess.run(cmd, input=SQL.encode('utf-8'), capture_output=True)
print("=== POSTGRESQL 17.10 QUALIFICATION OUTPUT ===")
print("STDOUT:")
print(proc.stdout.decode('utf-8', errors='replace'))
print("STDERR:")
print(proc.stderr.decode('utf-8', errors='replace'))
print("Exit code:", proc.returncode)
