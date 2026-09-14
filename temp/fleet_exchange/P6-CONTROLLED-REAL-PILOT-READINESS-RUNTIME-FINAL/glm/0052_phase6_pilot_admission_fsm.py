# Generated for Phase 6 Controlled Real Pilot Readiness FSM & 14-Gate Admission
import django.db.models.deletion
import uuid
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('learning', '0051_p5_controlled_pilot_activation_fsm'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pilottenantlifecycle',
            name='state',
            field=models.CharField(
                choices=[
                    ('CANDIDATE', 'Candidate'),
                    ('DUE_DILIGENCE', 'Due Diligence'),
                    ('SECURITY_REVIEW', 'Security Review'),
                    ('PRIVACY_REVIEW', 'Privacy Review'),
                    ('OPERATIONAL_REVIEW', 'Operational Review'),
                    ('TECHNICAL_READY', 'Technical Ready'),
                    ('MANAGER_DECISION_REQUIRED', 'Manager Decision Required'),
                    ('MANAGER_AUTHORIZED', 'Manager Authorized'),
                    ('ACTIVATION_WINDOW', 'Activation Window'),
                    ('ACTIVE', 'Active'),
                    ('SUSPENDED', 'Suspended'),
                    ('EXITING', 'Exiting'),
                    ('CLOSED', 'Closed'),
                ],
                default='CANDIDATE',
                max_length=32,
            ),
        ),
        migrations.AddField(
            model_name='pilottenantlifecycle',
            name='security_reviewer_id',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pilottenantlifecycle',
            name='privacy_reviewer_id',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pilottenantlifecycle',
            name='operational_reviewer_id',
            field=models.UUIDField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pilotprerequisitechecklist',
            name='legal_privacy_review_cleared',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pilotprerequisitechecklist',
            name='access_control_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pilotprerequisitechecklist',
            name='deletion_procedure_verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='pilotprerequisitechecklist',
            name='anti_ranking_validated',
            field=models.BooleanField(default=False),
        ),
        migrations.RemoveConstraint(
            model_name='pilottenantlifecycle',
            name='chk_pilot_lifecycle_state_valid',
        ),
        migrations.AddConstraint(
            model_name='pilottenantlifecycle',
            constraint=models.CheckConstraint(
                condition=models.Q(
                    ('state__in', [
                        'CANDIDATE',
                        'DUE_DILIGENCE',
                        'SECURITY_REVIEW',
                        'PRIVACY_REVIEW',
                        'OPERATIONAL_REVIEW',
                        'TECHNICAL_READY',
                        'MANAGER_DECISION_REQUIRED',
                        'MANAGER_AUTHORIZED',
                        'ACTIVATION_WINDOW',
                        'ACTIVE',
                        'SUSPENDED',
                        'EXITING',
                        'CLOSED',
                    ])
                ),
                name='chk_pilot_lifecycle_state_valid',
            ),
        ),
    ]
