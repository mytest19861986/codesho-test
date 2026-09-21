# ROLE_EXPERIENCE_MATRIX.md — CodeSho Role Experience Matrix

> **Wave 5.12 Phase 3 Deliverable**  
> **Status**: ROLE_MATRIX_CREATED ✅  
> **Hard Locks Enforced**: `CODE_CHANGE = 0`, `DATABASE_MIGRATION = 0`, `PRODUCTION_TOUCH = 0`, `UI_REFACTOR = FORBIDDEN`

---

## 1. Student Experience (`/student`)
```yaml
Role: Student
Primary Goal: Learning Journey Visibility & Personal Growth Ownership
Experience Principle: "Student Owns Growth Story — No Demotivating Ranking or Leaderboards"
Visible Components:
  - AppShell (Student Theme)
  - StudentCommandHero (Checklist + Milestone Banner)
  - GrowthCard (Weekly progress, personal record streak, competency gauges)
  - SkillMap (Visual mastery matrix)
  - PortfolioCard (Evidence, projects, achievements)
  - LearningTimeline (Completed tasks, upcoming milestones)
  - ReflectionPanel (Autonomous reflection & notes)
Hidden Components:
  - Administrative Controls / Tenant Settings
  - Mentor Private Assessment Notes
  - Cross-student Comparative Rank Lists
Theme: Student Light Purple (`#6d28d9` + soft lavender `#ede9fe` + growth mint `#10b981`)
Navigation Pattern: Learning First (Direct access to courses, tasks, and portfolio)
Mobile Behavior: Priority KPI cards stack vertically into a single-column fluid feed
Screenshot Reference: temp/audit_02_student_main_1440x900.png
```

---

## 2. Mentor Experience (`/mentor`)
```yaml
Role: Mentor
Primary Goal: Educational Guidance, Coaching & Facilitation
Experience Principle: "Guide Not Judge — Focus on Feedback, Evidence & Growth Potential"
Visible Components:
  - AppShell (Mentor Theme)
  - MentorWorkspace (Review queue, pending feedback list)
  - EvidenceTimeline (Student submission history & artifacts)
  - ReflectionPrompt (Structured coaching feedback inputs)
  - ProjectContextCard (Project specs & rubrics)
Hidden Components:
  - Parent Private Views & Communications
  - Student Private Introspective Reflection Notes
  - Global Financial & Tenant Billing Operations
Theme: Mentor Professional Deep Purple (`#581c87` + analytical slate `#475569`)
Navigation Pattern: Guidance First (Review queues, active cohorts, coaching slots)
Mobile Behavior: Compact review cards with clear call-to-action triggers
Screenshot Reference: temp/audit_06_mentor_panel_1440x900.png
```

---

## 3. Parent Experience (`/parent`)
```yaml
Role: Parent
Primary Goal: Understanding Growth Journey & Cultivating Encouragement
Experience Principle: "Support Without Comparison — Transparent, Reassuring, Accessible Telemetry"
Visible Components:
  - AppShell (Parent Theme)
  - GrowthNarrative (Plain-language growth storytelling)
  - AchievementStory (Completed projects, recognized milestones)
  - ConversationPrompt (Family dinner talking points based on weekly progress)
  - ParentIntelligenceView (Visual progress telemetry without overwhelming jargon)
Hidden Components:
  - Low-level Technical Logs / Git Commits
  - Raw Source Code Diff Viewers
  - Mentor Internal Evaluation Drafts
Theme: Parent Trust Soft Violet (`#7c3aed` + trust emerald `#059669` + soft neutral `#f8fafc`)
Navigation Pattern: Growth First (Child growth observatory, progress narrative, consent)
Mobile Behavior: Simplified story cards optimized for quick parent check-ins
Screenshot Reference: temp/audit_08_parent_observatory_1440x900.png
```

---

## 4. Admin Experience (`/admin`)
```yaml
Role: Admin
Primary Goal: Platform Governance, Tenant Isolation & Operational Stability
Experience Principle: "Operate Without Affecting Learning Identity — High Density & Control"
Visible Components:
  - AppShell (Admin Theme)
  - TenantHealth (Tenant isolation status & quota monitoring)
  - AuditExplorer (Immutable audit trails & governance logs)
  - GovernancePanel (Role-based access controls, tenant management)
Hidden Components:
  - Child Formative Learning Evaluations
  - Pedagogical Assessment Scoring
Theme: Admin Control Neutral (`#1e1b4b` + high-contrast governance amber `#d97706`)
Navigation Pattern: Operations First (Dashboard, Governance, Audit, Roles, System)
Mobile Behavior: Dense tabular data converts to scrollable containers with essential summary cards
Screenshot Reference: temp/audit_01_dashboard_admin_1440x900.png
```
