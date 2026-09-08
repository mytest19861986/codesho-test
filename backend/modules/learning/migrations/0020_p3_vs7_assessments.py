import django.core.validators
import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0017_p3_vs5_enrollment_rls'),
        ('platform_tenant', '0003_synthetic_membership_activation'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeAssessment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('language', models.CharField(default='python', max_length=32)),
                ('timeout_seconds', models.PositiveIntegerField(default=5, validators=[django.core.validators.MinValueValidator(1)])),
                ('memory_limit_mb', models.PositiveIntegerField(default=256, validators=[django.core.validators.MinValueValidator(16)])),
                ('starter_code', models.TextField(blank=True, default='')),
                ('testcases', models.JSONField(default=list)),
                ('testcases_hash', models.CharField(blank=True, db_index=True, max_length=64)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='code_assessments', to='learning.lesson')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='code_assessments', to='platform_tenant.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='CodeExecutionRun',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('attempt_number', models.PositiveIntegerField(default=1)),
                ('submitted_code', models.TextField()),
                ('code_hash', models.CharField(db_index=True, max_length=64)),
                ('runtime_image_hash', models.CharField(default='codesho-python-sandbox:sha256-standard', max_length=64)),
                ('idempotency_key', models.CharField(blank=True, max_length=128, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('running', 'Running'), ('passed', 'Passed'), ('failed', 'Failed'), ('timed_out', 'Timed Out'), ('error', 'Error')], db_index=True, default='pending', max_length=16)),
                ('duration_ms', models.PositiveIntegerField(default=0)),
                ('memory_used_kb', models.PositiveIntegerField(default=0)),
                ('stdout_log', models.TextField(blank=True, default='')),
                ('stderr_log', models.TextField(blank=True, default='')),
                ('lease_expires_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assessment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='execution_runs', to='learning.codeassessment')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='code_execution_runs', to='platform_tenant.tenant')),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentResult',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('passed_tests_count', models.PositiveIntegerField(default=0)),
                ('total_tests_count', models.PositiveIntegerField(default=0)),
                ('score', models.DecimalField(decimal_places=2, default=0.0, max_digits=5)),
                ('is_passed', models.BooleanField(default=False)),
                ('is_final', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='learning.codeassessment')),
                ('execution_run', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='result', to='learning.codeexecutionrun')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_results', to='platform_tenant.tenant')),
            ],
        ),
        migrations.AddIndex(
            model_name='codeassessment',
            index=models.Index(fields=['tenant', 'lesson', 'is_active'], name='codeassess_t_les_act_ix'),
        ),
        migrations.AddConstraint(
            model_name='codeassessment',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_codeassessment_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='codeassessment',
            constraint=models.UniqueConstraint(fields=('tenant', 'lesson'), name='learning_codeassessment_tenant_lesson_uniq'),
        ),
        migrations.AddIndex(
            model_name='codeexecutionrun',
            index=models.Index(fields=['tenant', 'student_id', 'status'], name='coderun_t_student_st_ix'),
        ),
        migrations.AddIndex(
            model_name='codeexecutionrun',
            index=models.Index(fields=['tenant', 'assessment', 'status'], name='coderun_t_assess_st_ix'),
        ),
        migrations.AddIndex(
            model_name='codeexecutionrun',
            index=models.Index(fields=['status', 'lease_expires_at'], name='coderun_lease_recover_ix'),
        ),
        migrations.AddConstraint(
            model_name='codeexecutionrun',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_coderun_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='codeexecutionrun',
            constraint=models.UniqueConstraint(condition=models.Q(('assessment__isnull', False)), fields=('tenant', 'assessment', 'student_id', 'attempt_number'), name='learning_coderun_attempt_uniq'),
        ),
        migrations.AddConstraint(
            model_name='codeexecutionrun',
            constraint=models.UniqueConstraint(condition=models.Q(('idempotency_key__isnull', False)), fields=('tenant', 'idempotency_key'), name='learning_coderun_idemp_uniq'),
        ),
        migrations.AddIndex(
            model_name='assessmentresult',
            index=models.Index(fields=['tenant', 'student_id', 'is_passed'], name='assessres_t_student_pass_ix'),
        ),
        migrations.AddConstraint(
            model_name='assessmentresult',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_assessresult_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='assessmentresult',
            constraint=models.UniqueConstraint(fields=('tenant', 'assessment', 'student_id'), name='learning_assessresult_final_uniq'),
        ),
    ]
