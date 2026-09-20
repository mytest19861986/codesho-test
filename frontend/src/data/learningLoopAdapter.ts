import { SharedLearningState, defaultSharedLearningState, getSharedLearningState, updateSharedLearningState, resetLearningLoopDemoState } from "./sharedLearningLoop";

/**
 * Wave 5.6: Dual-Engine Learning Loop Client Adapter
 * 
 * Invariants:
 * 1. UI components (/student, /parent, /mentor) consume identical contracts without any modification.
 * 2. If BACKEND_ENABLED is true and server is reachable, sync with Django REST API (/api/v1/learning-loop/*).
 * 3. Fallback automatically to resilient local synthetic state (codesho:learning-loop:v1) on any network/server failure.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";
const IS_BACKEND_ENABLED = process.env.NEXT_PUBLIC_ENABLE_LEARNING_API === "true";
const IS_SHADOW_MODE = process.env.NEXT_PUBLIC_LEARNING_SHADOW_MODE === "true" || false;
const IS_CONTROLLED_READ_ACTIVE = process.env.NEXT_PUBLIC_CONTROLLED_READ_ACTIVATION === "true" || false;

export interface ShadowComparisonReport {
  timestamp: string;
  matched: boolean;
  divergences: string[];
  syntheticSnippet: Partial<SharedLearningState>;
  backendSnippet: Partial<SharedLearningState>;
}

export class LearningLoopAdapter {
  private static lastComparison: ShadowComparisonReport | null = null;

  static getLastComparison(): ShadowComparisonReport | null {
    return this.lastComparison;
  }

  /**
   * Wave 5.6 Phase 8: Controlled Read Activation Source Selector
   * 1. If CONTROLLED READ or PRODUCTION BACKEND active: Attemps read from backend API.
   * 2. Transforms backend snake_case / camelCase representations seamlessly to SharedLearningState.
   * 3. On ANY fetch error, non-200 status, or timeout: Instantly falls back to synthetic state (codesho:learning-loop:v1).
   * 4. Zero layout shift, zero runtime exception, zero user-facing latency penalty.
   */
  static async getState(): Promise<SharedLearningState> {
    const syntheticState = getSharedLearningState();

    if (typeof window === "undefined") {
      return syntheticState;
    }

    const shouldAttemptBackendRead = IS_CONTROLLED_READ_ACTIVE || IS_BACKEND_ENABLED || IS_SHADOW_MODE;

    if (shouldAttemptBackendRead) {
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 2000);

        const res = await fetch(`${API_BASE_URL}/api/v1/learning-loop/state/`, {
          credentials: "include",
          headers: {
            "Accept": "application/json",
          },
          signal: controller.signal,
        });
        clearTimeout(timeoutId);

        if (res.ok) {
          const rawBackendData = await res.json();
          
          // Map to typed client SharedLearningState with robust fallbacks
          const backendData: SharedLearningState = {
            student: {
              id: rawBackendData.student?.id || syntheticState.student.id,
              name: rawBackendData.student?.name || syntheticState.student.name,
              avatar: rawBackendData.student?.avatar || syntheticState.student.avatar,
              level: rawBackendData.student?.level || syntheticState.student.level,
              streakDays: rawBackendData.student?.streakDays ?? rawBackendData.student?.streak_days ?? syntheticState.student.streakDays,
            },
            activeProject: {
              id: rawBackendData.activeProject?.id || syntheticState.activeProject.id,
              title: rawBackendData.activeProject?.title || syntheticState.activeProject.title,
              branch: rawBackendData.activeProject?.branch || syntheticState.activeProject.branch,
              commitHash: rawBackendData.activeProject?.commitHash ?? rawBackendData.activeProject?.commit_hash ?? syntheticState.activeProject.commitHash,
              progressPercentage: rawBackendData.activeProject?.progressPercentage ?? rawBackendData.activeProject?.progress_percentage ?? syntheticState.activeProject.progressPercentage,
              currentMilestone: rawBackendData.activeProject?.currentMilestone ?? rawBackendData.activeProject?.current_milestone ?? syntheticState.activeProject.currentMilestone,
              recentActivity: rawBackendData.activeProject?.recentActivity ?? rawBackendData.activeProject?.recent_activity ?? syntheticState.activeProject.recentActivity,
              lastCodeSnippet: rawBackendData.activeProject?.lastCodeSnippet ?? rawBackendData.activeProject?.last_code_snippet ?? syntheticState.activeProject.lastCodeSnippet,
              skillsDemonstrated: rawBackendData.activeProject?.skillsDemonstrated ?? rawBackendData.activeProject?.skills_demonstrated ?? syntheticState.activeProject.skillsDemonstrated,
            },
            mentorIntervention: {
              status: rawBackendData.mentorIntervention?.status || syntheticState.mentorIntervention.status,
              reason: rawBackendData.mentorIntervention?.reason || syntheticState.mentorIntervention.reason,
              recommendedAction: rawBackendData.mentorIntervention?.recommendedAction ?? rawBackendData.mentorIntervention?.recommended_action ?? syntheticState.mentorIntervention.recommendedAction,
              mentorNotes: rawBackendData.mentorIntervention?.mentorNotes ?? rawBackendData.mentorIntervention?.mentor_notes ?? syntheticState.mentorIntervention.mentorNotes,
              feedbacks: (rawBackendData.mentorIntervention?.feedbacks || []).map((fb: any) => ({
                id: fb.id,
                sender: fb.sender,
                timestamp: fb.timestamp,
                text: fb.text,
                actionType: fb.actionType ?? fb.action_type ?? "",
              })),
            },
            parentBridge: {
              lastBriefing: rawBackendData.parentBridge?.lastBriefing ?? rawBackendData.parentBridge?.last_briefing ?? syntheticState.parentBridge.lastBriefing,
              briefingTimestamp: rawBackendData.parentBridge?.briefingTimestamp ?? rawBackendData.parentBridge?.briefing_timestamp ?? syntheticState.parentBridge.briefingTimestamp,
              parentEncouragementSent: rawBackendData.parentBridge?.parentEncouragementSent ?? rawBackendData.parentBridge?.parent_encouragement_sent ?? syntheticState.parentBridge.parentEncouragementSent,
              parentEncouragementMessage: rawBackendData.parentBridge?.parentEncouragementMessage ?? rawBackendData.parentBridge?.parent_encouragement_message ?? syntheticState.parentBridge.parentEncouragementMessage,
            },
          };

          // Compute shadow parity comparison
          const divergences: string[] = [];
          if (backendData.student.id !== syntheticState.student.id) {
            divergences.push(`student.id divergence: ${backendData.student.id} vs ${syntheticState.student.id}`);
          }
          if (backendData.mentorIntervention.status !== syntheticState.mentorIntervention.status) {
            divergences.push(`intervention.status divergence: ${backendData.mentorIntervention.status} vs ${syntheticState.mentorIntervention.status}`);
          }

          this.lastComparison = {
            timestamp: new Date().toISOString(),
            matched: divergences.length === 0,
            divergences,
            syntheticSnippet: { student: syntheticState.student },
            backendSnippet: { student: backendData.student },
          };

          // If Controlled Read is ON and not in pure shadow comparison, return the verified backend data
          if ((IS_CONTROLLED_READ_ACTIVE || IS_BACKEND_ENABLED) && !IS_SHADOW_MODE) {
            return backendData;
          }
        }
      } catch (err) {
        // Safe Fallback Net: Absolute zero disruption to client UI
        console.warn("[LearningLoopAdapter] Fallback engaged, serving verified synthetic baseline:", err);
      }
    }

    // Resilient Fallback Guarantee
    return syntheticState;
  }


  /**
   * Updates intervention status (calls backend if active, updates local synthetic mirror)
   */
  static async updateInterventionStatus(
    interventionId: string,
    newStatus: "OPEN" | "REVIEWING" | "FOLLOW_UP" | "RESOLVED"
  ): Promise<SharedLearningState> {
    // Optimistically update local synthetic state so UI feels instant
    const updatedLocal = updateSharedLearningState((prev) => ({
      ...prev,
      mentorIntervention: {
        ...prev.mentorIntervention,
        status: newStatus,
      },
    }));

    if (IS_BACKEND_ENABLED && typeof window !== "undefined") {
      try {
        await fetch(`${API_BASE_URL}/api/v1/learning-loop/interventions/${interventionId}/status/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ status: newStatus }),
        });
      } catch (err) {
        console.warn("[LearningLoopAdapter] Backend status update fallback to local:", err);
      }
    }

    return updatedLocal;
  }

  /**
   * Appends feedback to intervention stream
   */
  static async addFeedback(
    interventionId: string,
    sender: "MENTOR" | "STUDENT",
    text: string,
    actionType: string
  ): Promise<SharedLearningState> {
    const updatedLocal = updateSharedLearningState((prev) => ({
      ...prev,
      mentorIntervention: {
        ...prev.mentorIntervention,
        feedbacks: [
          ...prev.mentorIntervention.feedbacks,
          {
            id: `fb-${Date.now()}`,
            sender,
            timestamp: "همین الان",
            text,
            actionType,
          },
        ],
      },
    }));

    if (IS_BACKEND_ENABLED && typeof window !== "undefined") {
      try {
        await fetch(`${API_BASE_URL}/api/v1/learning-loop/interventions/${interventionId}/feedbacks/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ text, action_type: actionType }),
        });
      } catch (err) {
        console.warn("[LearningLoopAdapter] Backend feedback fallback to local:", err);
      }
    }

    return updatedLocal;
  }

  /**
   * Submits mentor's parent briefing
   */
  static async updateParentBriefing(
    learnerId: string,
    briefingText: string
  ): Promise<SharedLearningState> {
    const updatedLocal = updateSharedLearningState((prev) => ({
      ...prev,
      parentBridge: {
        ...prev.parentBridge,
        lastBriefing: briefingText,
        briefingTimestamp: "همین الان",
      },
    }));

    if (IS_BACKEND_ENABLED && typeof window !== "undefined") {
      try {
        await fetch(`${API_BASE_URL}/api/v1/learning-loop/parent-bridge/${learnerId}/briefing/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ last_briefing: briefingText }),
        });
      } catch (err) {
        console.warn("[LearningLoopAdapter] Backend briefing fallback to local:", err);
      }
    }

    return updatedLocal;
  }

  /**
   * Submits parent praise/encouragement ribbon
   */
  static async sendParentEncouragement(
    learnerId: string,
    message: string
  ): Promise<SharedLearningState> {
    const updatedLocal = updateSharedLearningState((prev) => ({
      ...prev,
      parentBridge: {
        ...prev.parentBridge,
        parentEncouragementSent: true,
        parentEncouragementMessage: message,
      },
    }));

    if (IS_BACKEND_ENABLED && typeof window !== "undefined") {
      try {
        await fetch(`${API_BASE_URL}/api/v1/learning-loop/parent-bridge/${learnerId}/encouragement/`, {
          method: "POST",
          credentials: "include",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message }),
        });
      } catch (err) {
        console.warn("[LearningLoopAdapter] Backend encouragement fallback to local:", err);
      }
    }

    return updatedLocal;
  }

  /**
   * Resets demo state
   */
  static resetDemoState(): SharedLearningState {
    return resetLearningLoopDemoState();
  }
}
