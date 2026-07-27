from django.db import migrations, models
from django.db.models import Q

SECURITY_EVENT_TYPES = (
    "passcode_created",
    "passcode_changed",
    "passcode_verification_failed",
    "account_locked",
    "account_unlocked",
    "abuse_global_alert",
    "temporary_passcode_issued",
    "temporary_passcode_consumed",
    "guardian_reset_started",
    "guardian_reset_completed",
    "authentication_succeeded",
    "authentication_failed",
    "authentication_blocked",
    "session_logged_out",
    "passcode_change_challenge_issued",
    "passcode_change_challenge_revoked",
    "passcode_change_challenge_consumed",
    "passcode_change_challenge_expired",
    "passcode_change_rejected",
    "admin_user_viewed",
    "admin_user_action_denied",
    "admin_tenant_access_denied",
    "admin_policy_evaluated",
    "adult_age_attestation_accepted",
    "adult_signup_rejected_age_attestation_missing",
    "synthetic_account_bootstrapped",
)
SECURITY_EVENT_REASON_CODES = (
    "credential_created",
    "credential_changed",
    "verification_mismatch",
    "lock_threshold_reached",
    "lock_cleared",
    "abuse_threshold_reached",
    "temporary_credential_issued",
    "temporary_credential_consumed",
    "guardian_reset_requested",
    "guardian_reset_confirmed",
    "login_succeeded",
    "login_failed",
    "login_blocked",
    "session_logged_out",
    "passcode_change_required",
    "challenge_issued",
    "challenge_superseded",
    "challenge_consumed",
    "challenge_expired",
    "challenge_invalid",
    "passcode_same_as_current",
    "challenge_revoked_pepper_rotation",
    "admin_user_viewed",
    "admin_user_action_denied",
    "admin_tenant_access_denied",
    "admin_policy_evaluated",
    "adult_attested",
    "age_attestation_required",
    "synthetic_bootstrap_created",
)


def _values(values):
    return ", ".join(repr(value) for value in values)


def extend_allow_lists(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event DROP CONSTRAINT "
        "identity_security_event_type_valid"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event ADD CONSTRAINT "
        "identity_security_event_type_valid "
        f"CHECK (event_type IN ({_values(SECURITY_EVENT_TYPES)}))"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event DROP CONSTRAINT "
        "identity_security_event_reason_code_valid"
    )
    schema_editor.execute(
        "ALTER TABLE audit.identity_security_event ADD CONSTRAINT "
        "identity_security_event_reason_code_valid "
        f"CHECK (reason_code IS NULL OR reason_code IN ({_values(SECURITY_EVENT_REASON_CODES)}))"
    )


def irreversible(apps, schema_editor):
    from django.db.migrations.exceptions import IrreversibleError

    raise IrreversibleError("immutable audit allow-list must move forward")


class Migration(migrations.Migration):
    atomic = True
    dependencies = [("platform_event", "0010_adult_signup_events")]
    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunPython(extend_allow_lists, reverse_code=irreversible)
            ],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name="identitysecurityevent",
                    name="identity_security_event_type_valid",
                ),
                migrations.AddConstraint(
                    model_name="identitysecurityevent",
                    constraint=models.CheckConstraint(
                        condition=Q(event_type__in=SECURITY_EVENT_TYPES),
                        name="identity_security_event_type_valid",
                    ),
                ),
                migrations.RemoveConstraint(
                    model_name="identitysecurityevent",
                    name="identity_security_event_reason_code_valid",
                ),
                migrations.AddConstraint(
                    model_name="identitysecurityevent",
                    constraint=models.CheckConstraint(
                        condition=Q(reason_code__isnull=True)
                        | Q(reason_code__in=SECURITY_EVENT_REASON_CODES),
                        name="identity_security_event_reason_code_valid",
                    ),
                ),
            ],
        )
    ]
