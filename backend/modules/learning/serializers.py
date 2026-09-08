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
