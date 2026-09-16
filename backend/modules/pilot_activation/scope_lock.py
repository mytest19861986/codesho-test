"""
Scope Lock service for Phase 9 Synthetic Activation.
Freezes scope parameters, prevents unauthorized scope creep, and validates data classification.
"""

import hashlib
import json
from typing import Tuple
from .domain import RehearsalScope, DataClassification

class ScopeLockService:
    @staticmethod
    def calculate_digest(scope: RehearsalScope) -> str:
        canonical_json = json.dumps(scope.model_dump(), sort_keys=True)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    @staticmethod
    def validate_data_admission(scope: RehearsalScope) -> Tuple[bool, str]:
        for dc in scope.data_classes:
            if dc in [DataClassification.REAL_CHILD, DataClassification.REAL_GUARDIAN, DataClassification.REAL_SCHOOL]:
                return False, "REAL_DATA_PROHIBITED"
            if dc == DataClassification.UNKNOWN:
                return False, "UNKNOWN_DATA_CLASSIFICATION_FAIL_CLOSED"
        return True, "DATA_ADMISSION_PASS"

    @staticmethod
    def verify_no_scope_drift(locked_digest: str, current_scope: RehearsalScope) -> Tuple[bool, str]:
        current_digest = ScopeLockService.calculate_digest(current_scope)
        if current_digest != locked_digest:
            return False, "SCOPE_DRIFT_DETECTED"
        return True, "SCOPE_INTACT"
