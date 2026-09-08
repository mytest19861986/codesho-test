import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0023_p3_vs8_certificates_rls'),
        ('platform_tenant', '0003_synthetic_membership_activation'),
    ]

    operations = [
        migrations.CreateModel(
            name='CohortSupervision',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('mentor_id', models.UUIDField(db_index=True)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('assigned_by', models.UUIDField(blank=True, null=True)),
                ('is_lead', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(db_index=True, default=True)),
                ('revoked_at', models.DateTimeField(blank=True, null=True)),
                ('revoked_by', models.UUIDField(blank=True, null=True)),
                ('cohort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervisors', to='learning.cohort')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cohort_supervisions', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [models.Index(fields=['tenant', 'mentor_id', 'is_active'], name='cohortsup_t_men_act_ix')],
            },
        ),
        migrations.CreateModel(
            name='CohortProgressAggregate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_enrolled', models.PositiveIntegerField(default=0)),
                ('active_students', models.PositiveIntegerField(default=0)),
                ('completed_students', models.PositiveIntegerField(default=0)),
                ('average_progress_percentage', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('average_assessment_score', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('completion_rate', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cohort', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='analytics_aggregate', to='learning.cohort')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cohort_progress_aggregates', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [models.Index(fields=['tenant', 'cohort'], name='cohortprog_t_coh_ix')],
            },
        ),
        migrations.CreateModel(
            name='StudentSupervisionAlert',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('alert_type', models.CharField(choices=[('STALLED_PROGRESS', 'Stalled Progress'), ('FAILED_ASSESSMENTS', 'Failed Assessments'), ('AT_RISK_DROPOUT', 'At Risk Dropout')], max_length=32)),
                ('severity', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], max_length=16)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('ACKNOWLEDGED', 'Acknowledged'), ('RESOLVED', 'Resolved')], db_index=True, default='ACTIVE', max_length=16)),
                ('rule_version', models.PositiveIntegerField(default=1)),
                ('deduplication_key', models.CharField(db_index=True, max_length=255, unique=True)),
                ('details', models.JSONField(default=dict)),
                ('schema_version', models.PositiveIntegerField(default=1)),
                ('data_classification', models.CharField(default='INTERNAL_EDUCATIONAL_ANALYTICS', max_length=32)),
                ('acknowledged_at', models.DateTimeField(blank=True, null=True)),
                ('acknowledged_by', models.UUIDField(blank=True, null=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolved_by', models.UUIDField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('cohort', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='alerts', to='learning.cohort')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_supervision_alerts', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['tenant', 'cohort', 'status', 'resolved_at'], name='supalert_t_c_st_res_ix'),
                    models.Index(fields=['tenant', 'student_id', 'status'], name='supalert_t_stu_st_ix'),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='cohortsupervision',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_cohortsupervision_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='cohortsupervision',
            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True)), fields=('tenant', 'cohort', 'mentor_id'), name='learning_cohortsupervision_active_uniq'),
        ),
        migrations.AddConstraint(
            model_name='cohortsupervision',
            constraint=models.UniqueConstraint(condition=models.Q(('is_active', True), ('is_lead', True)), fields=('tenant', 'cohort'), name='learning_cohortsupervision_single_lead_uniq'),
        ),
        migrations.AddConstraint(
            model_name='cohortprogressaggregate',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_cohortprogaggregate_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='cohortprogressaggregate',
            constraint=models.UniqueConstraint(fields=('tenant', 'cohort'), name='learning_cohortprogaggregate_tenant_cohort_uniq'),
        ),
        migrations.AddConstraint(
            model_name='studentsupervisionalert',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_studentsupalert_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='studentsupervisionalert',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'ACTIVE')), fields=('tenant', 'cohort', 'student_id', 'alert_type'), name='learning_supalert_active_dedup_uniq'),
        ),
    ]
