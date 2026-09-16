import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge, Card, Progress } from "@/components/ui";
import styles from "./student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.dashboard.title}`,
  description: copy.dashboard.welcome,
};

export default function StudentDashboardPage() {
  const d = copy.dashboard;

  return (
    <div className={styles.studentDashboard}>
      <header className={styles.heroCard} aria-labelledby="dashboard-title">
        <div className={styles.heroHeader}>
          <h1 id="dashboard-title" className={styles.heroTitle}>
            {d.title}
          </h1>
          <Badge variant="primary">{copy.shell.roleLabel}</Badge>
        </div>
        <p className={styles.heroWelcome}>{d.welcome}</p>
      </header>

      <div className={styles.stateGrid}>
        <section className={styles.stateCard} aria-labelledby="current-state-heading">
          <h2 id="current-state-heading" className={styles.cardHeading}>
            {d.currentStateTitle}
          </h2>
          <div className={styles.badgeRow}>
            <Badge variant="info">{d.currentPathName}</Badge>
          </div>
          <p className={styles.cardText}>{d.currentModule}</p>
          <Progress
            value={d.progressValue}
            label={d.progressLabel}
          />
        </section>

        <section className={styles.stateCard} aria-labelledby="next-action-heading">
          <h2 id="next-action-heading" className={styles.cardHeading}>
            {d.nextActionTitle}
          </h2>
          <p className={styles.cardText}>{d.nextActionDesc}</p>
          <Link href="/student/learning" className={styles.actionButton}>
            {d.nextActionButton}
          </Link>
        </section>

        <section className={styles.stateCard} aria-labelledby="guidance-heading">
          <h2 id="guidance-heading" className={styles.cardHeading}>
            {d.guidanceTitle}
          </h2>
          <p className={styles.cardText}>{d.guidanceText}</p>
          <Link href="/student/coaching" className={`${styles.actionButton} ${styles.secondaryAction}`}>
            {copy.coaching.title}
          </Link>
        </section>
      </div>
    </div>
  );
}
