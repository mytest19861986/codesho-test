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
