# =============================================================================
# P3-MACRO-EPIC-26-28: ENTERPRISE GOVERNANCE, DATA LIFECYCLE & PILOT READINESS
# Sub-Slices: P3-VS26, P3-VS27, P3-VS28
# Canonical DDL: v1.2-HARDENED
# Models (20):
#   VS26: StaffAccessAssignment, DelegatedAdminScope, PrivilegedPermissionGrant,
#         AccessReviewCampaign, AccessReviewDecision, PrivilegedActionAudit
#   VS27: DataRetentionPolicy, RetentionPolicyVersion, LegalHold,
#         LegalHoldScope, RetentionEvaluation, DataDispositionRecord,
#         DispositionAuditLog
#   VS28: ReadinessControl, ReadinessEvidence, ReadinessAssessmentRun,
#         ReadinessFinding, ReadinessException, PilotReadinessGate,
#         ControlAttestationAudit
# =============================================================================

class StaffRole(models.TextChoices):
    TENANT_ADMIN = "TENANT_ADMIN", "Tenant Admin"
    DELEGATED_STAFF = "DELEGATED_STAFF", "Delegated Staff"
    COMPLIANCE_OFFICER = "COMPLIANCE_OFFICER", "Compliance Officer"
    AUDITOR = "AUDITOR", "Auditor"
    PROGRAM_OPERATOR = "PROGRAM_OPERATOR", "Program Operator"


class ScopeResourceType(models.TextChoices):
    BRANCH = "BRANCH", "Branch"
    PROGRAM = "PROGRAM", "Program"
    DEPARTMENT = "DEPARTMENT", "Department"
    COHORT = "COHORT", "Cohort"


class PrivilegedGrantStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    EXPIRED = "EXPIRED", "Expired"
    REVOKED = "REVOKED", "Revoked"


class AccessReviewCampaignStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    CONCLUDED = "CONCLUDED", "Concluded"
    CANCELLED = "CANCELLED", "Cancelled"


class AccessReviewDecisionChoice(models.TextChoices):
    MAINTAIN = "MAINTAIN", "Maintain"
    REVOKE = "REVOKE", "Revoke"
    RESTRICT = "RESTRICT", "Restrict"


class DispositionAction(models.TextChoices):
    ANONYMIZE = "ANONYMIZE", "Anonymize"
    PURGE = "PURGE", "Purge"
    ARCHIVE = "ARCHIVE", "Archive"


class LegalHoldStatus(models.TextChoices):
    ACTIVE = "ACTIVE", "Active"
    RELEASED = "RELEASED", "Released"


class ReadinessControlCategory(models.TextChoices):
    SECURITY = "SECURITY", "Security"
    DATA_GOVERNANCE = "DATA_GOVERNANCE", "Data Governance"
    TESTING = "TESTING", "Testing"
    RLS = "RLS", "RLS"
    FLEET = "FLEET", "Fleet"


class ReadinessEvidenceStatus(models.TextChoices):
    VALID = "VALID", "Valid"
    SUPERSEDED = "SUPERSEDED", "Superseded"
    REVOKED = "REVOKED", "Revoked"


class ReadinessOverallStatus(models.TextChoices):
    IN_PROGRESS = "IN_PROGRESS", "In Progress"
    READY = "READY", "Ready"
    NOT_READY = "NOT_READY", "Not Ready"
    BLOCKED = "BLOCKED", "Blocked"
    EXCEPTION_REQUIRED = "EXCEPTION_REQUIRED", "Exception Required"


class ReadinessFindingSeverity(models.TextChoices):
    BLOCKER = "BLOCKER", "Blocker"
    CRITICAL = "CRITICAL", "Critical"
    MAJOR = "MAJOR", "Major"
    MINOR = "MINOR", "Minor"


class PilotGateVerdict(models.TextChoices):
    READY = "READY", "Ready"
    NOT_READY = "NOT_READY", "Not Ready"
    BLOCKED = "BLOCKED", "Blocked"
    EXCEPTION_REQUIRED = "EXCEPTION_REQUIRED", "Exception Required"


# -----------------------------------------------------------------------------
# 1. P3-VS26: DELEGATED ADMINISTRATION & ACCESS GOVERNANCE
# -----------------------------------------------------------------------------

class StaffAccessAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="staff_access_assignments",
    )
    user_id = models.UUIDField()
    role_name = models.CharField(max_length=64, choices=StaffRole.choices)
    scope_type = models.CharField(max_length=32, default="TENANT_WIDE")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_until = models.DateTimeField(null=True, blank=True)
    assigned_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_staff_access_assignment"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_staff_access_assignment_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "user_id", "role_name"],
                name="uq_staff_assignment",
            ),
            models.CheckConstraint(
                condition=Q(role_name__in=StaffRole.values),
                name="chk_staff_role_valid",
            ),
            models.CheckConstraint(
                condition=Q(valid_until__isnull=True) | Q(valid_until__gt=models.F("valid_from")),
                name="chk_staff_validity_window",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "user_id", "is_active"], name="idx_staff_assign_t_u_act"),
        ]

    def clean(self):
        super().clean()
        if self.valid_until and self.valid_from and self.valid_until <= self.valid_from:
            raise ValidationError("valid_until must be strictly greater than valid_from.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.user_id}:{self.role_name}"


class DelegatedAdminScope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="delegated_admin_scopes",
    )
    assignment = models.ForeignKey(
        StaffAccessAssignment,
        on_delete=models.CASCADE,
        related_name="scopes",
    )
    scope_resource_type = models.CharField(max_length=64, choices=ScopeResourceType.choices)
    scope_resource_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_delegated_admin_scope"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_delegated_admin_scope_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(scope_resource_type__in=ScopeResourceType.values),
                name="chk_scope_resource_type",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "assignment"], name="idx_del_admin_scope_t_assign"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "assignment") and self.assignment is not None:
            if str(self.assignment.tenant_id) != str(self.tenant_id):
                raise ValidationError("StaffAccessAssignment tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.assignment_id}:{self.scope_resource_type}:{self.scope_resource_id}"


class PrivilegedPermissionGrant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="privileged_permission_grants",
    )
    user_id = models.UUIDField()
    permission_code = models.CharField(max_length=64)
    justification = models.TextField()
    granted_by_id = models.UUIDField()
    second_approver_id = models.UUIDField(null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=PrivilegedGrantStatus.choices,
        default=PrivilegedGrantStatus.ACTIVE,
    )
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_privileged_permission_grant"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_privileged_permission_grant_tenant_id",
            ),
            models.CheckConstraint(
                condition=~Q(user_id=models.F("granted_by_id")),
                name="chk_privilege_no_self_grant",
            ),
            models.CheckConstraint(
                condition=Q(second_approver_id__isnull=True) | ~Q(second_approver_id=models.F("granted_by_id")),
                name="chk_privilege_distinct_second_approver",
            ),
            models.CheckConstraint(
                condition=Q(status__in=PrivilegedGrantStatus.values),
                name="chk_privilege_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "user_id", "status"], name="idx_priv_grant_t_u_stat"),
        ]

    def clean(self):
        super().clean()
        if str(self.user_id) == str(self.granted_by_id):
            raise ValidationError("Self-granting of privileges is strictly prohibited.")
        if self.second_approver_id and str(self.second_approver_id) == str(self.granted_by_id):
            raise ValidationError("Second approver must be distinct from grantor.")
        _validate_pii_text_field(self.justification, "justification", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.user_id}:{self.permission_code}:{self.status}"


class AccessReviewCampaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="access_review_campaigns",
    )
    title = models.CharField(max_length=255)
    campaign_period = models.CharField(max_length=32)
    status = models.CharField(
        max_length=32,
        choices=AccessReviewCampaignStatus.choices,
        default=AccessReviewCampaignStatus.ACTIVE,
    )
    deadline = models.DateTimeField()
    created_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_access_review_campaign"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_access_review_campaign_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=AccessReviewCampaignStatus.values),
                name="chk_campaign_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_acc_camp_t_stat"),
        ]

    def clean(self):
        super().clean()
        _validate_pii_text_field(self.title, "title", 255)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.title}:{self.status}"


class AccessReviewDecision(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="access_review_decisions",
    )
    campaign = models.ForeignKey(
        AccessReviewCampaign,
        on_delete=models.CASCADE,
        related_name="decisions",
    )
    assignment = models.ForeignKey(
        StaffAccessAssignment,
        on_delete=models.CASCADE,
        related_name="review_decisions",
    )
    reviewer_id = models.UUIDField()
    decision = models.CharField(
        max_length=32,
        choices=AccessReviewDecisionChoice.choices,
    )
    notes = models.TextField(default="", blank=True)
    decided_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_access_review_decision"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_access_review_decision_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "campaign", "assignment"],
                name="uq_review_decision_per_assignment",
            ),
            models.CheckConstraint(
                condition=Q(decision__in=AccessReviewDecisionChoice.values),
                name="chk_review_decision",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "campaign", "reviewer_id"], name="idx_rev_dec_t_camp_rev"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "campaign") and self.campaign is not None:
            if str(self.campaign.tenant_id) != str(self.tenant_id):
                raise ValidationError("AccessReviewCampaign tenant mismatch.")
        if hasattr(self, "assignment") and self.assignment is not None:
            if str(self.assignment.tenant_id) != str(self.tenant_id):
                raise ValidationError("StaffAccessAssignment tenant mismatch.")
        _validate_pii_text_field(self.notes, "notes", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.campaign_id}:{self.assignment_id}:{self.decision}"


class PrivilegedActionAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="privileged_action_audits",
    )
    actor_id = models.UUIDField()
    action_type = models.CharField(max_length=64)
    target_resource = models.CharField(max_length=128)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    details = models.JSONBField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_privileged_action_audit"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_privileged_action_audit_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_priv_audit_t_act_cr"),
        ]

    def clean(self):
        super().clean()
        _validate_pii_jsonb_field(self.details, "details")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.actor_id}:{self.action_type}"


# -----------------------------------------------------------------------------
# 2. P3-VS27: DATA LIFECYCLE, RETENTION & DISPOSITION GOVERNANCE
# -----------------------------------------------------------------------------

class DataRetentionPolicy(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="data_retention_policies",
    )
    data_category = models.CharField(max_length=64)
    retention_period_days = models.IntegerField()
    disposition_action = models.CharField(
        max_length=32,
        choices=DispositionAction.choices,
        default=DispositionAction.ANONYMIZE,
    )
    is_active = models.BooleanField(default=True)
    created_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_data_retention_policy"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_data_retention_policy_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "data_category"],
                name="uq_retention_category",
            ),
            models.CheckConstraint(
                condition=Q(retention_period_days__gte=30),
                name="chk_retention_period_positive",
            ),
            models.CheckConstraint(
                condition=Q(disposition_action__in=DispositionAction.values),
                name="chk_disposition_action",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "is_active"], name="idx_ret_pol_t_act"),
        ]

    def clean(self):
        super().clean()
        if self.retention_period_days < 30:
            raise ValidationError("retention_period_days must be at least 30 days.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.data_category}:{self.retention_period_days}d"


class RetentionPolicyVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="retention_policy_versions",
    )
    policy = models.ForeignKey(
        DataRetentionPolicy,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version_number = models.IntegerField()
    retention_period_days = models.IntegerField()
    disposition_action = models.CharField(max_length=32, choices=DispositionAction.choices)
    effective_from = models.DateTimeField(auto_now_add=True)
    created_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_retention_policy_version"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_retention_policy_version_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "policy", "version_number"],
                name="uq_policy_version",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "policy", "-version_number"], name="idx_ret_ver_t_pol_v"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "policy") and self.policy is not None:
            if str(self.policy.tenant_id) != str(self.tenant_id):
                raise ValidationError("DataRetentionPolicy tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.policy_id}:v{self.version_number}"


class LegalHold(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="legal_holds",
    )
    title = models.CharField(max_length=255)
    legal_case_reference = models.CharField(max_length=128)
    reason = models.TextField()
    status = models.CharField(
        max_length=32,
        choices=LegalHoldStatus.choices,
        default=LegalHoldStatus.ACTIVE,
    )
    placed_by_id = models.UUIDField()
    placed_at = models.DateTimeField(auto_now_add=True)
    released_by_id = models.UUIDField(null=True, blank=True)
    released_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_legal_hold"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_legal_hold_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=LegalHoldStatus.values),
                name="chk_hold_status",
            ),
            models.CheckConstraint(
                condition=(
                    (Q(status="RELEASED") & Q(released_at__isnull=False) & Q(released_by_id__isnull=False)) |
                    (Q(status="ACTIVE") & Q(released_at__isnull=True) & Q(released_by_id__isnull=True))
                ),
                name="chk_hold_release_consistency",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_legal_hold_t_stat"),
        ]

    def clean(self):
        super().clean()
        if self.status == LegalHoldStatus.RELEASED and (not self.released_at or not self.released_by_id):
            raise ValidationError("Released LegalHold must have released_at and released_by_id set.")
        if self.status == LegalHoldStatus.ACTIVE and (self.released_at or self.released_by_id):
            raise ValidationError("Active LegalHold must not have released_at or released_by_id set.")
        _validate_pii_text_field(self.reason, "reason", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.legal_case_reference}:{self.status}"


class LegalHoldScope(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="legal_hold_scopes",
    )
    legal_hold = models.ForeignKey(
        LegalHold,
        on_delete=models.CASCADE,
        related_name="scopes",
    )
    target_entity_type = models.CharField(max_length=64)
    target_entity_id = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_legal_hold_scope"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_legal_hold_scope_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "legal_hold"], name="idx_legal_scope_t_hold"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "legal_hold") and self.legal_hold is not None:
            if str(self.legal_hold.tenant_id) != str(self.tenant_id):
                raise ValidationError("LegalHold tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.legal_hold_id}:{self.target_entity_type}:{self.target_entity_id}"


class RetentionEvaluation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="retention_evaluations",
    )
    policy = models.ForeignKey(
        DataRetentionPolicy,
        on_delete=models.RESTRICT,
        related_name="evaluations",
    )
    evaluated_entity_type = models.CharField(max_length=64)
    candidates_count = models.IntegerField(default=0)
    exempted_by_legal_hold_count = models.IntegerField(default=0)
    disposition_ready_count = models.IntegerField(default=0)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_retention_evaluation"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_retention_evaluation_tenant_id",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "policy") and self.policy is not None:
            if str(self.policy.tenant_id) != str(self.tenant_id):
                raise ValidationError("DataRetentionPolicy tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.evaluated_entity_type}:{self.disposition_ready_count} ready"


class DataDispositionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="data_disposition_records",
    )
    evaluation = models.ForeignKey(
        RetentionEvaluation,
        on_delete=models.RESTRICT,
        related_name="disposition_records",
    )
    action_applied = models.CharField(max_length=32, choices=DispositionAction.choices)
    status = models.CharField(max_length=32, default="EXECUTED")
    records_processed = models.IntegerField(default=0)
    cryptographic_digest = models.CharField(max_length=128)
    executed_by_id = models.UUIDField()
    executed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_data_disposition_record"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_data_disposition_record_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_disp_rec_t_stat"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "evaluation") and self.evaluation is not None:
            if str(self.evaluation.tenant_id) != str(self.tenant_id):
                raise ValidationError("RetentionEvaluation tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.action_applied}:{self.records_processed}"


class DispositionAuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="disposition_audit_logs",
    )
    disposition_record = models.ForeignKey(
        DataDispositionRecord,
        on_delete=models.RESTRICT,
        related_name="audit_logs",
    )
    actor_id = models.UUIDField(null=True, blank=True)
    entity_type = models.CharField(max_length=64)
    entity_key_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=32, default="SUCCESS")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_disposition_audit_log"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_disposition_audit_log_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "actor_id", "-created_at"], name="idx_disp_audit_t_act_cr"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "disposition_record") and self.disposition_record is not None:
            if str(self.disposition_record.tenant_id) != str(self.tenant_id):
                raise ValidationError("DataDispositionRecord tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.entity_type}:{self.entity_key_hash}"


# -----------------------------------------------------------------------------
# 3. P3-VS28: ENTERPRISE CONTROL EVIDENCE & PILOT READINESS CENTER
# -----------------------------------------------------------------------------

class ReadinessControl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_controls",
    )
    control_code = models.CharField(max_length=64)
    category = models.CharField(max_length=64, choices=ReadinessControlCategory.choices)
    description = models.TextField()
    is_mandatory = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "learning_readiness_control"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_control_tenant_id",
            ),
            models.UniqueConstraint(
                fields=["tenant", "control_code"],
                name="uq_readiness_control_code",
            ),
            models.CheckConstraint(
                condition=Q(category__in=ReadinessControlCategory.values),
                name="chk_control_category",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "category"], name="idx_read_ctrl_t_cat"),
        ]

    def clean(self):
        super().clean()
        _validate_pii_text_field(self.description, "description", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.control_code}:{self.category}"


class ReadinessEvidence(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_evidences",
    )
    control = models.ForeignKey(
        ReadinessControl,
        on_delete=models.RESTRICT,
        related_name="evidences",
    )
    evidence_type = models.CharField(max_length=64)
    artifact_reference = models.CharField(max_length=255)
    verification_hash = models.CharField(max_length=128)
    status = models.CharField(
        max_length=32,
        choices=ReadinessEvidenceStatus.choices,
        default=ReadinessEvidenceStatus.VALID,
    )
    recorded_by_id = models.UUIDField()
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_evidence"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_evidence_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(status__in=ReadinessEvidenceStatus.values),
                name="chk_evidence_status",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "control") and self.control is not None:
            if str(self.control.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessControl tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.control_id}:{self.evidence_type}:{self.status}"


class ReadinessAssessmentRun(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_assessment_runs",
    )
    run_reference = models.CharField(max_length=64)
    total_controls = models.IntegerField(default=0)
    passed_controls = models.IntegerField(default=0)
    failed_controls = models.IntegerField(default=0)
    overall_status = models.CharField(
        max_length=32,
        choices=ReadinessOverallStatus.choices,
        default=ReadinessOverallStatus.IN_PROGRESS,
    )
    status = models.CharField(max_length=32, default="IN_PROGRESS")
    executed_by_id = models.UUIDField()
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_assessment_run"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_assessment_run_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(overall_status__in=ReadinessOverallStatus.values),
                name="chk_run_status",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_read_run_t_stat"),
        ]

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.run_reference}:{self.overall_status}"


class ReadinessFinding(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_findings",
    )
    assessment_run = models.ForeignKey(
        ReadinessAssessmentRun,
        on_delete=models.CASCADE,
        related_name="findings",
    )
    control = models.ForeignKey(
        ReadinessControl,
        on_delete=models.RESTRICT,
        related_name="findings",
    )
    severity = models.CharField(
        max_length=32,
        choices=ReadinessFindingSeverity.choices,
        default=ReadinessFindingSeverity.MAJOR,
    )
    finding_summary = models.TextField()
    status = models.CharField(max_length=32, default="OPEN")
    is_resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_finding"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_finding_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(severity__in=ReadinessFindingSeverity.values),
                name="chk_finding_severity",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "severity", "status"], name="idx_read_find_t_sev_stat"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "assessment_run") and self.assessment_run is not None:
            if str(self.assessment_run.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessAssessmentRun tenant mismatch.")
        if hasattr(self, "control") and self.control is not None:
            if str(self.control.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessControl tenant mismatch.")
        _validate_pii_text_field(self.finding_summary, "finding_summary", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.control_id}:{self.severity}:resolved={self.is_resolved}"


class ReadinessException(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="readiness_exceptions",
    )
    finding = models.ForeignKey(
        ReadinessFinding,
        on_delete=models.RESTRICT,
        related_name="exceptions",
    )
    reason = models.TextField()
    expiry_date = models.DateTimeField()
    approved_by_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_readiness_exception"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_readiness_exception_tenant_id",
            ),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "finding") and self.finding is not None:
            if str(self.finding.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessFinding tenant mismatch.")
        _validate_pii_text_field(self.reason, "reason", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.finding_id}:{self.approved_by_id}"


class PilotReadinessGate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="pilot_readiness_gates",
    )
    assessment_run = models.ForeignKey(
        ReadinessAssessmentRun,
        on_delete=models.RESTRICT,
        related_name="pilot_gates",
    )
    gate_verdict = models.CharField(
        max_length=32,
        choices=PilotGateVerdict.choices,
    )
    status = models.CharField(max_length=32, default="EVALUATED")
    human_attestation_summary = models.TextField()
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_pilot_readiness_gate"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_pilot_readiness_gate_tenant_id",
            ),
            models.CheckConstraint(
                condition=Q(gate_verdict__in=PilotGateVerdict.values),
                name="chk_gate_verdict",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "status"], name="idx_pilot_gate_t_stat"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "assessment_run") and self.assessment_run is not None:
            if str(self.assessment_run.tenant_id) != str(self.tenant_id):
                raise ValidationError("ReadinessAssessmentRun tenant mismatch.")
        _validate_pii_text_field(self.human_attestation_summary, "human_attestation_summary", 2000)

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.assessment_run_id}:{self.gate_verdict}"


class ControlAttestationAudit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(
        "platform_tenant.Tenant",
        on_delete=models.CASCADE,
        related_name="control_attestation_audits",
    )
    gate = models.ForeignKey(
        PilotReadinessGate,
        on_delete=models.RESTRICT,
        related_name="attestations",
    )
    attested_by_id = models.UUIDField()
    attestation_role = models.CharField(max_length=64)
    signature_digest = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "learning_control_attestation_audit"
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "id"],
                name="uq_learning_control_attestation_audit_tenant_id",
            ),
        ]
        indexes = [
            models.Index(fields=["tenant", "gate", "-created_at"], name="idx_ctrl_attest_t_g_cr"),
        ]

    def clean(self):
        super().clean()
        if hasattr(self, "gate") and self.gate is not None:
            if str(self.gate.tenant_id) != str(self.tenant_id):
                raise ValidationError("PilotReadinessGate tenant mismatch.")

    def __str__(self) -> str:
        return f"{self.tenant_id}:{self.gate_id}:{self.attestation_role}:{self.attested_by_id}"
