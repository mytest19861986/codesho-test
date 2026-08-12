import type { DashboardViewState } from "./dashboard.types";
import styles from "./dashboard.module.css";

const messages: Record<Exclude<DashboardViewState, "ready" | "loading">, string> = {
  empty: "هنوز دوره‌ای برای نمایش وجود ندارد.",
  "lessons-empty": "این دوره هنوز درسی برای نمایش ندارد.",
  unauthenticated: "برای دیدن دوره‌های خود وارد حساب کاربری شوید.",
  "parent-not-found": "این دوره دیگر در دسترس نیست.",
  forbidden: "دسترسی به این دوره ممکن نیست.",
  "invalid-request": "درخواست دوره معتبر نبود.",
  "recoverable-error": "اتصال موقتاً برقرار نشد. دوباره تلاش کنید.",
  "stale-session": "نشست شما تغییر کرده است. در حال به‌روزرسانی…",
  error: "اتصال داشبورد موقتاً برقرار نیست.",
};

export function DashboardState({ state }: { state: Exclude<DashboardViewState, "ready"> }) {
  if (state === "loading") {
    return <div aria-label="در حال بارگذاری داشبورد" className={styles.stateGrid} role="status"><span /><span /><span /><span /></div>;
  }
  return <section className={styles.stateCard} role="status"><span aria-hidden="true" className={styles.stateIcon}>!</span><h2>{messages[state]}</h2><button className={styles.inlineAction} type="button" onClick={() => window.location.reload()}>تلاش دوباره</button></section>;
}
