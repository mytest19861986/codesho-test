# Generated for P3-MACRO-EPIC-17-19: Mentor Operations, Learning Continuity & Program Success
# Models: MentorCaseloadAssignment, SupportQueueItem, LearningCheckIn, FollowUpCommitment, ProgramSupportAggregate, MentorOperationsAuditLog

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0039_phase3_vs16_coaching_and_intervention_rls'),
        ('platform_tenant', '0004_p3_vs12_guardian_access_grant'),
    ]

    operations = [
        migrations.CreateModel(
            name='MentorCaseloadAssignment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mentor_id', models.UUIDField(db_index=True)),
                ('student_id', models.UUIDField(db_index=True)),
                ('is_active', models.BooleanField(default=True)),
                ('capacity_weight', models.DecimalField(decimal_places=2, default=1.0, max_digits=3)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('unassigned_at', models.DateTimeField(blank=True, null=True)),
                ('unassignment_reason', models.CharField(blank=True, max_length=1000, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_caseload_assignments', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_mentorcaseloadassignment',
            },
        ),
        migrations.CreateModel(
            name='SupportQueueItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mentor_id', models.UUIDField(db_index=True)),
                ('student_id', models.UUIDField(db_index=True)),
                ('urgency_level', models.CharField(choices=[('LOW', 'Low'), ('NORMAL', 'Normal'), ('HIGH', 'High'), ('CRITICAL', 'Critical')], default='NORMAL', max_length=32)),
                ('queue_status', models.CharField(choices=[('PENDING', 'Pending'), ('IN_REVIEW', 'In Review'), ('RESOLVED', 'Resolved'), ('DISMISSED', 'Dismissed')], default='PENDING', max_length=32)),
                ('due_date', models.DateTimeField()),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('source_intervention', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='queue_items', to='learning.supportintervention')),
                ('source_session', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='queue_items', to='learning.coachingsession')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='support_queue_items', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_supportqueueitem',
            },
        ),
        migrations.CreateModel(
            name='LearningCheckIn',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mentor_id', models.UUIDField(db_index=True)),
                ('student_id', models.UUIDField(db_index=True)),
                ('status', models.CharField(choices=[('SCHEDULED', 'Scheduled'), ('IN_PROGRESS', 'In Progress'), ('COMPLETED', 'Completed'), ('RESCHEDULED', 'Rescheduled'), ('CANCELLED', 'Cancelled')], default='SCHEDULED', max_length=32)),
                ('scheduled_start', models.DateTimeField()),
                ('actual_start', models.DateTimeField(blank=True, null=True)),
                ('actual_end', models.DateTimeField(blank=True, null=True)),
                ('meeting_link', models.CharField(blank=True, max_length=500, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('student_acknowledged', models.BooleanField(default=False)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('caseload_assignment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='checkins', to='learning.mentorcaseloadassignment')),
                ('rescheduled_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='rescheduled_to', to='learning.learningcheckin')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_checkins', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_learningcheckin',
            },
        ),
        migrations.CreateModel(
            name='FollowUpCommitment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('owner_role', models.CharField(choices=[('MENTOR', 'Mentor'), ('STUDENT', 'Student')], max_length=16)),
                ('title', models.CharField(max_length=255)),
                ('due_date', models.DateTimeField()),
                ('is_completed', models.BooleanField(default=False)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('checkin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='commitments', to='learning.learningcheckin')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followup_commitments', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_followupcommitment',
            },
        ),
        migrations.CreateModel(
            name='ProgramSupportAggregate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('period_start', models.DateTimeField()),
                ('period_end', models.DateTimeField()),
                ('total_assigned_students', models.IntegerField(default=0)),
                ('total_active_interventions', models.IntegerField(default=0)),
                ('total_completed_checkins', models.IntegerField(default=0)),
                ('average_response_time_hours', models.DecimalField(decimal_places=2, default=0.0, max_digits=6)),
                ('support_coverage_ratio', models.DecimalField(decimal_places=3, default=0.0, max_digits=4)),
                ('is_authoritative', models.BooleanField(default=False)),
                ('aggregated_at', models.DateTimeField(auto_now_add=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='program_support_aggregates', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_programsupportaggregate',
            },
        ),
        migrations.CreateModel(
            name='MentorOperationsAuditLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('action_type', models.CharField(choices=[('ASSIGN_CASELOAD', 'Assign Caseload'), ('UNASSIGN_CASELOAD', 'Unassign Caseload'), ('QUEUE_ITEM_PENDING', 'Queue Item Pending'), ('QUEUE_ITEM_IN_REVIEW', 'Queue Item In Review'), ('QUEUE_ITEM_RESOLVED', 'Queue Item Resolved'), ('QUEUE_ITEM_DISMISSED', 'Queue Item Dismissed'), ('SCHEDULE_CHECKIN', 'Schedule Check-in'), ('START_CHECKIN', 'Start Check-in'), ('COMPLETE_CHECKIN', 'Complete Check-in'), ('RESCHEDULE_CHECKIN', 'Reschedule Check-in'), ('CANCEL_CHECKIN', 'Cancel Check-in'), ('CREATE_COMMITMENT', 'Create Commitment'), ('COMPLETE_COMMITMENT', 'Complete Commitment'), ('GENERATE_SUPPORT_AGGREGATE', 'Generate Support Aggregate')], max_length=64)),
                ('actor_id', models.UUIDField(db_index=True)),
                ('details', models.JSONField(default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('target_aggregate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.programsupportaggregate')),
                ('target_caseload', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.mentorcaseloadassignment')),
                ('target_checkin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.learningcheckin')),
                ('target_commitment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.followupcommitment')),
                ('target_queue_item', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='audit_logs', to='learning.supportqueueitem')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mentor_operations_audit_logs', to='platform_tenant.tenant')),
            ],
            options={
                'db_table': 'learning_mentoroperationsauditlog',
            },
        ),
    ]
