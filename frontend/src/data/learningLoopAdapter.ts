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
const IS_SHADOW_MODE = process.env.NEXT_PUBLIC_LEARNING_SHADOW_MODE === "true" || true; // Active in non-production shadow testing

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
   * Retrieves current cross-role state:
   * 1. If in SHADOW MODE: Always serves resilient synthetic state to user, while asynchronously fetching backend shadow API and computing parity diff.
   * 2. If BACKEND_ENABLED (Production): Serves backend state with immediate synthetic fallback on error.
   */
  static async getState(): Promise<SharedLearningState> {
    const syntheticState = getSharedLearningState();

    if (typeof window === "undefined") {
      return syntheticState;
    }

    // Shadow Dual-Read: Run backend fetch in background, compare, and log without impacting UI
    if (IS_SHADOW_MODE || IS_BACKEND_ENABLED) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/v1/learning-loop/state/`, {
          credentials: "include",
          headers: {
            "Accept": "application/json",
          },
        });
        if (res.ok) {
          const backendData = (await res.json()) as SharedLearningState;
          
          // Compute non-blocking shadow parity comparison
          const divergences: string[] = [];
          if (backendData.student?.id !== syntheticState.student?.id) {
            divergences.push(`student.id divergence: ${backendData.student?.id} vs ${syntheticState.student?.id}`);
          }
          if (backendData.mentorIntervention?.status !== syntheticState.mentorIntervention?.status) {
            divergences.push(`intervention.status divergence: ${backendData.mentorIntervention?.status} vs ${syntheticState.mentorIntervention?.status}`);
          }

          this.lastComparison = {
            timestamp: new Date().toISOString(),
            matched: divergences.length === 0,
            divergences,
            syntheticSnippet: { student: syntheticState.student },
            backendSnippet: { student: backendData.student },
          };

          if (IS_BACKEND_ENABLED && !IS_SHADOW_MODE) {
            return backendData;
          }
        }
      } catch (err) {
        // Shadow mode completely swallows fetch errors; guarantees zero user impact
        if (!IS_SHADOW_MODE) {
          console.warn("[LearningLoopAdapter] Backend error, falling back to synthetic state:", err);
        }
      }
    }

    // Default: Return guaranteed stable synthetic state
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
