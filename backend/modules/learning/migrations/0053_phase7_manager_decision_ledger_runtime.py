# Generated for Phase 7 Real Pilot Manager Decision Ledger & Authority Runtime
import django.db.models.deletion
import uuid
from django.db import migrations, models


POSTGRES_P7_RLS_SQL = r"""
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_manager_decision_ledger',
        'learning_decision_evidence_snapshot',
        'learning_synthetic_activation_token',
        'learning_manager_decision_audit_log'
    ];
BEGIN
    IF current_setting('server_version_num', true)::int >= 100000 THEN
        FOREACH tbl IN ARRAY tables LOOP
            EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', tbl);
            EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY;', tbl);
            EXECUTE format('DROP POLICY IF EXISTS p7_tenant_isolation_policy ON %I;', tbl);
            EXECUTE format(
                'CREATE POLICY p7_tenant_isolation_policy ON %I ' ||
                'FOR ALL USING (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid) ' ||
                'WITH CHECK (tenant_id = NULLIF(current_setting(''app.current_tenant'', true), '''')::uuid);',
                tbl
            );
        END LOOP;

        -- GLM F1 & Immutability: Revoke UPDATE and DELETE on Decision Ledger and Audit Log
        EXECUTE 'REVOKE UPDATE, DELETE ON learning_manager_decision_ledger FROM PUBLIC;';
        EXECUTE 'REVOKE UPDATE, DELETE ON learning_manager_decision_audit_log FROM PUBLIC;';
        
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_app') THEN
            EXECUTE 'REVOKE DELETE ON learning_manager_decision_ledger FROM codesho_app;';
            EXECUTE 'REVOKE UPDATE, DELETE ON learning_manager_decision_audit_log FROM codesho_app;';
        END IF;
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_runtime') THEN
            EXECUTE 'REVOKE DELETE ON learning_manager_decision_ledger FROM codesho_runtime;';
            EXECUTE 'REVOKE UPDATE, DELETE ON learning_manager_decision_audit_log FROM codesho_runtime;';
        END IF;
    END IF;
END $$;
"""

REVERSE_P7_RLS_SQL = r"""
DO $$
DECLARE
    tbl text;
    tables text[] := ARRAY[
        'learning_manager_decision_ledger',
        'learning_decision_evidence_snapshot',
        'learning_synthetic_activation_token',
        'learning_manager_decision_audit_log'
    ];
BEGIN
    IF current_setting('server_version_num', true)::int >= 100000 THEN
        FOREACH tbl IN ARRAY tables LOOP
            EXECUTE format('DROP POLICY IF EXISTS p7_tenant_isolation_policy ON %I;', tbl);
            EXECUTE format('ALTER TABLE %I NO FORCE ROW LEVEL SECURITY;', tbl);
        END LOOP;
    END IF;
END $$;
"""

def enable_p7_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        tables = [
            'learning_manager_decision_ledger',
            'learning_decision_evidence_snapshot',
            'learning_synthetic_activation_token',
            'learning_manager_decision_audit_log'
        ]
        for tbl in tables:
            cursor.execute(f"ALTER TABLE {tbl} ENABLE ROW LEVEL SECURITY;")
            cursor.execute(f"ALTER TABLE {tbl} FORCE ROW LEVEL SECURITY;")
            cursor.execute(f"DROP POLICY IF EXISTS p7_tenant_isolation_policy ON {tbl};")
            cursor.execute(
                f"CREATE POLICY p7_tenant_isolation_policy ON {tbl} "
                f"FOR ALL USING (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid) "
                f"WITH CHECK (tenant_id = NULLIF(current_setting('app.current_tenant', true), '')::uuid);"
            )
        cursor.execute("REVOKE UPDATE, DELETE ON learning_manager_decision_ledger FROM PUBLIC;")
        cursor.execute("REVOKE UPDATE, DELETE ON learning_manager_decision_audit_log FROM PUBLIC;")
        cursor.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'codesho_app') THEN
                REVOKE UPDATE, DELETE ON learning_manager_decision_ledger FROM codesho_app;
                REVOKE UPDATE, DELETE ON learning_manager_decision_audit_log FROM codesho_app;
            END IF;
        END $$;
        """)

def disable_p7_postgres_rls(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    with schema_editor.connection.cursor() as cursor:
        tables = [
            'learning_manager_decision_ledger',
            'learning_decision_evidence_snapshot',
            'learning_synthetic_activation_token',
            'learning_manager_decision_audit_log'
        ]
        for tbl in tables:
            cursor.execute(f"DROP POLICY IF EXISTS p7_tenant_isolation_policy ON {tbl};")
            cursor.execute(f"ALTER TABLE {tbl} NO FORCE ROW LEVEL SECURITY;")


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0052_phase6_pilot_admission_fsm'),
        ('platform_tenant', '0004_p3_vs12_guardian_access_grant'),
    ]

    operations = [
        migrations.CreateModel(
            name='ManagerDecisionLedger',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('decision_version', models.PositiveIntegerField(default=1)),
                ('state', models.CharField(choices=[('DRAFT', 'Draft'), ('EVIDENCE_COLLECTION', 'Evidence Collection'), ('DUE_DILIGENCE_REVIEW', 'Due Diligence Review'), ('SECURITY_REVIEW', 'Security Review'), ('PRIVACY_REVIEW', 'Privacy Review'), ('OPERATIONAL_REVIEW', 'Operational Review'), ('SCOPE_REVIEW', 'Scope Review'), ('GO_NO_GO_READY', 'Go/No-Go Ready'), ('MANAGER_DECISION_REQUIRED', 'Manager Decision Required'), ('GO', 'Go (Authorized)'), ('NO_GO', 'No-Go (Denied)'), ('DEFER', 'Defer (Pending)'), ('REVOKED', 'Revoked'), ('EXPIRED', 'Expired')], default='DRAFT', max_length=32)),
                ('candidate_id', models.UUIDField()),
                ('scope_hash', models.CharField(max_length=64)),
                ('release_candidate_id', models.CharField(max_length=64)),
                ('activation_window_start', models.DateTimeField(blank=True, null=True)),
                ('activation_window_end', models.DateTimeField(blank=True, null=True)),
                ('token_expiry', models.DateTimeField(blank=True, null=True)),
                ('authorized_operators', models.JSONField(blank=True, default=list)),
                ('nonce', models.CharField(max_length=64, unique=True)),
                ('audit_reference', models.UUIDField(default=uuid.uuid4)),
                ('superseded_decision_id', models.UUIDField(blank=True, null=True)),
                ('approver_id', models.UUIDField(blank=True, null=True)),
                ('is_human_manager', models.BooleanField(default=False)),
                ('is_synthetic_rehearsal', models.BooleanField(default=True)),
                ('decision_notes', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='manager_decisions', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_manager_decision_ledger',
            },
        ),
        migrations.CreateModel(
            name='DecisionEvidenceSnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('domain', models.CharField(max_length=64)),
                ('evidence_hash', models.CharField(max_length=64)),
                ('freshness_state', models.CharField(choices=[('FRESH', 'Fresh (<24h)'), ('STALE', 'Stale (>24h)'), ('EXPIRED', 'Expired (>7d)'), ('SUPERSEDED', 'Superseded')], default='FRESH', max_length=16)),
                ('raw_evidence_summary', models.TextField(blank=True, default='')),
                ('certified_by_id', models.UUIDField()),
                ('snapshot_timestamp', models.DateTimeField(auto_now_add=True)),
                ('decision', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='evidence_snapshots', to='learning.managerdecisionledger')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='decision_evidence_snapshots', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_decision_evidence_snapshot',
            },
        ),
        migrations.CreateModel(
            name='SyntheticActivationToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token_value', models.CharField(max_length=128, unique=True)),
                ('scope_hash', models.CharField(max_length=64)),
                ('release_candidate_id', models.CharField(max_length=64)),
                ('authorized_operator_id', models.UUIDField()),
                ('nonce', models.CharField(max_length=64, unique=True)),
                ('activation_window_start', models.DateTimeField()),
                ('activation_window_end', models.DateTimeField()),
                ('expiry', models.DateTimeField()),
                ('is_consumed', models.BooleanField(default=False)),
                ('consumed_at', models.DateTimeField(blank=True, null=True)),
                ('is_revoked', models.BooleanField(default=False)),
                ('revoked_at', models.DateTimeField(blank=True, null=True)),
                ('revocation_reason', models.TextField(blank=True, default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('decision', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='tokens', to='learning.managerdecisionledger')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='activation_tokens', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_synthetic_activation_token',
            },
        ),
        migrations.CreateModel(
            name='ManagerDecisionAuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(max_length=64)),
                ('actor_id', models.UUIDField()),
                ('details', models.JSONField(default=dict)),
                ('shred_receipt', models.CharField(blank=True, default='', max_length=128)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('decision', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.RESTRICT, related_name='audit_logs', to='learning.managerdecisionledger')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, related_name='manager_audit_logs', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_manager_decision_audit_log',
            },
        ),
        migrations.AddConstraint(
            model_name='managerdecisionledger',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_manager_decision_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='managerdecisionledger',
            constraint=models.UniqueConstraint(fields=('tenant', 'candidate_id', 'decision_version'), name='uq_learning_manager_decision_version'),
        ),
        migrations.AddConstraint(
            model_name='managerdecisionledger',
            constraint=models.CheckConstraint(condition=models.Q(('state__in', ['DRAFT', 'EVIDENCE_COLLECTION', 'DUE_DILIGENCE_REVIEW', 'SECURITY_REVIEW', 'PRIVACY_REVIEW', 'OPERATIONAL_REVIEW', 'SCOPE_REVIEW', 'GO_NO_GO_READY', 'MANAGER_DECISION_REQUIRED', 'GO', 'NO_GO', 'DEFER', 'REVOKED', 'EXPIRED'])), name='chk_manager_decision_state_valid'),
        ),
        migrations.AddConstraint(
            model_name='managerdecisionledger',
            constraint=models.CheckConstraint(condition=models.Q(('is_synthetic_rehearsal', True)), name='chk_manager_decision_synthetic_only'),
        ),
        migrations.AddConstraint(
            model_name='decisionevidencesnapshot',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_decision_evidence_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='decisionevidencesnapshot',
            constraint=models.CheckConstraint(condition=models.Q(('freshness_state__in', ['FRESH', 'STALE', 'EXPIRED', 'SUPERSEDED'])), name='chk_decision_evidence_freshness'),
        ),
        migrations.AddConstraint(
            model_name='syntheticactivationtoken',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_synthetic_token_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='syntheticactivationtoken',
            constraint=models.CheckConstraint(condition=models.Q(('activation_window_start__lt', models.F('activation_window_end'))), name='chk_synth_token_window_order'),
        ),
        migrations.AddConstraint(
            model_name='managerdecisionauditlog',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_manager_audit_tenant_id'),
        ),
        migrations.AddIndex(
            model_name='managerdecisionledger',
            index=models.Index(fields=['tenant', 'state'], name='idx_mgr_dec_t_st'),
        ),
        migrations.AddIndex(
            model_name='managerdecisionledger',
            index=models.Index(fields=['candidate_id', 'decision_version'], name='idx_mgr_dec_cand_ver'),
        ),
        migrations.AddIndex(
            model_name='managerdecisionledger',
            index=models.Index(fields=['nonce'], name='idx_mgr_dec_nonce'),
        ),
        migrations.AddIndex(
            model_name='decisionevidencesnapshot',
            index=models.Index(fields=['tenant', 'domain', 'freshness_state'], name='idx_dec_ev_t_dom_fr'),
        ),
        migrations.AddIndex(
            model_name='syntheticactivationtoken',
            index=models.Index(fields=['tenant', 'token_value'], name='idx_token_t_val'),
        ),
        migrations.AddIndex(
            model_name='syntheticactivationtoken',
            index=models.Index(fields=['nonce'], name='idx_token_nonce'),
        ),
        migrations.AddIndex(
            model_name='managerdecisionauditlog',
            index=models.Index(fields=['tenant', 'action_type', '-created_at'], name='idx_mgr_audit_t_act_cr'),
        ),
        migrations.RunPython(
            code=enable_p7_postgres_rls,
            reverse_code=disable_p7_postgres_rls,
        ),
    ]
