from importlib import import_module
from unittest.mock import MagicMock, Mock, call

import pytest
from django.db.migrations.exceptions import IrreversibleError


@pytest.fixture
def migration():
    return import_module(
        "modules.platform_event.migrations.0007_passcode_change_challenge_allow_list"
    )


def test_passcode_change_audit_allow_list_is_additive_atomic_and_forward_only(migration):
    assert migration.Migration.atomic is True
    assert set(migration.PREVIOUS_EVENT_TYPES) <= set(migration.EVENT_TYPES)
    assert set(migration.PREVIOUS_REASON_CODES) <= set(migration.REASON_CODES)
    assert "passcode_change_challenge_issued" in migration.EVENT_TYPES
    assert "challenge_revoked_pepper_rotation" in migration.REASON_CODES
    with pytest.raises(IrreversibleError):
        migration.irreversible(None, None)


def test_migration_requires_expected_predecessor_constraint_definitions(migration):
    assert migration.Migration.dependencies == [
        ("platform_event", "0006_passcode_change_required_reason")
    ]
    assert "passcode_change_required" in migration.PREVIOUS_REASON_CODES
    assert "passcode_change_challenge_issued" not in migration.PREVIOUS_EVENT_TYPES
    assert "challenge_issued" not in migration.PREVIOUS_REASON_CODES


@pytest.mark.parametrize(
    ("column", "nullable", "previous_values"),
    [
        ("event_type", False, "PREVIOUS_EVENT_TYPES"),
        ("reason_code", True, "PREVIOUS_REASON_CODES"),
    ],
)
def test_expected_constraint_sql_has_one_column_reference_before_in(
    migration, column, nullable, previous_values
):
    cursor = Mock()
    cursor.fetchone.return_value = ("expected",)

    migration._expected_constraint(cursor, column, nullable)

    statement = cursor.execute.call_args_list[0].args[0]
    values = migration._values(getattr(migration, previous_values))
    expected_condition = f"{column} IS NULL OR {column} IN" if nullable else f"{column} IN"
    assert f"CHECK ({expected_condition} ({values}))" in statement


def test_mismatch_aborts_before_any_constraint_replacement(migration):
    cursor = Mock()
    cursor.fetchone.side_effect = [("expected",), ("unexpected", True)]
    connection = MagicMock(vendor="postgresql")
    connection.cursor.return_value.__enter__.return_value = cursor
    schema_editor = Mock(connection=connection)

    with pytest.raises(RuntimeError, match="does not match the expected allow-list"):
        migration.extend_passcode_change_allow_lists(None, schema_editor)

    schema_editor.execute.assert_not_called()


@pytest.mark.parametrize("current", [None, ("expected", False)])
def test_missing_or_unvalidated_constraint_aborts_before_replacement(migration, current):
    cursor = Mock()
    cursor.fetchone.side_effect = [("expected",), current]
    connection = MagicMock(vendor="postgresql")
    connection.cursor.return_value.__enter__.return_value = cursor
    schema_editor = Mock(connection=connection)

    with pytest.raises(RuntimeError, match="missing or unvalidated"):
        migration.extend_passcode_change_allow_lists(None, schema_editor)

    schema_editor.execute.assert_not_called()


def test_matching_validated_constraints_replace_both_allow_lists(migration):
    cursor = Mock()
    cursor.fetchone.side_effect = [
        ("event expected",),
        ("event expected", True),
        ("reason expected",),
        ("reason expected", True),
    ]
    connection = MagicMock(vendor="postgresql")
    connection.cursor.return_value.__enter__.return_value = cursor
    schema_editor = Mock(connection=connection)

    migration.extend_passcode_change_allow_lists(None, schema_editor)

    expected_statements = [
        "ALTER TABLE audit.identity_security_event "
        "DROP CONSTRAINT identity_security_event_type_valid",
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_type_valid "
        f"CHECK (event_type IN ({migration._values(migration.EVENT_TYPES)}))",
        "ALTER TABLE audit.identity_security_event "
        "DROP CONSTRAINT identity_security_event_reason_code_valid",
        "ALTER TABLE audit.identity_security_event "
        "ADD CONSTRAINT identity_security_event_reason_code_valid "
        f"CHECK (reason_code IS NULL OR reason_code IN "
        f"({migration._values(migration.REASON_CODES)}))",
    ]
    assert schema_editor.execute.call_args_list == [
        call(statement) for statement in expected_statements
    ]


def test_non_postgres_empty_test_database_is_a_noop(migration):
    schema_editor = Mock()
    schema_editor.connection.vendor = "sqlite"

    migration.extend_passcode_change_allow_lists(None, schema_editor)

    schema_editor.connection.cursor.assert_not_called()
    schema_editor.execute.assert_not_called()
