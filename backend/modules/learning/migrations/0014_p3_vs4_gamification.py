import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0013_p3_vs3_notifications_rls'),
        ('platform_tenant', '0003_synthetic_membership_activation'),
    ]

    operations = [
        migrations.CreateModel(
            name='BadgeDefinition',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('badge_code', models.CharField(db_index=True, max_length=64, unique=True)),
                ('badge_level', models.PositiveSmallIntegerField(default=1)),
                ('title', models.CharField(max_length=160)),
                ('description', models.CharField(default='', max_length=255)),
                ('threshold', models.PositiveIntegerField(default=1)),
                ('is_repeatable', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'constraints': [
                    models.UniqueConstraint(fields=('badge_code', 'badge_level'), name='badge_def_code_level_uniq')
                ],
            },
        ),
        migrations.CreateModel(
            name='StudentProgressionProfile',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('current_streak_days', models.PositiveIntegerField(default=0)),
                ('longest_streak_days', models.PositiveIntegerField(default=0)),
                ('last_qualifying_date', models.DateField(blank=True, null=True)),
                ('total_xp', models.PositiveIntegerField(default=0)),
                ('level', models.PositiveIntegerField(default=1)),
                ('completed_lessons_count', models.PositiveIntegerField(default=0)),
                ('reviewed_submissions_count', models.PositiveIntegerField(default=0)),
                ('version', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_progression_profiles', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [models.Index(fields=['tenant', 'student_id'], name='spp_tenant_student_ix')],
                'constraints': [
                    models.UniqueConstraint(fields=('tenant', 'id'), name='learning_spp_tenant_id_uniq'),
                    models.UniqueConstraint(fields=('tenant', 'student_id'), name='learning_spp_tenant_student_uniq'),
                ],
            },
        ),
        migrations.CreateModel(
            name='StudentBadgeAward',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('student_id', models.UUIDField(db_index=True)),
                ('badge_code', models.CharField(db_index=True, max_length=64)),
                ('badge_level', models.PositiveSmallIntegerField(default=1)),
                ('source_event_id', models.UUIDField(blank=True, db_index=True, null=True)),
                ('idempotency_key', models.CharField(blank=True, max_length=255, null=True)),
                ('awarded_at', models.DateTimeField(auto_now_add=True)),
                ('badge', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='awards', to='learning.badgedefinition')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_badge_awards', to='platform_tenant.tenant')),
            ],
            options={
                'indexes': [
                    models.Index(fields=['tenant', 'student_id', '-awarded_at'], name='sba_tenant_stud_award_ix'),
                    models.Index(fields=['tenant', 'badge_code'], name='sba_tenant_badge_ix'),
                ],
                'constraints': [
                    models.UniqueConstraint(fields=('tenant', 'id'), name='learning_sba_tenant_id_uniq'),
                    models.UniqueConstraint(fields=('tenant', 'student_id', 'badge_code', 'badge_level'), name='learning_sba_tenant_student_badge_level_uniq'),
                    models.UniqueConstraint(condition=models.Q(('idempotency_key__isnull', False)), fields=('tenant', 'idempotency_key'), name='learning_sba_tenant_idemp_uniq'),
                ],
            },
        ),
    ]
