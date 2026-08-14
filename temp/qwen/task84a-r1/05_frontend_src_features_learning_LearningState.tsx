import type { LearningViewState } from "./learning.types";
import styles from "./learning.module.css";

const copy: Record<LearningViewState, string> = {
  loading: "Loading courses and lessons…", empty: "No published courses are available.",
  "lessons-empty": "This course has no published lessons yet.", ready: "",
  unauthenticated: "Sign in to view your courses.", forbidden: "You do not have access to this learning data.",
  "parent-not-found": "The requested course was not found.", "invalid-request": "The learning request was invalid.",
  "recoverable-error": "The service is temporarily unavailable.", error: "We could not load the learning data.",
};

export function LearningState({ state }: { readonly state: LearningViewState }) {
  if (state === "loading" || state === "empty") return <section aria-live="polite" className={`${styles.state} ${state === "empty" ? styles.empty : ""}`} role="status"><span className={state === "loading" ? styles.spinner : undefined} aria-hidden="true">{state === "empty" ? "○" : ""}</span><h2>{copy[state]}</h2></section>;
  if (state === "lessons-empty" || state === "ready") return null;
  if (state === "unauthenticated") return <section aria-live="assertive" className={styles.state} role="alert"><span aria-hidden="true">!</span><h2>{copy[state]}</h2><a href="/login">Sign in</a></section>;
  if (state === "recoverable-error") return <section aria-live="assertive" className={styles.state} role="alert"><span aria-hidden="true">!</span><h2>{copy[state]}</h2><button type="button" onClick={() => window.location.reload()}>Retry</button></section>;
  return <section aria-live="assertive" className={styles.state} role="alert"><span aria-hidden="true">!</span><h2>{copy[state]}</h2></section>;
}
