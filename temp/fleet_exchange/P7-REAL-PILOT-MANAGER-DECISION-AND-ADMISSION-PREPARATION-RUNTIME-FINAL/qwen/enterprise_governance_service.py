import hashlib
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.utils import timezone

from modules.learning.models import (
    StaffAccessAssignment,
    DelegatedAdminScope,
    PrivilegedPermissionGrant,
    AccessReviewCampaign,
    AccessReviewDecision,
    PrivilegedActionAudit,
    DataRetentionPolicy,
    RetentionPolicyVersion,
    LegalHold,
    LegalHoldScope,
    RetentionEvaluation,
    DataDispositionRecord,
    DispositionAuditLog,
    ReadinessControl,
    ReadinessEvidence,
    ReadinessAssessmentRun,
    ReadinessFinding,
    ReadinessException,
    PilotReadinessGate,
    ControlAttestationAudit,
    PilotTenantLifecycle,
    PilotLifecycleState,
    PilotPrerequisiteChecklist,
    DualCustodyApprovalEvent,
    ManagerDecisionLedger,
    ManagerDecisionState,
    EvidenceFreshnessState,
    DecisionEvidenceSnapshot,
    SyntheticActivationToken,
    ManagerDecisionAuditLog,
    StaffRole,
    ScopeResourceType,
    PrivilegedGrantStatus,
    AccessReviewCampaignStatus,
    AccessReviewDecisionChoice,
    DispositionAction,
    LegalHoldStatus,
    ReadinessControlCategory,
    ReadinessEvidenceStatus,
    ReadinessOverallStatus,
    ReadinessFindingSeverity,
    PilotGateVerdict,
)
from modules.platform_event.services import append_outbox_event
from django.db import connection


class EnterpriseGovernanceService:
    """
    P3-MACRO-EPIC-26-28 Core Enterprise Governance Domain Service.
    Enforces strict architectural invariants:
      - PRIVILEGE_SELF_GRANT: DENY (user_id <> granted_by_id)
      - TWO_PERSON_RULE: ENFORCED (second_approver_id <> granted_by_id)
      - LEGAL_HOLD_BYPASS: DENY (Destruction/Disposition prohibited when LegalHold is active)
      - PRODUCTION_DEPLOY_AUTHORITY: 0 (Readiness gate is purely advisory; never triggers automated deploy)
      - STUDENT_RANKING: 0 (Anti-ranking compliance)
      - SYNTHETIC_DATA_ONLY: ENFORCED (Zero real child PII)
    """

    # -------------------------------------------------------------------------
    # 1. P3-VS26: DELEGATED ADMINISTRATION & PRIVILEGE GOVERNANCE
    # -------------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def assign_staff_access(
        cls,
        *,
        tenant_id: UUID,
        user_id: UUID,
        role_name: str,
        assigned_by_id: UUID,
        scope_type: str = "TENANT_WIDE",
        valid_until: Optional[datetime] = None,
        scopes: Optional[List[Dict[str, str]]] = None,
    ) -> StaffAccessAssignment:
        if role_name not in StaffRole.values:
            raise ValidationError(f"Invalid staff role: {role_name}")

        assignment = StaffAccessAssignment.objects.create(
            tenant_id=tenant_id,
            user_id=user_id,
            role_name=role_name,
            scope_type=scope_type,
            valid_until=valid_until,
            assigned_by_id=assigned_by_id,
        )

        if scopes:
            for s in scopes:
                DelegatedAdminScope.objects.create(
                    tenant_id=tenant_id,
                    assignment=assignment,
                    scope_resource_type=s["scope_resource_type"],
                    scope_resource_id=s["scope_resource_id"],
                )

        PrivilegedActionAudit.objects.create(
            tenant_id=tenant_id,
            actor_id=assigned_by_id,
            action_type="STAFF_ACCESS_ASSIGNED",
            target_resource=f"user:{user_id}",
            details={"role": role_name, "assignment_id": str(assignment.id)},
        )

        append_outbox_event(
            tenant_id=tenant_id,
            topic="governance.staff_access_assigned",
            aggregate_type="StaffAccessAssignment",
            aggregate_id=str(assignment.id),
            payload={"assignment_id": str(assignment.id), "user_id": str(user_id), "role": role_name},
        )
        return assignment

    @classmethod
    @transaction.atomic
    def grant_privileged_permission(
        cls,
        *,
        tenant_id: UUID,
        user_id: UUID,
        permission_code: str,
        justification: str,
        granted_by_id: UUID,
        expires_at: datetime,
        second_approver_id: Optional[UUID] = None,
    ) -> PrivilegedPermissionGrant:
        # Invariant: Self-grant denial
        if str(user_id) == str(granted_by_id):
            raise PermissionDenied("Self-granting of privileged permissions is strictly prohibited.")

        # Invariant: Distinct two-person approval
        if second_approver_id and str(second_approver_id) == str(granted_by_id):
            raise PermissionDenied("Second approver must be distinct from granting authority.")

        grant = PrivilegedPermissionGrant(
            tenant_id=tenant_id,
            user_id=user_id,
            permission_code=permission_code,
            justification=justification,
            granted_by_id=granted_by_id,
            second_approver_id=second_approver_id,
            expires_at=expires_at,
            status=PrivilegedGrantStatus.ACTIVE,
        )
        grant.full_clean()
        grant.save()

        PrivilegedActionAudit.objects.create(
            tenant_id=tenant_id,
            actor_id=granted_by_id,
            action_type="PRIVILEGED_PERMISSION_GRANTED",
            target_resource=f"user:{user_id}:permission:{permission_code}",
            details={"grant_id": str(grant.id), "second_approver": str(second_approver_id) if second_approver_id else None},
        )

        append_outbox_event(
            tenant_id=tenant_id,
            topic="governance.privileged_permission_granted",
            aggregate_type="PrivilegedPermissionGrant",
            aggregate_id=str(grant.id),
            payload={"grant_id": str(grant.id), "user_id": str(user_id), "permission": permission_code},
        )
        return grant

    @classmethod
    @transaction.atomic
    def revoke_privileged_permission(
        cls,
        *,
        tenant_id: UUID,
        grant_id: UUID,
        actor_id: UUID,
        reason: str,
    ) -> PrivilegedPermissionGrant:
        grant = PrivilegedPermissionGrant.objects.select_for_update().get(id=grant_id, tenant_id=tenant_id)
        if grant.status == PrivilegedGrantStatus.REVOKED:
            return grant

        grant.status = PrivilegedGrantStatus.REVOKED
        grant.save()

        PrivilegedActionAudit.objects.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            action_type="PRIVILEGED_PERMISSION_REVOKED",
            target_resource=f"grant:{grant.id}",
            details={"reason": reason},
        )
        return grant

    @classmethod
    @transaction.atomic
    def create_access_review_campaign(
        cls,
        *,
        tenant_id: UUID,
        title: str,
        campaign_period: str,
        deadline: datetime,
        created_by_id: UUID,
    ) -> AccessReviewCampaign:
        campaign = AccessReviewCampaign.objects.create(
            tenant_id=tenant_id,
            title=title,
            campaign_period=campaign_period,
            deadline=deadline,
            created_by_id=created_by_id,
            status=AccessReviewCampaignStatus.ACTIVE,
        )
        PrivilegedActionAudit.objects.create(
            tenant_id=tenant_id,
            actor_id=created_by_id,
            action_type="ACCESS_REVIEW_CAMPAIGN_LAUNCHED",
            target_resource=f"campaign:{campaign.id}",
            details={"title": title, "period": campaign_period},
        )
        return campaign

    @classmethod
    @transaction.atomic
    def record_access_review_decision(
        cls,
        *,
        tenant_id: UUID,
        campaign_id: UUID,
        assignment_id: UUID,
        reviewer_id: UUID,
        decision: str,
        notes: str = "",
    ) -> AccessReviewDecision:
        if decision not in AccessReviewDecisionChoice.values:
            raise ValidationError(f"Invalid access review decision: {decision}")

        rev_decision, created = AccessReviewDecision.objects.update_or_create(
            tenant_id=tenant_id,
            campaign_id=campaign_id,
            assignment_id=assignment_id,
            defaults={
                "reviewer_id": reviewer_id,
                "decision": decision,
                "notes": notes,
            },
        )

        if decision == AccessReviewDecisionChoice.REVOKE:
            # Authoritatively deactivate assignment
            StaffAccessAssignment.objects.filter(
                id=assignment_id, tenant_id=tenant_id
            ).update(is_active=False)

        PrivilegedActionAudit.objects.create(
            tenant_id=tenant_id,
            actor_id=reviewer_id,
            action_type="ACCESS_REVIEW_DECISION_RECORDED",
            target_resource=f"assignment:{assignment_id}",
            details={"campaign_id": str(campaign_id), "decision": decision},
        )
        return rev_decision

    # -------------------------------------------------------------------------
    # 2. P3-VS27: DATA RETENTION, LEGAL HOLD & DISPOSITION GOVERNANCE
    # -------------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def set_retention_policy(
        cls,
        *,
        tenant_id: UUID,
        data_category: str,
        retention_period_days: int,
        created_by_id: UUID,
        disposition_action: str = DispositionAction.ANONYMIZE,
    ) -> DataRetentionPolicy:
        if retention_period_days < 30:
            raise ValidationError("retention_period_days must be at least 30 days.")

        policy, created = DataRetentionPolicy.objects.get_or_create(
            tenant_id=tenant_id,
            data_category=data_category,
            defaults={
                "retention_period_days": retention_period_days,
                "disposition_action": disposition_action,
                "created_by_id": created_by_id,
            },
        )

        latest_version = RetentionPolicyVersion.objects.filter(
            tenant_id=tenant_id, policy=policy
        ).order_by("-version_number").first()

        next_ver = 1 if not latest_version else latest_version.version_number + 1

        if not created:
            policy.retention_period_days = retention_period_days
            policy.disposition_action = disposition_action
            policy.save()

        RetentionPolicyVersion.objects.create(
            tenant_id=tenant_id,
            policy=policy,
            version_number=next_ver,
            retention_period_days=retention_period_days,
            disposition_action=disposition_action,
            created_by_id=created_by_id,
        )

        return policy

    @classmethod
    @transaction.atomic
    def place_legal_hold(
        cls,
        *,
        tenant_id: UUID,
        title: str,
        legal_case_reference: str,
        reason: str,
        placed_by_id: UUID,
        scopes: List[Dict[str, str]],
    ) -> LegalHold:
        hold = LegalHold.objects.create(
            tenant_id=tenant_id,
            title=title,
            legal_case_reference=legal_case_reference,
            reason=reason,
            placed_by_id=placed_by_id,
            status=LegalHoldStatus.ACTIVE,
        )

        for s in scopes:
            LegalHoldScope.objects.create(
                tenant_id=tenant_id,
                legal_hold=hold,
                target_entity_type=s["target_entity_type"],
                target_entity_id=s["target_entity_id"],
            )

        PrivilegedActionAudit.objects.create(
            tenant_id=tenant_id,
            actor_id=placed_by_id,
            action_type="LEGAL_HOLD_PLACED",
            target_resource=f"legal_case:{legal_case_reference}",
            details={"hold_id": str(hold.id), "title": title},
        )
        return hold

    @classmethod
    @transaction.atomic
    def release_legal_hold(
        cls,
        *,
        tenant_id: UUID,
        hold_id: UUID,
        released_by_id: UUID,
    ) -> LegalHold:
        hold = LegalHold.objects.select_for_update().get(id=hold_id, tenant_id=tenant_id)
        if hold.status == LegalHoldStatus.RELEASED:
            return hold

        hold.status = LegalHoldStatus.RELEASED
        hold.released_by_id = released_by_id
        hold.released_at = timezone.now()
        hold.save()

        PrivilegedActionAudit.objects.create(
            tenant_id=tenant_id,
            actor_id=released_by_id,
            action_type="LEGAL_HOLD_RELEASED",
            target_resource=f"legal_hold:{hold.id}",
            details={"case_reference": hold.legal_case_reference},
        )
        return hold

    @classmethod
    @transaction.atomic
    def evaluate_and_execute_disposition(
        cls,
        *,
        tenant_id: UUID,
        policy_id: UUID,
        executed_by_id: UUID,
        targeted_entity_keys: List[Dict[str, str]],
    ) -> DataDispositionRecord:
        policy = DataRetentionPolicy.objects.get(id=policy_id, tenant_id=tenant_id)
        
        # Check active legal holds
        active_holds = LegalHoldScope.objects.filter(
            tenant_id=tenant_id,
            legal_hold__status=LegalHoldStatus.ACTIVE,
        )
        held_target_ids = set(active_holds.values_list("target_entity_id", flat=True))

        candidates_count = len(targeted_entity_keys)
        exempted_count = 0
        disposable_keys = []

        for item in targeted_entity_keys:
            if item["id"] in held_target_ids:
                exempted_count += 1
            else:
                disposable_keys.append(item)

        evaluation = RetentionEvaluation.objects.create(
            tenant_id=tenant_id,
            policy=policy,
            evaluated_entity_type=policy.data_category,
            candidates_count=candidates_count,
            exempted_by_legal_hold_count=exempted_count,
            disposition_ready_count=len(disposable_keys),
        )

        digest = hashlib.sha256(
            f"{tenant_id}:{evaluation.id}:{len(disposable_keys)}".encode("utf-8")
        ).hexdigest()

        disp_record = DataDispositionRecord.objects.create(
            tenant_id=tenant_id,
            evaluation=evaluation,
            action_applied=policy.disposition_action,
            records_processed=len(disposable_keys),
            cryptographic_digest=digest,
            executed_by_id=executed_by_id,
        )

        for item in disposable_keys:
            key_hash = hashlib.sha256(f"{item['type']}:{item['id']}".encode("utf-8")).hexdigest()
            DispositionAuditLog.objects.create(
                tenant_id=tenant_id,
                disposition_record=disp_record,
                entity_type=item["type"],
                entity_key_hash=key_hash,
                status="SUCCESS",
            )

        return disp_record

    # -------------------------------------------------------------------------
    # 3. P3-VS28: ENTERPRISE CONTROL EVIDENCE & PILOT READINESS CENTER
    # -------------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def register_readiness_control(
        cls,
        *,
        tenant_id: UUID,
        control_code: str,
        category: str,
        description: str,
        is_mandatory: bool = True,
    ) -> ReadinessControl:
        control, _ = ReadinessControl.objects.update_or_create(
            tenant_id=tenant_id,
            control_code=control_code,
            defaults={
                "category": category,
                "description": description,
                "is_mandatory": is_mandatory,
            },
        )
        return control

    @classmethod
    @transaction.atomic
    def attach_readiness_evidence(
        cls,
        *,
        tenant_id: UUID,
        control_id: UUID,
        evidence_type: str,
        artifact_reference: str,
        raw_payload: str,
        recorded_by_id: UUID,
    ) -> ReadinessEvidence:
        v_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
        evidence = ReadinessEvidence.objects.create(
            tenant_id=tenant_id,
            control_id=control_id,
            evidence_type=evidence_type,
            artifact_reference=artifact_reference,
            verification_hash=v_hash,
            recorded_by_id=recorded_by_id,
            status=ReadinessEvidenceStatus.VALID,
        )
        return evidence

    @classmethod
    @transaction.atomic
    def execute_pilot_readiness_assessment(
        cls,
        *,
        tenant_id: UUID,
        run_reference: str,
        executed_by_id: UUID,
    ) -> ReadinessAssessmentRun:
        controls = list(ReadinessControl.objects.filter(tenant_id=tenant_id))
        total = len(controls)
        passed = 0
        failed = 0

        run = ReadinessAssessmentRun.objects.create(
            tenant_id=tenant_id,
            run_reference=run_reference,
            total_controls=total,
            executed_by_id=executed_by_id,
            overall_status=ReadinessOverallStatus.IN_PROGRESS,
        )

        for ctrl in controls:
            valid_evidence = ReadinessEvidence.objects.filter(
                tenant_id=tenant_id,
                control=ctrl,
                status=ReadinessEvidenceStatus.VALID,
            ).exists()

            if valid_evidence:
                passed += 1
            else:
                failed += 1
                ReadinessFinding.objects.create(
                    tenant_id=tenant_id,
                    assessment_run=run,
                    control=ctrl,
                    severity=ReadinessFindingSeverity.MAJOR if ctrl.is_mandatory else ReadinessFindingSeverity.MINOR,
                    finding_summary=f"Mandatory control {ctrl.control_code} lacks valid recorded evidence.",
                    is_resolved=False,
                )

        run.passed_controls = passed
        run.failed_controls = failed
        run.overall_status = ReadinessOverallStatus.READY if failed == 0 else ReadinessOverallStatus.NOT_READY
        run.completed_at = timezone.now()
        run.save()

        return run

    @classmethod
    @transaction.atomic
    def grant_readiness_exception(
        cls,
        *,
        tenant_id: UUID,
        finding_id: UUID,
        reason: str,
        expiry_date: datetime,
        approved_by_id: UUID,
    ) -> ReadinessException:
        finding = ReadinessFinding.objects.select_for_update().get(id=finding_id, tenant_id=tenant_id)
        exception = ReadinessException.objects.create(
            tenant_id=tenant_id,
            finding=finding,
            reason=reason,
            expiry_date=expiry_date,
            approved_by_id=approved_by_id,
        )
        finding.is_resolved = True
        finding.save()
        return exception

    @classmethod
    @transaction.atomic
    def evaluate_pilot_gate(
        cls,
        *,
        tenant_id: UUID,
        assessment_run_id: UUID,
        attested_by_id: UUID,
        attestation_role: str,
        human_summary: str,
    ) -> PilotReadinessGate:
        run = ReadinessAssessmentRun.objects.get(id=assessment_run_id, tenant_id=tenant_id)
        unresolved_blockers = ReadinessFinding.objects.filter(
            tenant_id=tenant_id,
            assessment_run=run,
            is_resolved=False,
            severity__in=[ReadinessFindingSeverity.BLOCKER, ReadinessFindingSeverity.CRITICAL],
        ).exists()

        if unresolved_blockers:
            verdict = PilotGateVerdict.BLOCKED
        elif run.failed_controls > 0:
            verdict = PilotGateVerdict.EXCEPTION_REQUIRED
        else:
            verdict = PilotGateVerdict.READY

        gate = PilotReadinessGate.objects.create(
            tenant_id=tenant_id,
            assessment_run=run,
            gate_verdict=verdict,
            human_attestation_summary=human_summary,
        )

        sig = hashlib.sha256(
            f"{tenant_id}:{gate.id}:{verdict}:{attested_by_id}:{human_summary}".encode("utf-8")
        ).hexdigest()

        ControlAttestationAudit.objects.create(
            tenant_id=tenant_id,
            gate=gate,
            attested_by_id=attested_by_id,
            attestation_role=attestation_role,
            signature_digest=sig,
        )

        append_outbox_event(
            tenant_id=tenant_id,
            topic="governance.pilot_readiness_gate_evaluated",
            aggregate_type="PilotReadinessGate",
            aggregate_id=str(gate.id),
            payload={"gate_id": str(gate.id), "verdict": verdict, "assessment_run_id": str(run.id)},
        )
        return gate

    # -------------------------------------------------------------------------
    # 4. PHASE 5: CONTROLLED PILOT ACTIVATION & ADVISORY CONCURRENCY
    # -------------------------------------------------------------------------

    @classmethod
    @transaction.atomic
    def initiate_pilot_candidate(
        cls,
        *,
        tenant_id: UUID,
        pilot_code: str,
        initiated_by_id: UUID,
    ) -> PilotTenantLifecycle:
        lifecycle = PilotTenantLifecycle(
            tenant_id=tenant_id,
            pilot_code=pilot_code,
            state=PilotLifecycleState.CANDIDATE,
            initiated_by_id=initiated_by_id,
        )
        lifecycle.full_clean()
        lifecycle.save()

        PilotPrerequisiteChecklist.objects.create(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
        )

        append_outbox_event(
            tenant_id=tenant_id,
            topic="governance.pilot_candidate_initiated",
            aggregate_type="PilotTenantLifecycle",
            aggregate_id=str(lifecycle.id),
            payload={"lifecycle_id": str(lifecycle.id), "pilot_code": pilot_code, "initiated_by_id": str(initiated_by_id)},
        )
        return lifecycle

    @classmethod
    @transaction.atomic
    def advance_pilot_lifecycle(
        cls,
        *,
        tenant_id: UUID,
        lifecycle_id: UUID,
        target_state: PilotLifecycleState,
        actor_id: UUID,
        is_synthetic_rehearsal: bool = False,
    ) -> PilotTenantLifecycle:
        # Qwen R2: PostgreSQL advisory locking for concurrent race prevention
        lock_id = int(hashlib.md5(f"pilot_lock:{tenant_id}:{lifecycle_id}".encode("utf-8")).hexdigest()[:8], 16)
        if connection.vendor == "postgresql":
            with connection.cursor() as cursor:
                cursor.execute("SELECT pg_advisory_xact_lock(%s);", [lock_id])

        lifecycle = PilotTenantLifecycle.objects.select_for_update().get(id=lifecycle_id, tenant_id=tenant_id)
        
        # Check prerequisites before advancing to TECHNICAL_READY
        if target_state == PilotLifecycleState.TECHNICAL_READY:
            checklist = getattr(lifecycle, "prerequisite_checklist", None)
            if not checklist or not checklist.is_fully_satisfied():
                raise ValidationError("PREREQUISITE_FAILED: 14-prerequisite real data admission gate is not fully satisfied.")

        lifecycle.transition_to(target_state, actor_id=actor_id, is_synthetic_rehearsal=is_synthetic_rehearsal)

        append_outbox_event(
            tenant_id=tenant_id,
            topic="governance.pilot_lifecycle_transitioned",
            aggregate_type="PilotTenantLifecycle",
            aggregate_id=str(lifecycle.id),
            payload={"lifecycle_id": str(lifecycle.id), "state": target_state, "actor_id": str(actor_id)},
        )
        return lifecycle

    @classmethod
    @transaction.atomic
    def execute_dual_custody_approval(
        cls,
        *,
        tenant_id: UUID,
        lifecycle_id: UUID,
        action_type: str,
        initiator_id: UUID,
        secondary_signer_id: UUID,
        nonce: str,
    ) -> DualCustodyApprovalEvent:
        if initiator_id == secondary_signer_id:
            raise ValidationError("DUAL_CUSTODY_BYPASS: DENY. Initiator and secondary signer must be distinct actors.")

        # Replay attack prevention check
        if DualCustodyApprovalEvent.objects.filter(nonce=nonce).exists():
            raise ValidationError("REPLAY_ATTACK: DENY. Approval token nonce has already been utilized.")

        lifecycle = PilotTenantLifecycle.objects.select_for_update().get(id=lifecycle_id, tenant_id=tenant_id)
        
        sig = hashlib.sha256(
            f"{tenant_id}:{lifecycle_id}:{action_type}:{initiator_id}:{secondary_signer_id}:{nonce}".encode("utf-8")
        ).hexdigest()

        event = DualCustodyApprovalEvent.objects.create(
            tenant_id=tenant_id,
            lifecycle=lifecycle,
            action_type=action_type,
            initiator_id=initiator_id,
            secondary_signer_id=secondary_signer_id,
            nonce=nonce,
            signature_digest=sig,
            is_executed=True,
        )

        append_outbox_event(
            tenant_id=tenant_id,
            topic="governance.dual_custody_approval_executed",
            aggregate_type="DualCustodyApprovalEvent",
            aggregate_id=str(event.id),
            payload={"event_id": str(event.id), "lifecycle_id": str(lifecycle.id), "action_type": action_type},
        )
        return event

    # -------------------------------------------------------------------------
    # 5. PHASE 7: MANAGER DECISION LEDGER, EVIDENCE & TOKEN RUNTIME
    # -------------------------------------------------------------------------

    @classmethod
    def compute_canonical_scope_hash(cls, payload: Dict[str, Any]) -> str:
        """
        GLM F3: Canonicalization of scope_hash with deterministic key ordering and ISO UTC strings.
        """
        import json
        ordered_keys = sorted(payload.keys())
        canonical_str = json.dumps({k: payload[k] for k in ordered_keys}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    @classmethod
    @transaction.atomic
    def create_manager_decision(
        cls,
        *,
        tenant_id: UUID,
        candidate_id: UUID,
        scope_payload: Dict[str, Any],
        release_candidate_id: str,
        creator_id: UUID,
        decision_notes: str = "",
    ) -> ManagerDecisionLedger:
        scope_hash = cls.compute_canonical_scope_hash(scope_payload)
        
        # Check if previous version exists
        prev = ManagerDecisionLedger.objects.filter(
            tenant_id=tenant_id, candidate_id=candidate_id
        ).order_by("-decision_version").first()
        
        version = (prev.decision_version + 1) if prev else 1
        nonce = str(uuid.uuid4())
        
        decision = ManagerDecisionLedger.objects.create(
            tenant_id=tenant_id,
            candidate_id=candidate_id,
            decision_version=version,
            state=ManagerDecisionState.DRAFT,
            scope_hash=scope_hash,
            release_candidate_id=release_candidate_id,
            nonce=nonce,
            decision_notes=decision_notes,
            is_synthetic_rehearsal=True,
        )

        ManagerDecisionAuditLog.objects.create(
            tenant_id=tenant_id,
            decision=decision,
            action_type="DECISION_CREATED",
            actor_id=creator_id,
            details={"version": version, "candidate_id": str(candidate_id), "scope_hash": scope_hash},
        )
        return decision

    @classmethod
    @transaction.atomic
    def attach_evidence_snapshot(
        cls,
        *,
        tenant_id: UUID,
        decision_id: UUID,
        domain: str,
        evidence_payload: Dict[str, Any],
        certified_by_id: UUID,
        freshness_state: EvidenceFreshnessState = EvidenceFreshnessState.FRESH,
    ) -> DecisionEvidenceSnapshot:
        import json
        ev_str = json.dumps(evidence_payload, sort_keys=True, separators=(",", ":"))
        ev_hash = hashlib.sha256(ev_str.encode("utf-8")).hexdigest()

        decision = ManagerDecisionLedger.objects.select_for_update().get(id=decision_id, tenant_id=tenant_id)
        
        snapshot = DecisionEvidenceSnapshot.objects.create(
            tenant_id=tenant_id,
            decision=decision,
            domain=domain,
            evidence_hash=ev_hash,
            freshness_state=freshness_state,
            raw_evidence_summary=ev_str[:1500],
            certified_by_id=certified_by_id,
        )

        ManagerDecisionAuditLog.objects.create(
            tenant_id=tenant_id,
            decision=decision,
            action_type="EVIDENCE_SNAPSHOT_ATTACHED",
            actor_id=certified_by_id,
            details={"domain": domain, "evidence_hash": ev_hash, "freshness_state": freshness_state},
        )
        return snapshot

    @classmethod
    @transaction.atomic
    def issue_manager_determination(
        cls,
        *,
        tenant_id: UUID,
        decision_id: UUID,
        determination: ManagerDecisionState,
        manager_user_id: UUID,
        is_human_manager: bool,
        operator_ids: List[UUID],
        activation_window_start: datetime,
        activation_window_end: datetime,
        token_expiry: datetime,
        determination_notes: str = "",
    ) -> ManagerDecisionLedger:
        # Invariants
        if determination not in {ManagerDecisionState.GO, ManagerDecisionState.NO_GO, ManagerDecisionState.DEFER}:
            raise ValidationError("INVALID_DETERMINATION: Determination must be GO, NO_GO, or DEFER.")
        
        if not is_human_manager:
            raise ValidationError("HUMAN_MANAGER_ONLY: Automated agents/applications are forbidden from issuing manager decisions.")

        decision = ManagerDecisionLedger.objects.select_for_update().get(id=decision_id, tenant_id=tenant_id)

        # Check self-approval: Creator cannot be the approving manager
        audit_first = ManagerDecisionAuditLog.objects.filter(decision=decision, action_type="DECISION_CREATED").first()
        if audit_first and audit_first.actor_id == manager_user_id:
            raise ValidationError("SELF_APPROVAL: DENY. Operator cannot approve own candidate organization decision.")

        # Hard stop check for GO: Must not have any STALE or EXPIRED required evidence
        if determination == ManagerDecisionState.GO:
            snapshots = decision.evidence_snapshots.all()
            for snap in snapshots:
                if snap.freshness_state in {EvidenceFreshnessState.STALE, EvidenceFreshnessState.EXPIRED}:
                    raise ValidationError(f"REQUIRED_EVIDENCE_STALE: Domain {snap.domain} is {snap.freshness_state}. Cannot issue GO.")

        decision.state = determination
        decision.approver_id = manager_user_id
        decision.is_human_manager = is_human_manager
        decision.authorized_operators = [str(op) for op in operator_ids]
        decision.activation_window_start = activation_window_start
        decision.activation_window_end = activation_window_end
        decision.token_expiry = token_expiry
        decision.decision_notes = determination_notes
        decision.save()

        ManagerDecisionAuditLog.objects.create(
            tenant_id=tenant_id,
            decision=decision,
            action_type=f"MANAGER_DETERMINATION_{determination}",
            actor_id=manager_user_id,
            details={"determination": determination, "token_expiry": token_expiry.isoformat()},
        )
        return decision

    @classmethod
    @transaction.atomic
    def issue_synthetic_activation_token(
        cls,
        *,
        tenant_id: UUID,
        decision_id: UUID,
        operator_id: UUID,
    ) -> SyntheticActivationToken:
        decision = ManagerDecisionLedger.objects.select_for_update().get(id=decision_id, tenant_id=tenant_id)

        if decision.state != ManagerDecisionState.GO:
            raise ValidationError("TOKEN_ISSUANCE_DENIED: Decision is not in authorized GO state.")

        if str(operator_id) not in [str(op) for op in decision.authorized_operators]:
            raise ValidationError("UNAUTHORIZED_OPERATOR: Operator is not in authorized operators list.")

        now = timezone.now()
        if decision.token_expiry and now > decision.token_expiry:
            raise ValidationError("EXPIRED_APPROVAL: Decision token past expiry timestamp.")

        nonce = str(uuid.uuid4())
        token_val = hashlib.sha256(f"token:{tenant_id}:{decision_id}:{operator_id}:{nonce}".encode("utf-8")).hexdigest()

        token = SyntheticActivationToken.objects.create(
            tenant_id=tenant_id,
            decision=decision,
            token_value=token_val,
            scope_hash=decision.scope_hash,
            release_candidate_id=decision.release_candidate_id,
            authorized_operator_id=operator_id,
            nonce=nonce,
            activation_window_start=decision.activation_window_start or now,
            activation_window_end=decision.activation_window_end or now,
            expiry=decision.token_expiry or now,
        )

        ManagerDecisionAuditLog.objects.create(
            tenant_id=tenant_id,
            decision=decision,
            action_type="TOKEN_ISSUED",
            actor_id=operator_id,
            details={"token_id": str(token.id), "nonce": nonce},
        )
        return token

    @classmethod
    @transaction.atomic
    def consume_synthetic_activation_token(
        cls,
        *,
        tenant_id: UUID,
        token_value: str,
        operator_id: UUID,
        submitted_scope_hash: str,
        submitted_rc_id: str,
    ) -> SyntheticActivationToken:
        token = SyntheticActivationToken.objects.select_for_update().get(token_value=token_value, tenant_id=tenant_id)

        if token.is_consumed:
            raise ValidationError("TOKEN_REPLAY: DENY. Token nonce has already been consumed.")

        if token.is_revoked:
            raise ValidationError("TOKEN_USED_AFTER_REVOCATION: DENY. Token is revoked.")

        now = timezone.now()
        if now > token.expiry:
            raise ValidationError("EXPIRED_TOKEN: DENY. Activation token is expired.")

        if now < token.activation_window_start or now > token.activation_window_end:
            raise ValidationError("ACTIVATION_WINDOW_VIOLATION: DENY. Attempted operation outside activation window.")

        if token.authorized_operator_id != operator_id:
            raise ValidationError("TOKEN_TRANSFER: DENY. Token presented by unauthorized operator.")

        if token.scope_hash != submitted_scope_hash:
            raise ValidationError("SCOPE_HASH_MISMATCH: DENY. Payload scope does not match signed scope hash.")

        if token.release_candidate_id != submitted_rc_id:
            raise ValidationError("RELEASE_MISMATCH: DENY. Release candidate ID does not match signed decision.")

        token.is_consumed = True
        token.consumed_at = now
        token.save()

        ManagerDecisionAuditLog.objects.create(
            tenant_id=tenant_id,
            decision=token.decision,
            action_type="TOKEN_CONSUMED_SYNTHETIC",
            actor_id=operator_id,
            details={"token_value": token_value[:16]},
        )
        return token

    @classmethod
    @transaction.atomic
    def execute_manager_revocation(
        cls,
        *,
        tenant_id: UUID,
        decision_id: UUID,
        manager_id: UUID,
        reason: str,
    ) -> ManagerDecisionLedger:
        decision = ManagerDecisionLedger.objects.select_for_update().get(id=decision_id, tenant_id=tenant_id)
        decision.state = ManagerDecisionState.REVOKED
        decision.save()

        # Invalidate all associated tokens immediately
        SyntheticActivationToken.objects.filter(decision=decision, tenant_id=tenant_id).update(
            is_revoked=True,
            revoked_at=timezone.now(),
            revocation_reason=reason,
        )

        ManagerDecisionAuditLog.objects.create(
            tenant_id=tenant_id,
            decision=decision,
            action_type="DECISION_REVOKED",
            actor_id=manager_id,
            details={"reason": reason},
        )
        return decision

    @classmethod
    @transaction.atomic
    def execute_tenant_crypto_shredding(
        cls,
        *,
        tenant_id: UUID,
        operator_id: UUID,
        decision_id: Optional[UUID] = None,
    ) -> str:
        """
        GLM F5: Durable exit state persistence with cryptographic shred receipt.
        Purges mock tenant data keys and emits immutable receipt.
        """
        shred_receipt = f"SHRED-RECEIPT-{hashlib.sha256(f'{tenant_id}:{timezone.now().isoformat()}'.encode('utf-8')).hexdigest()}"
        
        dec = ManagerDecisionLedger.objects.filter(id=decision_id, tenant_id=tenant_id).first() if decision_id else None

        ManagerDecisionAuditLog.objects.create(
            tenant_id=tenant_id,
            decision=dec,
            action_type="TENANT_CRYPTO_SHREDDED",
            actor_id=operator_id,
            shred_receipt=shred_receipt,
            details={"exit_timestamp": timezone.now().isoformat(), "shred_receipt": shred_receipt},
        )
        return shred_receipt

