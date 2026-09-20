from django.urls import path
from .views import (
    learning_loop_state_view,
    update_intervention_status_view,
    add_intervention_feedback_view,
    update_parent_briefing_view,
    send_parent_encouragement_view,
    submit_evidence_view,
)

urlpatterns = [
    path("state/", learning_loop_state_view, name="learning-loop-state"),
    path(
        "projects/<uuid:project_id>/evidence/",
        submit_evidence_view,
        name="learning-loop-submit-evidence",
    ),
    path(
        "interventions/<uuid:intervention_id>/status/",
        update_intervention_status_view,
        name="learning-loop-intervention-status",
    ),
    path(
        "interventions/<uuid:intervention_id>/feedbacks/",
        add_intervention_feedback_view,
        name="learning-loop-intervention-feedback",
    ),
    path(
        "parent-bridge/<uuid:learner_id>/briefing/",
        update_parent_briefing_view,
        name="learning-loop-parent-briefing",
    ),
    path(
        "parent-bridge/<uuid:learner_id>/encouragement/",
        send_parent_encouragement_view,
        name="learning-loop-parent-encouragement",
    ),
]
