from rest_framework import serializers

from .models import (
    Assignment,
    AssignmentSubmissionMetrics,
    Course,
    CourseProgressAggregate,
    Feedback,
    LearningPath,
    Lesson,
    Module,
    Progress,
    RoleActivityFeed,
    Submission,
    SyntheticMediaAttachment,
    NotificationItem,
    BadgeDefinition,
    StudentBadgeAward,
    StudentProgressionProfile,
    Cohort,
    CourseEnrollment,
    CoursePrerequisite,
    CodeAssessment,
    CodeExecutionRun,
    AssessmentResult,
)


class LearningPathSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningPath
        fields = ["id", "code", "title", "state", "created_at"]
        read_only_fields = ["id", "created_at"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ["id", "learning_path", "code", "title", "state", "created_at"]
        read_only_fields = ["id", "created_at"]


class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            "id",
            "course",
            "code",
            "title",
            "position",
            "state",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "module",
            "code",
            "title",
            "position",
            "state",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ["id", "lesson", "code", "title", "description", "state", "created_at"]
        read_only_fields = ["id", "created_at"]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "student_id",
            "content",
            "state",
            "submitted_at",
            "created_at",
        ]
        read_only_fields = ["id", "state", "submitted_at", "created_at"]


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ["id", "submission", "mentor_id", "content", "created_at"]
        read_only_fields = ["id", "created_at"]


class ProgressSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    lesson_code = serializers.CharField(source="lesson.code", read_only=True)

    class Meta:
        model = Progress
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "lesson_code",
            "student_id",
            "state",
            "completed_at",
            "created_at",
        ]
        read_only_fields = ["id", "state", "completed_at", "created_at"]


class MentorSubmissionQueueSerializer(serializers.ModelSerializer):
    assignment_title = serializers.CharField(source="assignment.title", read_only=True)
    assignment_code = serializers.CharField(source="assignment.code", read_only=True)
    lesson_title = serializers.CharField(source="assignment.lesson.title", read_only=True)
    feedbacks = FeedbackSerializer(many=True, read_only=True)

    class Meta:
        model = Submission
        fields = [
            "id",
            "assignment",
            "assignment_title",
            "assignment_code",
            "lesson_title",
            "student_id",
            "content",
            "state",
            "submitted_at",
            "created_at",
            "feedbacks",
        ]
        read_only_fields = fields


class ParentStudentSummarySerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    learning_paths = LearningPathSerializer(many=True)
    courses = CourseSerializer(many=True)
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    completion_percentage = serializers.IntegerField()
    active_assignments = AssignmentSerializer(many=True)
    submissions = MentorSubmissionQueueSerializer(many=True)
    recent_feedbacks = FeedbackSerializer(many=True)


class SyntheticMediaAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SyntheticMediaAttachment
        fields = [
            "id",
            "lesson",
            "title",
            "storage_key",
            "mime_type",
            "file_size_bytes",
            "checksum_sha256",
            "state",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CourseProgressAggregateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseProgressAggregate
        fields = [
            "id",
            "course",
            "total_lessons",
            "completed_lessons",
            "progress_percentage",
            "updated_at",
        ]
        read_only_fields = fields


class AssignmentSubmissionMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentSubmissionMetrics
        fields = [
            "id",
            "assignment",
            "submitted_count",
            "under_review_count",
            "reviewed_count",
            "updated_at",
        ]
        read_only_fields = fields


class RoleActivityFeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleActivityFeed
        fields = [
            "id",
            "target_role",
            "activity_type",
            "summary",
            "occurred_at",
        ]
        read_only_fields = fields


class NotificationItemSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationItem.
    Zero-PII, returns authoritative metadata and delivery state.
    """

    class Meta:
        model = NotificationItem
        fields = [
            "id",
            "role",
            "title",
            "message",
            "notification_type",
            "state",
            "read_at",
            "delivered_at",
            "created_at",
        ]
        read_only_fields = fields


class BadgeDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BadgeDefinition
        fields = [
            "id",
            "badge_code",
            "badge_level",
            "title",
            "description",
            "threshold",
            "is_repeatable",
        ]
        read_only_fields = fields


class StudentBadgeAwardSerializer(serializers.ModelSerializer):
    title = serializers.CharField(source="badge.title", read_only=True)
    description = serializers.CharField(source="badge.description", read_only=True)

    class Meta:
        model = StudentBadgeAward
        fields = [
            "id",
            "badge_code",
            "badge_level",
            "title",
            "description",
            "awarded_at",
        ]
        read_only_fields = fields


class StudentProgressionProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProgressionProfile
        fields = [
            "id",
            "current_streak_days",
            "longest_streak_days",
            "last_qualifying_date",
            "total_xp",
            "level",
            "completed_lessons_count",
            "reviewed_submissions_count",
            "updated_at",
        ]
        read_only_fields = fields


class StudentGamificationResponseSerializer(serializers.Serializer):
    profile = StudentProgressionProfileSerializer()
    badges = StudentBadgeAwardSerializer(many=True)
    available_badges = BadgeDefinitionSerializer(many=True)


class CohortSerializer(serializers.ModelSerializer):
    current_enrollments_count = serializers.SerializerMethodField()

    class Meta:
        model = Cohort
        fields = [
            "id",
            "course",
            "code",
            "title",
            "max_capacity",
            "current_enrollments_count",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "current_enrollments_count", "created_at"]

    def get_current_enrollments_count(self, obj: Cohort) -> int:
        return obj.enrollments.filter(status__in=["enrolled", "active"]).count()


class CourseEnrollmentSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    course_code = serializers.CharField(source="course.code", read_only=True)
    cohort_title = serializers.CharField(source="cohort.title", read_only=True, allow_null=True)
    cohort_code = serializers.CharField(source="cohort.code", read_only=True, allow_null=True)

    class Meta:
        model = CourseEnrollment
        fields = [
            "id",
            "student_id",
            "course",
            "course_title",
            "course_code",
            "cohort",
            "cohort_title",
            "cohort_code",
            "status",
            "enrolled_at",
            "activated_at",
            "completed_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "course_title",
            "course_code",
            "cohort_title",
            "cohort_code",
            "enrolled_at",
            "activated_at",
            "completed_at",
        ]


class StudentEnrollRequestSerializer(serializers.Serializer):
    course_id = serializers.UUIDField(required=True)
    cohort_id = serializers.UUIDField(required=False, allow_null=True)
    idempotency_key = serializers.CharField(max_length=255, required=False, allow_null=True)


class CodeAssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeAssessment
        fields = [
            "id",
            "lesson",
            "language",
            "timeout_seconds",
            "memory_limit_mb",
            "starter_code",
            "testcases",
            "testcases_hash",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "testcases_hash", "created_at", "updated_at"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Filter hidden test cases from public student view
        request = self.context.get("request")
        if request and getattr(request.user, "is_staff", False):
            return ret
        if "testcases" in ret and isinstance(ret["testcases"], list):
            ret["testcases"] = [
                {
                    "id": tc.get("id"),
                    "input": tc.get("input"),
                    "expected_output": tc.get("expected_output") if not tc.get("is_hidden") else "[HIDDEN]",
                    "is_hidden": tc.get("is_hidden", False),
                    "weight": tc.get("weight", 1),
                }
                for tc in ret["testcases"]
            ]
        return ret


class CodeExecutionRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = CodeExecutionRun
        fields = [
            "id",
            "assessment",
            "student_id",
            "attempt_number",
            "submitted_code",
            "code_hash",
            "runtime_image_hash",
            "status",
            "duration_ms",
            "memory_used_kb",
            "stdout_log",
            "stderr_log",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "attempt_number",
            "code_hash",
            "runtime_image_hash",
            "status",
            "duration_ms",
            "memory_used_kb",
            "stdout_log",
            "stderr_log",
            "created_at",
            "updated_at",
        ]


class AssessmentResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssessmentResult
        fields = [
            "id",
            "execution_run",
            "assessment",
            "student_id",
            "passed_tests_count",
            "total_tests_count",
            "score",
            "is_passed",
            "is_final",
            "created_at",
        ]
        read_only_fields = ["id", "is_final", "created_at"]


class CodePlaygroundRunRequestSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_blank=False)
    language = serializers.CharField(default="python", required=False)


class CodeSubmitAssessmentRequestSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_blank=False)
    idempotency_key = serializers.CharField(max_length=128, required=False, allow_null=True)



from .models import (
    CertificateTemplate,
    CourseCertificate,
    CertificateVerificationRecord,
)


class CertificateTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateTemplate
        fields = [
            "id",
            "course",
            "version",
            "title",
            "description",
            "min_score_percentage",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CourseCertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    template_title = serializers.CharField(source="template.title", read_only=True)

    class Meta:
        model = CourseCertificate
        fields = [
            "id",
            "course",
            "course_title",
            "template",
            "template_title",
            "student_id",
            "completion_round",
            "certificate_number",
            "verification_hash",
            "status",
            "final_score",
            "completion_snapshot",
            "source_event_id",
            "issued_at",
            "revoked_at",
            "revocation_reason",
        ]
        read_only_fields = [
            "id",
            "certificate_number",
            "verification_hash",
            "status",
            "final_score",
            "completion_snapshot",
            "source_event_id",
            "issued_at",
            "revoked_at",
            "revocation_reason",
        ]


class CertificateVerificationRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateVerificationRecord
        fields = [
            "id",
            "certificate",
            "queried_number",
            "result_status",
            "queried_by_role",
            "queried_at",
        ]
        read_only_fields = ["id", "queried_at"]


class LearningAchievementTimelineItemSerializer(serializers.Serializer):
    id = serializers.CharField()
    event_type = serializers.CharField()
    title = serializers.CharField()
    description = serializers.CharField(allow_blank=True)
    occurred_at = serializers.DateTimeField()
    metadata = serializers.DictField(default=dict)


class DiscussionCommentSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import DiscussionComment
        model = DiscussionComment
        fields = [
            "id",
            "thread",
            "parent",
            "author_id",
            "body",
            "status",
            "is_mentor_endorsed",
            "endorsed_by_id",
            "endorsed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author_id",
            "status",
            "is_mentor_endorsed",
            "endorsed_by_id",
            "endorsed_at",
            "created_at",
            "updated_at",
        ]


class DiscussionThreadSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import DiscussionThread
        model = DiscussionThread
        fields = [
            "id",
            "cohort",
            "lesson",
            "author_id",
            "title",
            "body",
            "status",
            "is_pinned",
            "is_locked",
            "replies_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "author_id",
            "status",
            "is_pinned",
            "is_locked",
            "replies_count",
            "created_at",
            "updated_at",
        ]


class DiscussionModerationActionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import DiscussionModerationAction
        model = DiscussionModerationAction
        fields = [
            "id",
            "target_thread",
            "target_comment",
            "action",
            "previous_status",
            "new_status",
            "performed_by",
            "reason",
            "note",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "previous_status",
            "new_status",
            "performed_by",
            "created_at",
        ]


# =============================================================================
# Phase 3 VS11: Adaptive Progression and Personalization Serializers
# =============================================================================

class SkillDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import SkillDefinition
        model = SkillDefinition
        fields = [
            "id",
            "slug",
            "title",
            "description",
            "category",
            "difficulty_level",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentSkillProgressSerializer(serializers.ModelSerializer):
    skill = SkillDefinitionSerializer(read_only=True)

    class Meta:
        from .models import StudentSkillProgress
        model = StudentSkillProgress
        fields = [
            "id",
            "student_id",
            "skill",
            "mastery_level",
            "mastery_score",
            "practice_count",
            "last_evaluated_at",
        ]
        read_only_fields = ["id", "last_evaluated_at"]


class StudentLearningProfileSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import StudentLearningProfile
        model = StudentLearningProfile
        fields = [
            "id",
            "student_id",
            "total_skills_tracked",
            "mastered_skills_count",
            "developing_skills_count",
            "overall_competency_index",
            "identified_learning_gaps",
            "last_rebuilt_at",
            "rebuild_version",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "total_skills_tracked",
            "mastered_skills_count",
            "developing_skills_count",
            "overall_competency_index",
            "identified_learning_gaps",
            "last_rebuilt_at",
            "rebuild_version",
        ]


class LearningRecommendationSerializer(serializers.ModelSerializer):
    target_skill_slug = serializers.CharField(source="target_skill.slug", read_only=True, allow_null=True)
    target_skill_title = serializers.CharField(source="target_skill.title", read_only=True, allow_null=True)

    class Meta:
        from .models import LearningRecommendation
        model = LearningRecommendation
        fields = [
            "id",
            "student_id",
            "target_course",
            "target_lesson",
            "target_skill",
            "target_skill_slug",
            "target_skill_title",
            "recommendation_type",
            "status",
            "priority",
            "recommendation_reason",
            "evidence_context",
            "idempotency_key",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "idempotency_key",
            "created_at",
            "updated_at",
        ]


class RecommendationTransitionLogSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import RecommendationTransitionLog
        model = RecommendationTransitionLog
        fields = [
            "id",
            "recommendation",
            "from_status",
            "to_status",
            "actor_id",
            "actor_type",
            "transition_reason",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "recommendation",
            "from_status",
            "to_status",
            "actor_id",
            "actor_type",
            "transition_reason",
            "created_at",
        ]


class AchievementArtifactSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import AchievementArtifact
        model = AchievementArtifact
        fields = [
            "id",
            "portfolio",
            "artifact_type",
            "title",
            "reflection_notes",
            "mentor_endorsement",
            "mentor_user_id",
            "source_submission",
            "source_certificate",
            "moderation_status",
            "is_featured",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "mentor_endorsement",
            "mentor_user_id",
            "moderation_status",
            "created_at",
            "updated_at",
        ]


class LearningPortfolioSerializer(serializers.ModelSerializer):
    artifacts = AchievementArtifactSerializer(many=True, read_only=True)

    class Meta:
        from .models import LearningPortfolio
        model = LearningPortfolio
        fields = [
            "id",
            "student_id",
            "headline",
            "summary_narrative",
            "featured_artifact_count",
            "visibility",
            "moderation_status",
            "public_consent_active",
            "public_consent_at",
            "artifacts",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "featured_artifact_count",
            "moderation_status",
            "public_consent_active",
            "public_consent_at",
            "created_at",
            "updated_at",
        ]


class StudentJourneyTimelineSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import StudentJourneyTimeline
        model = StudentJourneyTimeline
        fields = [
            "id",
            "student_id",
            "event_key",
            "event_title",
            "narrative_description",
            "milestone_date",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "student_id", "created_at", "updated_at"]


class GuardianAccessGrantSerializer(serializers.ModelSerializer):
    class Meta:
        from modules.platform_tenant.models import GuardianAccessGrant
        model = GuardianAccessGrant
        fields = [
            "id",
            "guardian_user_id",
            "student_id",
            "status",
            "decided_at",
            "revoked_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "status", "decided_at", "revoked_at", "created_at", "updated_at"]


class GrowthMetricSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import GrowthMetricSnapshot
        model = GrowthMetricSnapshot
        fields = [
            "id",
            "student_id",
            "metric_key",
            "metric_value",
            "baseline_value",
            "growth_delta",
            "snapshot_date",
            "metadata",
            "recorded_at",
        ]
        read_only_fields = fields


class StudentGrowthTrendSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import StudentGrowthTrend
        model = StudentGrowthTrend
        fields = [
            "id",
            "student_id",
            "competency_domain",
            "trend_direction",
            "current_score",
            "velocity_rate",
            "total_milestones_achieved",
            "competency_vectors",
            "updated_at",
        ]
        read_only_fields = fields


class LearningMilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import LearningMilestone
        model = LearningMilestone
        fields = [
            "id",
            "student_id",
            "milestone_code",
            "title",
            "description",
            "status",
            "achieved_at",
            "retracted_at",
            "retraction_reason",
            "evidence_digest",
            "evidence_payload",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "achieved_at",
            "retracted_at",
            "evidence_digest",
            "created_at",
        ]


class LearningInsightSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import LearningInsight
        model = LearningInsight
        fields = [
            "id",
            "student_id",
            "insight_type",
            "title",
            "description",
            "confidence_level",
            "lifecycle_status",
            "valid_until",
            "retracted_at",
            "retraction_reason",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "lifecycle_status",
            "valid_until",
            "retracted_at",
            "retraction_reason",
            "created_at",
            "updated_at",
        ]


# ============================================================================
# P3-VS14: STUDENT LEARNING OPERATIONS & AI-ASSISTED REFLECTION SERIALIZERS
# ============================================================================

class LearningReflectionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import LearningReflection
        model = LearningReflection
        fields = [
            "id",
            "student_id",
            "prompt_type",
            "content",
            "mood_sentiment",
            "is_retracted",
            "retracted_at",
            "retraction_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "is_retracted",
            "retracted_at",
            "retraction_reason",
            "created_at",
            "updated_at",
        ]


class GoalActionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import GoalActionPlan
        model = GoalActionPlan
        fields = [
            "id",
            "goal",
            "step_order",
            "description",
            "status",
            "due_date",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class StudentLearningGoalSerializer(serializers.ModelSerializer):
    action_steps = GoalActionPlanSerializer(many=True, read_only=True)

    class Meta:
        from .models import StudentLearningGoal
        model = StudentLearningGoal
        fields = [
            "id",
            "student_id",
            "title",
            "domain",
            "target_milestone",
            "status",
            "target_date",
            "completed_at",
            "action_steps",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "status",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class AIAssistedGrowthSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import AIAssistedGrowthSuggestion
        model = AIAssistedGrowthSuggestion
        fields = [
            "id",
            "student_id",
            "source_insight",
            "generation_run",
            "suggestion_type",
            "recommended_action",
            "rationale",
            "evidence_context",
            "model_identifier",
            "provenance_digest",
            "idempotency_key",
            "status",
            "is_authoritative",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "source_insight",
            "generation_run",
            "model_identifier",
            "provenance_digest",
            "idempotency_key",
            "status",
            "is_authoritative",
            "created_at",
            "updated_at",
        ]


class MentorReflectionFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import MentorReflectionFeedback
        model = MentorReflectionFeedback
        fields = [
            "id",
            "reflection",
            "mentor_id",
            "feedback_text",
            "is_retracted",
            "retracted_at",
            "retraction_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "mentor_id",
            "is_retracted",
            "retracted_at",
            "retraction_reason",
            "created_at",
            "updated_at",
        ]


class ReflectionAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ReflectionAuditLog
        model = ReflectionAuditLog
        fields = [
            "id",
            "actor_id",
            "target_reflection",
            "target_goal",
            "target_feedback",
            "target_suggestion",
            "action",
            "metadata",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "actor_id",
            "target_reflection",
            "target_goal",
            "target_feedback",
            "target_suggestion",
            "action",
            "metadata",
            "created_at",
        ]


# ============================================================================
# P3-VS15: LEARNING CONTINUITY & STUDENT SUCCESS PLANNING SERIALIZERS
# ============================================================================

class SuccessActionStepSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import SuccessActionStep
        model = SuccessActionStep
        fields = [
            "id",
            "plan",
            "title",
            "description",
            "status",
            "sequence_order",
            "is_authoritative",
            "target_date",
            "completed_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "is_authoritative",
            "completed_at",
            "created_at",
            "updated_at",
        ]


class SuccessTimelineEventSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import SuccessTimelineEvent
        model = SuccessTimelineEvent
        fields = [
            "id",
            "plan",
            "actor_id",
            "event_type",
            "headline",
            "detail",
            "target_goal",
            "target_insight",
            "target_reflection",
            "target_action_step",
            "target_milestone",
            "client_mutation_id",
            "replaces_event",
            "metadata",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "actor_id",
            "created_at",
        ]


class LearningStudentSuccessPlanSerializer(serializers.ModelSerializer):
    action_steps = SuccessActionStepSerializer(many=True, read_only=True)
    timeline_events = SuccessTimelineEventSerializer(many=True, read_only=True)

    class Meta:
        from .models import LearningStudentSuccessPlan
        model = LearningStudentSuccessPlan
        fields = [
            "id",
            "student_id",
            "title",
            "target_period",
            "status",
            "notes",
            "completed_at",
            "paused_at",
            "superseded_at",
            "archived_at",
            "action_steps",
            "timeline_events",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "status",
            "completed_at",
            "paused_at",
            "superseded_at",
            "archived_at",
            "created_at",
            "updated_at",
        ]


class SuccessAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import SuccessAuditLog
        model = SuccessAuditLog
        fields = [
            "id",
            "actor_id",
            "target_plan",
            "target_action_step",
            "target_timeline_event",
            "action",
            "metadata",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "actor_id",
            "target_plan",
            "target_action_step",
            "target_timeline_event",
            "action",
            "metadata",
            "created_at",
        ]


# ============================================================================
# P3-VS16: Coaching Sessions, Notes, Interventions, and Actions Serializers
# ============================================================================

class CoachingNoteSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import CoachingNote
        model = CoachingNote
        fields = [
            "id",
            "session",
            "author_id",
            "note_type",
            "content",
            "is_shared_with_student",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "author_id",
            "created_at",
        ]


class FollowUpActionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import FollowUpAction
        model = FollowUpAction
        fields = [
            "id",
            "intervention",
            "session",
            "student_id",
            "assigned_by_id",
            "title",
            "status",
            "due_date",
            "completed_at",
            "skipped_at",
            "skip_reason",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "assigned_by_id",
            "status",
            "completed_at",
            "skipped_at",
            "created_at",
            "updated_at",
        ]


class SupportInterventionSerializer(serializers.ModelSerializer):
    followup_actions = FollowUpActionSerializer(many=True, read_only=True)

    class Meta:
        from .models import SupportIntervention
        model = SupportIntervention
        fields = [
            "id",
            "student_id",
            "mentor_id",
            "success_plan",
            "title",
            "category",
            "status",
            "is_authoritative",
            "rationale",
            "student_feedback",
            "proposed_at",
            "acknowledged_at",
            "declined_at",
            "started_at",
            "completed_at",
            "paused_at",
            "metadata",
            "followup_actions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "mentor_id",
            "status",
            "is_authoritative",
            "proposed_at",
            "acknowledged_at",
            "declined_at",
            "started_at",
            "completed_at",
            "paused_at",
            "created_at",
            "updated_at",
        ]


class CoachingSessionSerializer(serializers.ModelSerializer):
    notes = CoachingNoteSerializer(many=True, read_only=True)
    followup_actions = FollowUpActionSerializer(many=True, read_only=True)

    class Meta:
        from .models import CoachingSession
        model = CoachingSession
        fields = [
            "id",
            "student_id",
            "mentor_id",
            "success_plan",
            "learning_insight",
            "title",
            "status",
            "scheduled_at",
            "started_at",
            "completed_at",
            "cancelled_at",
            "cancellation_reason",
            "summary",
            "metadata",
            "notes",
            "followup_actions",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "student_id",
            "mentor_id",
            "status",
            "started_at",
            "completed_at",
            "cancelled_at",
            "created_at",
            "updated_at",
        ]


class CoachingAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import CoachingAuditLog
        model = CoachingAuditLog
        fields = [
            "id",
            "action_type",
            "actor_id",
            "target_session",
            "target_note",
            "target_intervention",
            "target_action",
            "details",
            "created_at",
        ]
        read_only_fields = fields



