from rest_framework import serializers
from .models import (
    LearnerProfile,
    ActiveLearningProject,
    MentorIntervention,
    InterventionFeedback,
    ParentBridge,
)


class FeedbackItemSerializer(serializers.ModelSerializer):
    timestamp = serializers.DateTimeField(source="created_at", format="%Y-%m-%d %H:%M")
    text = serializers.CharField(source="feedback_text")
    sender = serializers.CharField(source="sender_role")

    class Meta:
        model = InterventionFeedback
        fields = ["id", "sender", "timestamp", "text", "action_type"]


class MentorInterventionSerializer(serializers.ModelSerializer):
    feedbacks = FeedbackItemSerializer(many=True, read_only=True)

    class Meta:
        model = MentorIntervention
        fields = [
            "id",
            "status",
            "reason",
            "recommended_action",
            "mentor_notes",
            "feedbacks",
        ]


class ActiveProjectSerializer(serializers.ModelSerializer):
    branch = serializers.CharField(source="repo_branch")

    class Meta:
        model = ActiveLearningProject
        fields = [
            "id",
            "title",
            "branch",
            "commit_hash",
            "progress_percentage",
            "current_milestone",
            "recent_activity",
            "last_code_snippet",
            "skills_demonstrated",
        ]


class ParentBridgeSerializer(serializers.ModelSerializer):
    briefing_timestamp = serializers.DateTimeField(
        source="briefing_updated_at", format="%Y-%m-%d %H:%M"
    )

    class Meta:
        model = ParentBridge
        fields = [
            "last_briefing",
            "briefing_timestamp",
            "parent_encouragement_sent",
            "parent_encouragement_message",
        ]


class LearnerStudentSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="display_name")
    avatar = serializers.CharField(source="avatar_key")
    level = serializers.CharField(source="level_title")
    id = serializers.CharField(source="student_code")

    class Meta:
        model = LearnerProfile
        fields = ["id", "name", "avatar", "level", "streak_days"]


class SharedLearningStateAggregateSerializer(serializers.Serializer):
    """
    Serializes the complete cross-role domain state matching SharedLearningState
    1:1 with frontend client interface.
    """
    student = LearnerStudentSerializer()
    activeProject = ActiveProjectSerializer(source="active_project")
    mentorIntervention = MentorInterventionSerializer(source="mentor_intervention")
    parentBridge = ParentBridgeSerializer(source="parent_bridge")


# Input Serializers
class UpdateInterventionStatusInputSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=MentorIntervention.Status.choices)


class AddFeedbackInputSerializer(serializers.Serializer):
    text = serializers.CharField(min_length=2, max_length=2000)
    action_type = serializers.CharField(max_length=64)


class SaveParentBriefingInputSerializer(serializers.Serializer):
    last_briefing = serializers.CharField(min_length=5, max_length=3000)


class SendParentEncouragementInputSerializer(serializers.Serializer):
    message = serializers.CharField(min_length=2, max_length=1000)
