import { Card } from "@/components/ui";
import { AppShell, type NavigationItem } from "@/components/layout";
import type { LearningModel, LearningViewState } from "./learning.types";
import styles from "./learning.module.css";
import { LearningState } from "./LearningState";

const navigationItems: NavigationItem[] = [{ id: "dashboard", label: "داشبورد", href: "/dashboard", icon: "⌂" }, { id: "learning", label: "یادگیری", href: "/learning", icon: "◈" }];
function Brand() { return <a className={styles.brand} href="/dashboard"><span aria-hidden="true">⌁</span><span>کُدشو</span></a>; }

export function LearningScreen({ model, state, onSelectCourse }: { readonly model?: LearningModel; readonly state: LearningViewState; readonly onSelectCourse?: (courseId: string) => void }) {
  return <AppShell activeItemId="learning" brand={<Brand />} drawerCloseLabel="بستن منو" menuButtonLabel="باز کردن منوی یادگیری" bottomNavigationItems={navigationItems} navigationItems={navigationItems} navigationLabel="ناوبری یادگیری" tone="learner" profileSlot={<span aria-label="حساب کاربری" className={styles.profile}>آ</span>}>
    <main className={styles.page} dir="rtl"><header className={styles.hero}><p className={styles.eyebrow}>فضای یادگیری</p><h1>یادگیری پروژه‌محور</h1><p>دوره‌ها و درس‌های منتشرشده را یک‌جا ببینید.</p></header>
      <LearningState state={state} />
      {model && (state === "ready" || state === "lessons-empty") ? <section aria-labelledby="courses-title" className={styles.section}><div className={styles.heading}><div><p className={styles.eyebrow}>یادگیری</p><h2 id="courses-title">دوره‌های منتشرشده</h2></div><span className={styles.count}>{model.courses.length} دوره</span></div><div className={styles.grid}>
        {model.courses.map((course) => { const selected = course.id === model.selectedCourseId; const lessonsId = `learning-lessons-${course.id}`; return <Card className={styles.card} key={course.id}><button type="button" aria-expanded={selected} {...(selected ? { "aria-controls": lessonsId } : {})} onClick={() => onSelectCourse?.(course.id)}><strong>{course.title}</strong><span>{course.code}</span></button>{selected ? <div id={lessonsId} role="region" aria-label={`${course.title} درس‌ها`}>{model.lessons.length > 0 ? <ul aria-label="درس‌های دوره" className={styles.lessons}>{model.lessons.map((lesson) => <li key={lesson.id}><span>{lesson.position}. {lesson.title}</span><small>{lesson.code}</small></li>)}</ul> : <p role="status" className={styles.muted}>این دوره هنوز درسی برای نمایش ندارد.</p>}</div> : null}</Card>; })}
      </div></section> : null}
    </main>
  </AppShell>;
}
