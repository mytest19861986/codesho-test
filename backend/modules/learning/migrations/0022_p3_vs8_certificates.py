import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0021_p3_vs7_assessments_rls'),
        ('platform_tenant', '0003_synthetic_membership_activation'),
    ]

    operations = [
        migrations.CreateModel(
            name='CertificateTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('version', models.PositiveIntegerField(default=1)),
                ('title', models.CharField(max_length=160)),
                ('description', models.TextField(blank=True, default='')),
                ('min_score_percentage', models.DecimalField(decimal_places=2, default=70.0, max_digits=5)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificate_templates', to='learning.course')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificate_templates', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [models.Index(fields=['tenant', 'course', 'is_active'], name='certtmpl_t_course_act_ix')],
            },
        ),
        migrations.CreateModel(
            name='CourseCertificate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('completion_round', models.PositiveIntegerField(default=1)),
                ('certificate_number', models.CharField(db_index=True, max_length=64)),
                ('verification_hash', models.CharField(db_index=True, max_length=64)),
                ('status', models.CharField(choices=[('ISSUED', 'Issued'), ('REVOKED', 'Revoked')], default='ISSUED', max_length=16)),
                ('final_score', models.DecimalField(decimal_places=2, max_digits=5)),
                ('completion_snapshot', models.JSONField(default=dict)),
                ('source_event_id', models.UUIDField(db_index=True)),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('revoked_at', models.DateTimeField(blank=True, null=True)),
                ('revocation_reason', models.TextField(blank=True, default='')),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='issued_certificates', to='learning.course')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='issued_certificates', to='learning.certificatetemplate')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issued_certificates', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['tenant', 'student_id', 'status'], name='coursecert_t_stu_status_ix'),
                    models.Index(fields=['tenant', 'certificate_number'], name='coursecert_t_number_ix'),
                ],
            },
        ),
        migrations.CreateModel(
            name='CertificateVerificationRecord',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('queried_number', models.CharField(db_index=True, max_length=64)),
                ('result_status', models.CharField(max_length=16)),
                ('queried_by_role', models.CharField(default='anonymous', max_length=16)),
                ('queried_at', models.DateTimeField(auto_now_add=True)),
                ('certificate', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='verification_records', to='learning.coursecertificate')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='certificate_verification_records', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [models.Index(fields=['tenant', 'queried_number', 'queried_at'], name='certverif_t_num_date_ix')],
            },
        ),
        migrations.AddConstraint(
            model_name='certificatetemplate',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_certtemplate_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='certificatetemplate',
            constraint=models.UniqueConstraint(fields=('tenant', 'course', 'version'), name='learning_certtemplate_tenant_course_ver_uniq'),
        ),
        migrations.AddConstraint(
            model_name='coursecertificate',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_coursecert_tenant_id_uniq'),
        ),
        migrations.AddConstraint(
            model_name='coursecertificate',
            constraint=models.UniqueConstraint(fields=('tenant', 'course', 'student_id', 'completion_round'), name='learning_coursecert_round_uniq'),
        ),
        migrations.AddConstraint(
            model_name='coursecertificate',
            constraint=models.UniqueConstraint(fields=('tenant', 'certificate_number'), name='learning_coursecert_number_uniq'),
        ),
        migrations.AddConstraint(
            model_name='coursecertificate',
            constraint=models.UniqueConstraint(fields=('tenant', 'verification_hash'), name='learning_coursecert_hash_uniq'),
        ),
        migrations.AddConstraint(
            model_name='coursecertificate',
            constraint=models.UniqueConstraint(fields=('tenant', 'source_event_id'), name='learning_coursecert_source_event_uniq'),
        ),
        migrations.AddConstraint(
            model_name='coursecertificate',
            constraint=models.UniqueConstraint(condition=models.Q(('status', 'ISSUED')), fields=('tenant', 'course', 'student_id'), name='idx_unique_active_certificate'),
        ),
        migrations.AddConstraint(
            model_name='certificateverificationrecord',
            constraint=models.UniqueConstraint(fields=('tenant', 'id'), name='learning_certverif_tenant_id_uniq'),
        ),
    ]
