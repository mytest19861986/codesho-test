# P10 Scope Definition Template

## 1. Scope Parameter Specifications
This template defines the exact schema and boundary restrictions required for an authorized real pilot scope. Every field is mandatory.

```yaml
pilot_scope_definition:
  metadata:
    decision_reference: "MGR-GO-2026-XXXX"
    scope_version: "1.0.0"
    created_at_utc: "YYYY-MM-DDTHH:MM:SSZ"
  
  institutional_boundary:
    organization_name: "<EXACT_SCHOOL_NAME>"
    organization_id: "<UUID_V4>"
    domain_suffix: "<SCHOOL_DOMAIN_CODESHO_LOCAL>"
    maximum_organizations: 1  # Hard Invariant: Exactly 1
  
  user_cohort_limits:
    maximum_active_students: 50   # Maximum limit
    maximum_active_guardians: 50  # 1:1 or 1:2 guardian binding
    maximum_mentors: 5            # Dedicated staff mentors
    allow_anonymous_browsing: false # Hard Invariant: Denied
    allow_public_registration: false # Hard Invariant: Denied
  
  duration_and_schedule:
    start_timestamp_utc: "YYYY-MM-DDTHH:MM:SSZ"
    mandatory_review_timestamp_utc: "YYYY-MM-DDTHH:MM:SSZ"
    maximum_calendar_days: 14     # Hard Invariant: Max 14 days
  
  feature_whitelist:
    enabled_modules:
      - "STUDENT_COURSE_VIEW"
      - "EXERCISE_SUBMISSION"
      - "ATTENDANCE_CHECK"
      - "GUARDIAN_PROGRESS_MONITOR"
    disabled_modules:
      - "PAYMENT_AND_BILLING"     # Hard Invariant: Disabled
      - "PUBLIC_COMMUNITY_FORUM"  # Hard Invariant: Disabled
      - "LIVE_STREAMING_VIDEO"    # Hard Invariant: Disabled
  
  data_classification_boundaries:
    permitted_data_classes:
      - "EDUCATIONAL_METRICS"
      - "ACADEMIC_PROGRESS"
      - "FIRST_NAME_INITIALS"
    strictly_prohibited_data_classes:
      - "BIOMETRIC_DATA"
      - "NATIONAL_ID_CARD_IMAGES"
      - "FINANCIAL_PAYMENT_DATA"
      - "PRECISE_GEOLOCATION_GPS"

  operational_governance:
    pilot_program_lead: "<NAME_AND_ROLE>"
    incident_commander: "<NAME_AND_ROLE>"
    primary_kill_switch_holder: "<NAME_AND_ROLE>"
```
