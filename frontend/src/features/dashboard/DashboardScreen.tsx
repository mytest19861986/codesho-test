import { Badge, Button, Card, Progress } from "@/components/ui";
import { AppShell, type NavigationItem } from "@/components/layout";

import { dashboardFixture } from "./dashboard.fixture";
import { DashboardState } from "./DashboardState";
import type { DashboardModel, DashboardViewState } from "./dashboard.types";
import styles from "./dashboard.module.css";

const navigationItems: NavigationItem[] = [
  { id: "dashboard", label: "داشبورد", href: "/dashboard", icon: "⌂" },
  { id: "learning", label: "یادگیری", href: "/dashboard", icon: "◈" },
  { id: "assignments", label: "تمرین‌ها", href: "/dashboard", icon: "✓" },
  { id: "calendar", label: "تقویم", href: "/dashboard", icon: "◷" },
];

function Brand() { return <a className={styles.brand} href="/dashboard"><span aria-hidden="true">⌁</span><span>کُدشو</span></a>; }

function DashboardContent({ model, state }: { model: DashboardModel; state: DashboardViewState }) {
  if (state !== "ready") return <DashboardState state={state} />;
  return <>
    <section aria-labelledby="dashboard-greeting" className={styles.hero}>
      <div><p className={styles.eyebrow}>فضای یادگیری تو</p><h1 id="dashboard-greeting">سلام {model.student.displayName}، {model.student.greeting}</h1><p className={styles.heroMeta}>{model.student.className}</p></div>
      <div aria-hidden="true" className={styles.heroOrb}>✦</div>
    </section>
    <div className={styles.primaryGrid}>
      <Card className={`${styles.card} ${styles.learningCard}`}>
        <div className={styles.cardHeader}><div><p className={styles.eyebrow}>ادامه یادگیری</p><h2>{model.learning.course}</h2></div><Badge variant="info">ماژول فعال</Badge></div>
        <p className={styles.muted}>{model.learning.module} · {model.learning.lesson}</p><Progress label={`پیشرفت دوره، ${model.learning.progress} درصد`} value={model.learning.progress} /><div className={styles.progressMeta}><span>{model.learning.completedUnits.toLocaleString("fa-IR")} از {model.learning.totalUnits.toLocaleString("fa-IR")} واحد</span><strong>{model.learning.progress.toLocaleString("fa-IR")}%</strong></div><Button disabled aria-label="ادامه درس؛ با اتصال قرارداد داده فعال می‌شود" title="با اتصال قرارداد داده فعال می‌شود">ادامه درس</Button>
      </Card>
      <Card className={styles.card}><div className={styles.cardHeader}><div><p className={styles.eyebrow}>جلسه بعدی</p><h2>{model.nextSession.title}</h2></div><Badge variant="success">{model.nextSession.status}</Badge></div><p className={styles.sessionDate}>{model.nextSession.date} · {model.nextSession.time}</p><p className={styles.muted}>{model.nextSession.type}</p><Button disabled aria-label="مشاهده جزئیات؛ با اتصال قرارداد داده فعال می‌شود" variant="outline" title="با اتصال قرارداد داده فعال می‌شود">مشاهده جزئیات</Button></Card>
    </div>
    <section aria-labelledby="momentum-title" className={styles.section}><div className={styles.sectionHeading}><div><p className={styles.eyebrow}>ریتم تو</p><h2 id="momentum-title">با همین استمرار ادامه بده</h2></div><span aria-hidden="true" className={styles.sectionMark}>↗</span></div><div className={styles.momentumGrid}><Card className={styles.statCard}><span>امتیاز تجربه</span><strong>{model.momentum.xp.toLocaleString("fa-IR")}</strong><small>XP</small></Card><Card className={styles.statCard}><span>رتبه فعلی</span><strong>{model.momentum.rank}</strong><small>در مسیر رشد</small></Card><Card className={styles.statCard}><span>زنجیره تمرین</span><strong>{model.momentum.streak}</strong><small>روز پشت سر هم</small></Card></div></section>
    <div className={styles.secondaryGrid}><Card className={styles.card}><div className={styles.cardHeader}><div><p className={styles.eyebrow}>تمرین نزدیک</p><h2>{model.assignment.title}</h2></div><Badge variant="warning">{model.assignment.status}</Badge></div><p className={styles.muted}>{model.assignment.dueLabel}</p><Button disabled aria-label={`${model.assignment.actionLabel}؛ با اتصال قرارداد داده فعال می‌شود`} variant="secondary" title="با اتصال قرارداد داده فعال می‌شود">{model.assignment.actionLabel}</Button></Card><Card className={styles.card}><div className={styles.cardHeader}><div><p className={styles.eyebrow}>پیشنهاد بعدی</p><h2>{model.recommendation.title}</h2></div><span aria-hidden="true" className={styles.recommendationIcon}>✧</span></div><p className={styles.muted}>{model.recommendation.reason}</p><span className={styles.textAction} role="status">شروع چالش ←</span></Card></div>
    <section aria-labelledby="attention-title" className={styles.attention}><div><p className={styles.eyebrow}>خلاصه توجه</p><h2 id="attention-title">چیزهایی که ارزش دیدن دارند</h2></div><ul>{model.attention.map((item) => <li key={item}><span aria-hidden="true">•</span>{item}</li>)}</ul></section>
  </>;
}

export function DashboardScreen({ model = dashboardFixture, state = "ready" }: { model?: DashboardModel; state?: DashboardViewState }) {
  return <AppShell activeItemId="dashboard" brand={<Brand />} drawerCloseLabel="بستن منو" menuButtonLabel="باز کردن منوی داشبورد" bottomNavigationItems={navigationItems} navigationItems={navigationItems} navigationLabel="ناوبری داشبورد" tone="learner" profileSlot={<span aria-label="حساب کاربری آ" className={styles.profile}>آ</span>}><div className={styles.page}><DashboardContent model={model} state={state} /></div></AppShell>;
}
