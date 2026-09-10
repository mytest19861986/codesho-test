# Generated for P3-VS16: Coaching Sessions, Notes, Interventions, Follow-up Actions, and Audit Log

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0037_phase3_vs15_learning_success_rls'),
        ('platform_tenant', '0004_p3_vs12_guardian_access_grant'),
    ]

    operations = [
        migrations.CreateModel(
            name='CoachingSession',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('mentor_id', models.UUIDField(db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('CANCELLED', 'Cancelled')], default='SCHEDULED', max_length=32)),
                ('scheduled_at', models.DateTimeField()),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('cancelled_at', models.DateTimeField(blank=True, null=True)),
                ('cancellation_reason', models.CharField(blank=True, max_length=1000, null=True)),
                ('summary', models.TextField(blank=True, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('learning_insight', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coaching_sessions', to='learning.learninginsight')),
                ('success_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coaching_sessions', to='learning.learningstudentsuccessplan')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_sessions', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_coachingsession',
            },
        ),
        migrations.CreateModel(
            name='CoachingNote',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('author_id', models.UUIDField(db_index=True)),
                ('note_type', models.CharField(choices=[('OBSERVATION', 'Observation'), ('STRENGTH', 'Strength'), ('GROWTH_OPPORTUNITY', 'Growth Opportunity'), ('ACTION_ITEM', 'Action Item'), ('SUMMARY', 'Summary')], default='OBSERVATION', max_length=32)),
                ('content', models.TextField()),
                ('is_shared_with_student', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='learning.coachingsession')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_notes', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_coachingnote',
            },
        ),
        migrations.CreateModel(
            name='SupportIntervention',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('mentor_id', models.UUIDField(db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('ACADEMIC_SCAFFOLDING', 'Academic Scaffolding'), ('RESOURCE_RECOMMENDATION', 'Resource Recommendation'), ('STUDY_STRATEGY', 'Study Strategy'), ('PACING_ADJUSTMENT', 'Pacing Adjustment'), ('PEER_STUDY_CONNECTION', 'Peer Study Connection')], default='ACADEMIC_SCAFFOLDING', max_length=64)),
                ('status', models.CharField(choices=[('PROPOSED', 'Proposed'), ('ACCEPTED', 'Accepted'), ('DECLINED', 'Declined'), ('ACTIVE', 'Active'), ('PAUSED', 'Paused'), ('COMPLETED', 'Completed')], default='PROPOSED', max_length=32)),
                ('is_authoritative', models.BooleanField(default=False)),
                ('rationale', models.TextField()),
                ('student_feedback', models.TextField(blank=True, null=True)),
                ('proposed_at', models.DateTimeField(auto_now_add=True)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('declined_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('paused_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('success_plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='support_interventions', to='learning.learningstudentsuccessplan')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_interventions', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_supportintervention',
            },
        ),
        migrations.CreateModel(
            name='FollowUpAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('assigned_by_id', models.UUIDField(db_index=True)),
                ('title', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('SKIPPED', 'Skipped')], default='PENDING', max_length=32)),
                ('due_date', models.DateTimeField()),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('skipped_at', models.DateTimeField(blank=True, null=True)),
                ('skip_reason', models.CharField(blank=True, max_length=1000, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('intervention', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_actions', to='learning.supportintervention')),
                ('session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='followup_actions', to='learning.coachingsession')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_followup_actions', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_followupaction',
            },
        ),
        migrations.CreateModel(
            name='CoachingAuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(choices=[('SCHEDULE_SESSION', 'Schedule Session'), ('START_SESSION', 'Start Session'), ('RESCHEDULE_SESSION', 'Reschedule Session'), ('CANCEL_SESSION', 'Cancel Session'), ('COMPLETE_SESSION', 'Complete Session'), ('CREATE_NOTE', 'Create Note'), ('PROPOSE_INTERVENTION', 'Propose Intervention'), ('ACCEPT_INTERVENTION', 'Accept Intervention'), ('DECLINE_INTERVENTION', 'Decline Intervention'), ('START_INTERVENTION', 'Start Intervention'), ('PAUSE_INTERVENTION', 'Pause Intervention'), ('RESUME_INTERVENTION', 'Resume Intervention'), ('COMPLETE_INTERVENTION', 'Complete Intervention'), ('ASSIGN_ACTION', 'Assign Action'), ('START_ACTION', 'Start Action'), ('COMPLETE_ACTION', 'Complete Action'), ('SKIP_ACTION', 'Skip Action')], max_length=64)),
                ('actor_id', models.UUIDField(db_index=True)),
                ('details', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('target_action', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.followupaction')),
                ('target_intervention', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.supportintervention')),
                ('target_note', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.coachingnote')),
                ('target_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.coachingsession')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coaching_audit_logs', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_coachingauditlog',
            },
        ),
        migrations.AddConstraint(
            model_name='coachingsession',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_coachingsession_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='coachingsession',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['SCHEDULED', 'IN_PROGRESS', 'COMPLETED', 'CANCELLED'])), name='chk_coachingsession_status'),
        ),
        migrations.AddIndex(
            model_name='coachingsession',
            index=models.Index(fields=['tenant', 'student_id', '-scheduled_at'], name='idx_coachingsession_stud_time'),
        ),
        migrations.AddIndex(
            model_name='coachingsession',
            index=models.Index(fields=['tenant', 'mentor_id', '-scheduled_at'], name='idx_coachingsession_ment_time'),
        ),
        migrations.AddConstraint(
            model_name='coachingnote',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_coachingnote_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='coachingnote',
            constraint=models.CheckConstraint(condition=models.Q(('note_type__in', ['OBSERVATION', 'STRENGTH', 'GROWTH_OPPORTUNITY', 'ACTION_ITEM', 'SUMMARY'])), name='chk_coachingnote_type'),
        ),
        migrations.AddIndex(
            model_name='coachingnote',
            index=models.Index(fields=['tenant', 'session', 'created_at'], name='idx_coachingnote_session_time'),
        ),
        migrations.AddConstraint(
            model_name='supportintervention',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_supportintervention_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='supportintervention',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['PROPOSED', 'ACCEPTED', 'DECLINED', 'ACTIVE', 'PAUSED', 'COMPLETED'])), name='chk_intervention_status'),
        ),
        migrations.AddConstraint(
            model_name='supportintervention',
            constraint=models.CheckConstraint(condition=models.Q(('category__in', ['ACADEMIC_SCAFFOLDING', 'RESOURCE_RECOMMENDATION', 'STUDY_STRATEGY', 'PACING_ADJUSTMENT', 'PEER_STUDY_CONNECTION'])), name='chk_intervention_category_supportive'),
        ),
        migrations.AddConstraint(
            model_name='supportintervention',
            constraint=models.CheckConstraint(condition=models.Q(('is_authoritative', False)), name='chk_intervention_non_authoritative'),
        ),
        migrations.AddIndex(
            model_name='supportintervention',
            index=models.Index(fields=['tenant', 'student_id', 'status'], name='idx_intervention_stud_status'),
        ),
        migrations.AddConstraint(
            model_name='followupaction',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_followupaction_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='followupaction',
            constraint=models.CheckConstraint(condition=models.Q(('status__in', ['PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED'])), name='chk_followupaction_status'),
        ),
        migrations.AddIndex(
            model_name='followupaction',
            index=models.Index(fields=['tenant', 'student_id', 'due_date'], name='idx_followupaction_stud_due'),
        ),
        migrations.AddConstraint(
            model_name='coachingauditlog',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='uq_learning_coachingauditlog_tenant_id'),
        ),
        migrations.AddConstraint(
            model_name='coachingauditlog',
            constraint=models.CheckConstraint(condition=models.Q(('action_type__in', ['SCHEDULE_SESSION', 'START_SESSION', 'RESCHEDULE_SESSION', 'CANCEL_SESSION', 'COMPLETE_SESSION', 'CREATE_NOTE', 'PROPOSE_INTERVENTION', 'ACCEPT_INTERVENTION', 'DECLINE_INTERVENTION', 'START_INTERVENTION', 'PAUSE_INTERVENTION', 'RESUME_INTERVENTION', 'COMPLETE_INTERVENTION', 'ASSIGN_ACTION', 'START_ACTION', 'COMPLETE_ACTION', 'SKIP_ACTION'])), name='chk_coachingaudit_action_type'),
        ),
        migrations.AddIndex(
            model_name='coachingauditlog',
            index=models.Index(fields=['tenant', 'actor_id', '-created_at'], name='idx_coachingaudit_actor_time'),
        ),
        migrations.AddIndex(
            model_name='coachingauditlog',
            index=models.Index(fields=['tenant', 'target_session'], name='idx_coachingaudit_session'),
        ),
        migrations.AddIndex(
            model_name='coachingauditlog',
            index=models.Index(fields=['tenant', 'target_note'], name='idx_coachingaudit_note'),
        ),
        migrations.AddIndex(
            model_name='coachingauditlog',
            index=models.Index(fields=['tenant', 'target_intervention'], name='idx_coachingaudit_interv'),
        ),
        migrations.AddIndex(
            model_name='coachingauditlog',
            index=models.Index(fields=['tenant', 'target_action'], name='idx_coachingaudit_action'),
        ),
    ]
