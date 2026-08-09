import type { DashboardViewState } from "./dashboard.types";
import styles from "./dashboard.module.css";

export function DashboardState({ state }: { state: Exclude<DashboardViewState, "ready"> }) {
  if (state === "loading") {
    return <div aria-label="در حال بارگذاری داشبورد" className={styles.stateGrid} role="status"><span /><span /><span /><span /></div>;
  }
  if (state === "empty") {
    return <section className={styles.stateCard}><span aria-hidden="true" className={styles.stateIcon}>✦</span><h2>مسیر یادگیری تو آماده می‌شود</h2><p>به‌زودی اولین کلاس و تمرینت اینجا نمایش داده می‌شود.</p></section>;
  }
  return <section className={styles.stateCard}><span aria-hidden="true" className={styles.stateIcon}>!</span><h2>اتصال داشبورد موقتاً برقرار نیست</h2><p>لطفاً دوباره تلاش کن. اطلاعات تو حذف نشده است.</p><button className={styles.inlineAction} type="button" onClick={() => window.location.reload()}>تلاش دوباره</button></section>;
}
