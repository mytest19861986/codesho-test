"""
Domain models and Enums for Phase 9 Synthetic Pilot Activation.
Enforces strict typing and zero-real-data invariants.
"""

from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import uuid
import datetime

class ActivationState(str, Enum):
    DRAFT = "DRAFT"
    PRECHECK_PENDING = "PRECHECK_PENDING"
    MANAGER_DECISION_REQUIRED = "MANAGER_DECISION_REQUIRED"
    SCOPE_LOCKED = "SCOPE_LOCKED"
    AUTHORIZATION_READY = "AUTHORIZATION_READY"
    ACTIVATION_READY = "ACTIVATION_READY"
    ACTIVATING = "ACTIVATING"
    ACTIVE_SYNTHETIC = "ACTIVE_SYNTHETIC"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    ROLLING_BACK = "ROLLING_BACK"
    ROLLED_BACK = "ROLLED_BACK"
    EMERGENCY_ABORTED = "EMERGENCY_ABORTED"
    FAILED_CLOSED = "FAILED_CLOSED"

class DataClassification(str, Enum):
    SYNTHETIC = "SYNTHETIC"
    TEST_FIXTURE = "TEST_FIXTURE"
    NON_PII = "NON_PII"
    REAL_CHILD = "REAL_CHILD"
    REAL_GUARDIAN = "REAL_GUARDIAN"
    REAL_SCHOOL = "REAL_SCHOOL"
    UNKNOWN = "UNKNOWN"

class RehearsalScope(BaseModel):
    tenant_id: str
    tenant_count: int = 1
    max_students: int = 50
    max_duration_days: int = 14
    environment: str = "SYNTHETIC_TEST"
    features: List[str] = Field(default_factory=lambda: ["COURSES", "QUIZZES", "ATTENDANCE"])
    data_classes: List[DataClassification] = Field(default_factory=lambda: [DataClassification.SYNTHETIC, DataClassification.TEST_FIXTURE, DataClassification.NON_PII])
    payment_mode: str = "STUB_DISABLED"
    communication_mode: str = "STUB_DISABLED"
    activation_version: str = "9.0.1"

class ActivationToken(BaseModel):
    token_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    authorized_scope: Dict[str, Any]
    scope_digest: str
    issued_at: datetime.datetime
    expires_at: datetime.datetime
    purpose: str = "SYNTHETIC_ACTIVATION_REHEARSAL"
    decision_reference: str
    nonce: str
    revoked: bool = False
    signature: str

class AuditRecord(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime.datetime = Field(default_factory=lambda: datetime.datetime.now(datetime.timezone.utc))
    actor: str
    tenant_id: str
    command: str
    source_state: ActivationState
    target_state: ActivationState
    scope_digest: str
    token_id: Optional[str] = None
    outcome: str
    failure_reason: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
