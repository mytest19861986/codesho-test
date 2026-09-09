# Generated for P3-VS14: Student Learning Operations, Reflection & AI-Assisted Growth

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0033_phase3_vs13_growth_insights_rls'),
        ('platform_tenant', '0004_p3_vs12_guardian_access_grant'),
    ]

    operations = [
        migrations.CreateModel(
            name='LearningReflection',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('prompt_type', models.CharField(choices=[('WEEKLY_REVIEW', 'Weekly Review'), ('MILESTONE_RETROSPECTIVE', 'Milestone Retrospective'), ('OBSTACLE_ANALYSIS', 'Obstacle Analysis'), ('FREE_REFLECTION', 'Free Reflection')], max_length=32)),
                ('content', models.TextField()),
                ('mood_sentiment', models.CharField(choices=[('GROWTH_MINDSET', 'Growth Mindset'), ('CONFIDENT', 'Confident'), ('CHALLENGED', 'Challenged'), ('CURIOUS', 'Curious'), ('NEUTRAL', 'Neutral')], default='NEUTRAL', max_length=32)),
                ('is_retracted', models.BooleanField(default=False)),
                ('retracted_at', models.DateTimeField(blank=True, null=True)),
                ('retraction_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_reflections', to='platform_tenant.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='StudentLearningGoal',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('domain', models.CharField(db_index=True, max_length=64)),
                ('status', models.CharField(choices=[('DRAFT', 'Draft'), ('ACTIVE', 'Active'), ('ACHIEVED', 'Achieved'), ('PAUSED', 'Paused'), ('ARCHIVED', 'Archived'), ('SUPERSEDED', 'Superseded')], default='DRAFT', max_length=32)),
                ('target_date', models.DateField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('target_milestone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='targeted_goals', to='learning.learningmilestone')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_goals', to='platform_tenant.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='GoalActionPlan',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('step_order', models.PositiveSmallIntegerField()),
                ('description', models.CharField(max_length=500)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('SKIPPED', 'Skipped')], default='PENDING', max_length=32)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('goal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='action_steps', to='learning.studentlearninggoal')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='goal_action_plans', to='platform_tenant.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='AIAssistedGrowthSuggestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('suggestion_type', models.CharField(max_length=32)),
                ('recommended_action', models.CharField(max_length=500)),
                ('rationale', models.TextField()),
                ('evidence_context', models.JSONField()),
                ('model_identifier', models.CharField(max_length=64)),
                ('provenance_digest', models.CharField(max_length=64)),
                ('idempotency_key', models.CharField(max_length=128)),
                ('status', models.CharField(choices=[('PENDING', 'Pending (Moderation Gate)'), ('PRESENTED', 'Presented to Student'), ('ACCEPTED', 'Accepted by Student'), ('DISMISSED', 'Dismissed by Student'), ('WITHDRAWN', 'Withdrawn by Mentor/System'), ('SUPERSEDED', 'Superseded by Newer Insight')], default='PENDING', max_length=32)),
                ('is_authoritative', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('generation_run', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='growth_suggestions', to='learning.calculationrun')),
                ('source_insight', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='growth_suggestions', to='learning.learninginsight')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ai_growth_suggestions', to='platform_tenant.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='MentorReflectionFeedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mentor_id', models.UUIDField(db_index=True)),
                ('feedback_text', models.TextField()),
                ('is_retracted', models.BooleanField(default=False)),
                ('retracted_at', models.DateTimeField(blank=True, null=True)),
                ('retraction_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reflection', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_feedbacks', to='learning.learningreflection')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_feedbacks', to='platform_tenant.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='ReflectionAuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('actor_id', models.UUIDField(db_index=True)),
                ('action', models.CharField(choices=[('CREATE_REFLECTION', 'Create Reflection'), ('RETRACT_REFLECTION', 'Retract Reflection'), ('RESTORE_REFLECTION', 'Restore Reflection'), ('CREATE_GOAL', 'Create Goal'), ('TRANSITION_GOAL_STATUS', 'Transition Goal Status'), ('CREATE_ACTION_PLAN', 'Create Action Plan'), ('UPDATE_ACTION_PLAN', 'Update Action Plan'), ('GENERATE_AI_SUGGESTION', 'Generate AI Suggestion'), ('MODERATE_AI_SUGGESTION', 'Moderate AI Suggestion'), ('ACCEPT_AI_SUGGESTION', 'Accept AI Suggestion'), ('DISMISS_AI_SUGGESTION', 'Dismiss AI Suggestion'), ('SUPERSEDE_AI_SUGGESTION', 'Supersede AI Suggestion'), ('WITHDRAW_AI_SUGGESTION', 'Withdraw AI Suggestion'), ('POST_MENTOR_FEEDBACK', 'Post Mentor Feedback'), ('RETRACT_MENTOR_FEEDBACK', 'Retract Mentor Feedback')], max_length=64)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('target_feedback', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.mentorreflectionfeedback')),
                ('target_goal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.studentlearninggoal')),
                ('target_reflection', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.learningreflection')),
                ('target_suggestion', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.aiassistedgrowthsuggestion')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reflection_audit_logs', to='platform_tenant.tenant')),
            ],
        ),
        # Constraints and Indexes
        migrations.AddConstraint(
            model_name='learningreflection',
            constraint=models.UniqueConstraint(fields=['tenant', 'id'], name='uq_learning_learningreflection_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='learningreflection',
            constraint=models.CheckConstraint(condition=models.Q(prompt_type__in=['WEEKLY_REVIEW', 'MILESTONE_RETROSPECTIVE', 'OBSTACLE_ANALYSIS', 'FREE_REFLECTION']), name='chk_reflection_prompt_type'),
        ),
        migrations.AddConstraint(
            model_name='learningreflection',
            constraint=models.CheckConstraint(condition=models.Q(mood_sentiment__in=['GROWTH_MINDSET', 'CONFIDENT', 'CHALLENGED', 'CURIOUS', 'NEUTRAL']), name='chk_reflection_mood'),
        ),
        migrations.AddConstraint(
            model_name='learningreflection',
            constraint=models.CheckConstraint(condition=models.Q(is_retracted=False, retracted_at__isnull=True, retraction_reason__isnull=True) | models.Q(is_retracted=True, retracted_at__isnull=False, retraction_reason__isnull=False), name='chk_reflection_retraction_consistency'),
        ),
        migrations.AddIndex(
            model_name='learningreflection',
            index=models.Index(fields=['tenant', 'student_id', '-created_at'], name='idx_reflection_tenant_student'),
        ),
        migrations.AddConstraint(
            model_name='studentlearninggoal',
            constraint=models.UniqueConstraint(fields=['tenant', 'id'], name='uq_learning_studentlearninggoal_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='studentlearninggoal',
            constraint=models.UniqueConstraint(condition=models.Q(status='ACTIVE'), fields=['tenant', 'student_id', 'domain'], name='uq_goal_student_domain_active'),
        ),
        migrations.AddConstraint(
            model_name='studentlearninggoal',
            constraint=models.CheckConstraint(condition=models.Q(status__in=['DRAFT', 'ACTIVE', 'ACHIEVED', 'PAUSED', 'ARCHIVED', 'SUPERSEDED']), name='chk_goal_status'),
        ),
        migrations.AddConstraint(
            model_name='studentlearninggoal',
            constraint=models.CheckConstraint(condition=models.Q(status='ACHIEVED', completed_at__isnull=False) | (~models.Q(status='ACHIEVED') & models.Q(completed_at__isnull=True)), name='chk_goal_completion_consistency'),
        ),
        migrations.AddIndex(
            model_name='studentlearninggoal',
            index=models.Index(fields=['tenant', 'student_id', 'status'], name='idx_goal_tenant_student_status'),
        ),
        migrations.AddConstraint(
            model_name='goalactionplan',
            constraint=models.UniqueConstraint(fields=['tenant', 'id'], name='uq_learning_goalactionplan_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='goalactionplan',
            constraint=models.UniqueConstraint(fields=['tenant', 'goal', 'step_order'], name='uq_goalactionplan_step'),
        ),
        migrations.AddConstraint(
            model_name='goalactionplan',
            constraint=models.CheckConstraint(condition=models.Q(step_order__gte=1), name='chk_action_step_order'),
        ),
        migrations.AddConstraint(
            model_name='goalactionplan',
            constraint=models.CheckConstraint(condition=models.Q(status__in=['PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED']), name='chk_action_status'),
        ),
        migrations.AddConstraint(
            model_name='goalactionplan',
            constraint=models.CheckConstraint(condition=models.Q(status='COMPLETED', completed_at__isnull=False) | (~models.Q(status='COMPLETED') & models.Q(completed_at__isnull=True)), name='chk_action_completed_consistency'),
        ),
        migrations.AddConstraint(
            model_name='aiassistedgrowthsuggestion',
            constraint=models.UniqueConstraint(fields=['tenant', 'id'], name='uq_learning_aiassistedgrowthsuggestion_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='aiassistedgrowthsuggestion',
            constraint=models.UniqueConstraint(fields=['tenant', 'idempotency_key'], name='uq_growthsuggestion_idempotency'),
        ),
        migrations.AddConstraint(
            model_name='aiassistedgrowthsuggestion',
            constraint=models.UniqueConstraint(condition=models.Q(status='PRESENTED'), fields=['tenant', 'student_id', 'suggestion_type'], name='uq_suggestion_presented_singleton'),
        ),
        migrations.AddConstraint(
            model_name='aiassistedgrowthsuggestion',
            constraint=models.CheckConstraint(condition=models.Q(status__in=['PENDING', 'PRESENTED', 'ACCEPTED', 'DISMISSED', 'WITHDRAWN', 'SUPERSEDED']), name='chk_suggestion_status'),
        ),
        migrations.AddConstraint(
            model_name='aiassistedgrowthsuggestion',
            constraint=models.CheckConstraint(condition=models.Q(is_authoritative=False), name='chk_suggestion_advisory_invariant'),
        ),
        migrations.AddConstraint(
            model_name='aiassistedgrowthsuggestion',
            constraint=models.CheckConstraint(condition=~models.Q(evidence_context={}), name='chk_suggestion_evidence_context'),
        ),
        migrations.AddIndex(
            model_name='aiassistedgrowthsuggestion',
            index=models.Index(fields=['tenant', 'student_id', 'status'], name='idx_suggestion_student_status'),
        ),
        migrations.AddConstraint(
            model_name='mentorreflectionfeedback',
            constraint=models.UniqueConstraint(fields=['tenant', 'id'], name='uq_learning_mentorreflectionfeedback_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='mentorreflectionfeedback',
            constraint=models.CheckConstraint(condition=models.Q(is_retracted=False, retracted_at__isnull=True, retraction_reason__isnull=True) | models.Q(is_retracted=True, retracted_at__isnull=False, retraction_reason__isnull=False), name='chk_feedback_retraction_consistency'),
        ),
        migrations.AddConstraint(
            model_name='reflectionauditlog',
            constraint=models.UniqueConstraint(fields=['tenant', 'id'], name='uq_learning_reflectionauditlog_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='reflectionauditlog',
            constraint=models.CheckConstraint(condition=models.Q(action__in=['CREATE_REFLECTION', 'RETRACT_REFLECTION', 'RESTORE_REFLECTION', 'CREATE_GOAL', 'TRANSITION_GOAL_STATUS', 'CREATE_ACTION_PLAN', 'UPDATE_ACTION_PLAN', 'GENERATE_AI_SUGGESTION', 'MODERATE_AI_SUGGESTION', 'ACCEPT_AI_SUGGESTION', 'DISMISS_AI_SUGGESTION', 'SUPERSEDE_AI_SUGGESTION', 'WITHDRAW_AI_SUGGESTION', 'POST_MENTOR_FEEDBACK', 'RETRACT_MENTOR_FEEDBACK']), name='chk_audit_action'),
        ),
        migrations.AddIndex(
            model_name='reflectionauditlog',
            index=models.Index(fields=['tenant', 'actor_id', '-created_at'], name='idx_audit_tenant_actor_time'),
        ),
        migrations.AddIndex(
            model_name='reflectionauditlog',
            index=models.Index(fields=['tenant', 'target_reflection'], name='idx_audit_tenant_refl'),
        ),
        migrations.AddIndex(
            model_name='reflectionauditlog',
            index=models.Index(fields=['tenant', 'target_goal'], name='idx_audit_tenant_goal'),
        ),
        migrations.AddIndex(
            model_name='reflectionauditlog',
            index=models.Index(fields=['tenant', 'target_feedback'], name='idx_audit_tenant_feedback'),
        ),
        migrations.AddIndex(
            model_name='reflectionauditlog',
            index=models.Index(fields=['tenant', 'target_suggestion'], name='idx_audit_tenant_sugg'),
        ),
    ]
