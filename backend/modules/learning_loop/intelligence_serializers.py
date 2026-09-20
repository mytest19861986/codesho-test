"""
Wave 5.7 Phase 3: Intelligence Read Contract, DTO Projections & Serializers.

Provides standardized, read-only DTO projections for:
1. Skill Graph Progression (Non-competitive DAG)
2. Mentor Intelligence Dossier (Evidence-backed Socratic Prompts)
3. Parent Empathetic Growth Insight (Jargon-free Developmental Guidance)
4. Student Reflection Timeline (Learner-owned self-reflections)

Strict Invariants:
- NO_SKILL_SCORE: No rankings, no grades, no comparisons.
- ZERO_DATABASE_MIGRATIONS: Pure read projections over existing aggregates.
- FAIL_CLOSED_TENANT_ISOLATION: Scoped strictly to authenticated tenant.
"""
from rest_framework import serializers


class SkillNodeSerializer(serializers.Serializer):
    slug = serializers.CharField()
    title = serializers.CharField()
    category = serializers.CharField()
    status = serializers.ChoiceField(choices=["DEMONSTRATED", "IN_PROGRESS"])
    prerequisites = serializers.ListField(child=serializers.CharField())


class LearnerSkillGraphReadModelSerializer(serializers.Serializer):
    learner_id = serializers.CharField()
    student_code = serializers.CharField()
    skills = SkillNodeSerializer(many=True)


class EffortPatternSerializer(serializers.Serializer):
    pattern = serializers.CharField()
    trend = serializers.CharField()
    context = serializers.CharField()
    has_error_handling_mastery = serializers.BooleanField()


class LearningFrictionSignalSerializer(serializers.Serializer):
    signal_type = serializers.CharField()
    concept = serializers.CharField()
    suggested_mentor_action = serializers.CharField()
    is_active = serializers.BooleanField()


class MentorIntelligenceDossierReadModelSerializer(serializers.Serializer):
    learner_id = serializers.CharField()
    student_code = serializers.CharField()
    display_name = serializers.CharField()
    pedagogical_summary = serializers.ListField(child=serializers.CharField())
    evidence_trace = serializers.ListField(child=serializers.CharField())
    suggested_socratic_prompts = serializers.ListField(child=serializers.CharField())
    friction_signal = LearningFrictionSignalSerializer(allow_null=True, required=False)


class ParentInsightReadModelSerializer(serializers.Serializer):
    learner_id = serializers.CharField()
    developmental_translation = serializers.CharField()
    home_support_cues = serializers.ListField(child=serializers.CharField())
    technical_jargon_suppressed = serializers.BooleanField(default=True)
    last_briefing_at = serializers.CharField(allow_null=True, required=False)


class StudentReflectionEntrySerializer(serializers.Serializer):
    reflection_id = serializers.CharField()
    milestone_slug = serializers.CharField()
    reflection_text = serializers.CharField()
    sentiment = serializers.CharField()
    created_at = serializers.CharField()
    status = serializers.CharField()


class UnifiedIntelligenceProjectionSerializer(serializers.Serializer):
    """
    Composite Read Projection aggregating multi-role intelligence views under strict permission filtering.
    """
    skill_graph = LearnerSkillGraphReadModelSerializer(allow_null=True, required=False)
    mentor_dossier = MentorIntelligenceDossierReadModelSerializer(allow_null=True, required=False)
    parent_insight = ParentInsightReadModelSerializer(allow_null=True, required=False)
    reflections = StudentReflectionEntrySerializer(many=True, required=False)
