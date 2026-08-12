import { Card } from "@/components/ui";
import { AppShell, type NavigationItem } from "@/components/layout";

import { DashboardState } from "./DashboardState";
import type { DashboardModel, DashboardViewState } from "./dashboard.types";
import styles from "./dashboard.module.css";

const navigationItems: NavigationItem[] = [{ id: "dashboard", label: "داشبورد", href: "/dashboard", icon: "⌂" }, { id: "learning", label: "یادگیری", href: "/dashboard", icon: "◈" }];
function Brand() { return <a className={styles.brand} href="/dashboard"><span aria-hidden="true">⌁</span><span>کُدشو</span></a>; }

export function DashboardScreen({ model, state }: { readonly model?: DashboardModel; readonly state: DashboardViewState }) {
  const courses = model?.learning.courses ?? [];
  const lessons = model?.learning.lessons ?? [];
  return <AppShell activeItemId="dashboard" brand={<Brand />} drawerCloseLabel="بستن منو" menuButtonLabel="باز کردن منوی داشبورد" bottomNavigationItems={navigationItems} navigationItems={navigationItems} navigationLabel="ناوبری داشبورد" tone="learner" profileSlot={<span aria-label="حساب کاربری" className={styles.profile}>آ</span>}><main className={styles.page} dir="rtl">{state !== "ready" || model === undefined ? <DashboardState state={state as Exclude<DashboardViewState, "ready">} /> : <><section aria-labelledby="dashboard-greeting" className={styles.hero}><div><p className={styles.eyebrow}>فضای یادگیری تو</p><h1 id="dashboard-greeting">سلام {model.student.displayName}</h1><p className={styles.heroMeta}>دوره‌ها و درس‌های منتشرشده</p></div></section><section aria-labelledby="courses-title" className={styles.section}><div className={styles.sectionHeading}><div><p className={styles.eyebrow}>یادگیری</p><h2 id="courses-title">دوره‌های من</h2></div></div><div className={styles.primaryGrid}>{courses.map((course) => <Card className={styles.card} key={course.id}><h3>{course.title}</h3><p className={styles.muted}>{course.code}</p>{course.id === model.learning.selectedCourseId && <ul aria-label="درس‌های دوره" className={styles.lessonList}>{lessons.map((item) => <li key={item.id}><span>{item.position}. {item.title}</span><small>{item.code}</small></li>)}</ul>}</Card>)}</div></section></>}</main></AppShell>;
}
