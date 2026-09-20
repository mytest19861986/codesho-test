/**
 * Wave 5.7 Phase 5: Learning Intelligence Read Projection Types & Contracts.
 * Conforms 1-to-1 with Backend Intelligence Serializers:
 * - LearnerSkillGraphReadModelSerializer
 * - MentorIntelligenceDossierReadModelSerializer
 * - ParentInsightReadModelSerializer
 * - StudentReflectionEntrySerializer
 * 
 * Strict Invariant:
 * NO_JUDGMENT_ENGINE: Zero numeric rankings, zero scores, zero competitive stats.
 */

export interface SkillNode {
  slug: string;
  title: string;
  category: "core" | "resilience" | "advanced" | "architecture" | string;
  status: "DEMONSTRATED" | "IN_PROGRESS";
  prerequisites: string[];
}

export interface LearnerSkillGraphReadModel {
  learner_id: string;
  student_code: string;
  skills: SkillNode[];
}

export interface LearningFrictionSignal {
  signal_type: string;
  concept: string;
  suggested_mentor_action: string;
  is_active: boolean;
}

export interface MentorIntelligenceDossierReadModel {
  learner_id: string;
  student_code: string;
  display_name: string;
  pedagogical_summary: string[];
  evidence_trace: string[];
  suggested_socratic_prompts: string[];
  friction_signal?: LearningFrictionSignal | null;
}

export interface ParentInsightReadModel {
  learner_id: string;
  developmental_translation: string;
  home_support_cues: string[];
  technical_jargon_suppressed: boolean;
  last_briefing_at?: string | null;
}

export interface StudentReflectionEntry {
  reflection_id: string;
  milestone_slug: string;
  reflection_text: string;
  sentiment: string;
  created_at: string;
  status: string;
}

export interface UnifiedIntelligenceProjection {
  skill_graph?: LearnerSkillGraphReadModel | null;
  mentor_dossier?: MentorIntelligenceDossierReadModel | null;
  parent_insight?: ParentInsightReadModel | null;
  reflections?: StudentReflectionEntry[];
}
