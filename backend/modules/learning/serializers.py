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

