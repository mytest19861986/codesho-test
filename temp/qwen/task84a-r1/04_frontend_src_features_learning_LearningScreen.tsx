import { Card } from "@/components/ui";
import { AppShell, type NavigationItem } from "@/components/layout";
import type { LearningModel, LearningViewState } from "./learning.types";
import styles from "./learning.module.css";
import { LearningState } from "./LearningState";

const navigationItems: NavigationItem[] = [{ id: "dashboard", label: "Dashboard", href: "/dashboard", icon: "⌂" }, { id: "learning", label: "Learning", href: "/learning", icon: "◈" }];
function Brand() { return <a className={styles.brand} href="/dashboard"><span aria-hidden="true">⌁</span><span>Codesho</span></a>; }

export function LearningScreen({ model, state, onSelectCourse }: { readonly model?: LearningModel; readonly state: LearningViewState; readonly onSelectCourse?: (courseId: string) => void }) {
  return <AppShell activeItemId="learning" brand={<Brand />} drawerCloseLabel="Close menu" menuButtonLabel="Open learning menu" bottomNavigationItems={navigationItems} navigationItems={navigationItems} navigationLabel="Learning navigation" tone="learner" profileSlot={<span aria-label="User account" className={styles.profile}>A</span>}>
    <main className={styles.page} dir="rtl"><header className={styles.hero}><p className={styles.eyebrow}>Learning space</p><h1>Project-based learning</h1><p>Browse published courses and lessons in one place.</p></header>
      <LearningState state={state} />
      {model && (state === "ready" || state === "lessons-empty") ? <section aria-labelledby="courses-title" className={styles.section}><div className={styles.heading}><div><p className={styles.eyebrow}>Courses</p><h2 id="courses-title">Published courses</h2></div><span className={styles.count}>{model.courses.length} courses</span></div><div className={styles.grid}>
        {model.courses.map((course) => { const selected = course.id === model.selectedCourseId; const lessonsId = `learning-lessons-${course.id}`; return <Card className={styles.card} key={course.id}><button type="button" aria-pressed={selected} aria-expanded={selected} aria-controls={lessonsId} onClick={() => onSelectCourse?.(course.id)}><strong>{course.title}</strong><span>{course.code}</span></button>{selected ? <div id={lessonsId} role="region" aria-label={`${course.title} lessons`}>{model.lessons.length > 0 ? <ul aria-label="درس‌های دوره" className={styles.lessons}>{model.lessons.map((lesson) => <li key={lesson.id}><span>{lesson.position}. {lesson.title}</span><small>{lesson.code}</small></li>)}</ul> : <p role="status" className={styles.muted}>This course has no published lessons yet.</p>}</div> : null}</Card>; })}
      </div></section> : null}
    </main>
  </AppShell>;
}
