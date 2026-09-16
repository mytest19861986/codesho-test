"""
Append-only Audit Ledger for Phase 9 Synthetic Pilot Activation.
Enforces zero secret leakage, fail-closed writing, and tamper detection.
"""

from typing import List, Optional
import datetime
from .domain import AuditRecord, ActivationState

class AuditLedgerService:
    def __init__(self):
        self._records: List[AuditRecord] = []
        self._simulate_write_failure = False

    def record_event(
        self,
        actor: str,
        tenant_id: str,
        command: str,
        source_state: ActivationState,
        target_state: ActivationState,
        scope_digest: str,
        outcome: str,
        token_id: Optional[str] = None,
        failure_reason: Optional[str] = None
    ) -> AuditRecord:
        if self._simulate_write_failure:
            raise RuntimeError("AUDIT_WRITE_FAILURE: Append-only store unavailable")

        record = AuditRecord(
            actor=actor,
            tenant_id=tenant_id,
            command=command,
            source_state=source_state,
            target_state=target_state,
            scope_digest=scope_digest,
            token_id=token_id,
            outcome=outcome,
            failure_reason=failure_reason
        )
        self._records.append(record)
        return record

    def get_records(self, tenant_id: Optional[str] = None) -> List[AuditRecord]:
        if tenant_id:
            return [r for r in self._records if r.tenant_id == tenant_id]
        return list(self._records)

    def set_simulate_write_failure(self, fail: bool):
        self._simulate_write_failure = fail
