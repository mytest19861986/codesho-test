import type { LearningViewState } from "./learning.types";
import styles from "./learning.module.css";

const copy: Record<LearningViewState, string> = {
  loading: "در حال بارگذاری دوره‌ها و درس‌ها…", empty: "هیچ دوره منتشرشده‌ای در دسترس نیست.",
  "lessons-empty": "این دوره هنوز درسی برای نمایش ندارد.", ready: "",
  unauthenticated: "برای دیدن دوره‌ها وارد حساب کاربری شوید.", forbidden: "به این داده‌های یادگیری دسترسی ندارید.",
  "parent-not-found": "دوره درخواست‌شده پیدا نشد.", "invalid-request": "درخواست یادگیری نامعتبر است.",
  "recoverable-error": "سرویس موقتاً در دسترس نیست.", error: "بارگذاری داده‌های یادگیری انجام نشد.",
};

export function LearningState({ state }: { readonly state: LearningViewState }) {
  if (state === "loading" || state === "empty") return <section aria-live="polite" className={`${styles.state} ${state === "empty" ? styles.empty : ""}`} role="status"><span className={state === "loading" ? styles.spinner : undefined} aria-hidden="true">{state === "empty" ? "◌" : ""}</span><h2>{copy[state]}</h2></section>;
  if (state === "lessons-empty" || state === "ready") return null;
  if (state === "unauthenticated") return <section aria-live="assertive" className={styles.state} role="alert"><span aria-hidden="true">!</span><h2>{copy[state]}</h2><a href="/login">ورود</a></section>;
  if (state === "recoverable-error") return <section aria-live="assertive" className={styles.state} role="alert"><span aria-hidden="true">!</span><h2>{copy[state]}</h2><button type="button" onClick={() => window.location.reload()}>تلاش دوباره</button></section>;
  return <section aria-live="assertive" className={styles.state} role="alert"><span aria-hidden="true">!</span><h2>{copy[state]}</h2></section>;
}
