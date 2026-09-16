import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge, Progress } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.learning.title}`,
  description: copy.learning.description,
};

export default function StudentLearningPage() {
  const l = copy.learning;
  const ic = copy.icons;

  return (
    <div className={styles.studentDashboard}>
      {/* Learning Hero Section */}
      <header className={styles.heroCard} aria-labelledby="learning-title">
        <div className={styles.heroHeader}>
          <h1 id="learning-title" className={styles.heroTitle}>
            {l.title}
          </h1>
          <Badge variant="primary">{l.currentPath}</Badge>
        </div>
        <p className={styles.heroWelcome}>{l.description}</p>
        <div style={{ marginBlockStart: "var(--cs-space-3)" }}>
          <Progress value={68} label={l.progressRatio} />
        </div>
      </header>

      {/* Modules Roadmap Grid */}
      <section className={styles.cardPanel} aria-labelledby="modules-title">
        <div className={styles.panelHeader}>
          <h2 id="modules-title" className={styles.panelTitle}>
            <span aria-hidden="true">{ic.map}</span>
            <span>{l.roadmapHeader}</span>
          </h2>
          <span className={styles.panelFilter}>{l.progressRatio}</span>
        </div>

        <ul className={styles.listGroup}>
          <li className={styles.listItem} style={{ flexDirection: "column", alignItems: "stretch", gap: "var(--cs-space-2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
                {l.module1Title}
              </span>
              <Badge variant="success">{l.module1Status}</Badge>
            </div>
            <span className={styles.activityTime}>{l.module1Time}</span>
            <div className={styles.skillBarBackground}>
              <div className={styles.skillBarFill} style={{ inlineSize: "100%", background: "var(--cs-color-success)" }} />
            </div>
          </li>

          <li className={styles.listItem} style={{ flexDirection: "column", alignItems: "stretch", gap: "var(--cs-space-2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
                {l.module2Title}
              </span>
              <Badge variant="warning">{l.module2Status}</Badge>
            </div>
            <span className={styles.activityTime}>{l.module2Time}</span>
            <div className={styles.skillBarBackground}>
              <div className={styles.skillBarFill} style={{ inlineSize: "65%", background: "var(--cs-color-warning)" }} />
            </div>
          </li>

          <li className={styles.listItem} style={{ flexDirection: "column", alignItems: "stretch", gap: "var(--cs-space-2)" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
                {l.module3Title}
              </span>
              <Badge variant="info">{l.module3Status}</Badge>
            </div>
            <span className={styles.activityTime}>{l.module3Time}</span>
            <div className={styles.skillBarBackground}>
              <div className={styles.skillBarFill} style={{ inlineSize: "0%", background: "var(--cs-color-border-subtle)" }} />
            </div>
          </li>
        </ul>

        <div style={{ marginBlockStart: "var(--cs-space-4)", display: "flex", gap: "var(--cs-space-3)" }}>
          <Link href="/student" className={styles.actionButton}>
            {l.actionContinue}
          </Link>
          <Link href="/student/coaching" className={`${styles.actionButton} ${styles.secondaryAction}`}>
            {copy.coaching.title}
          </Link>
        </div>
      </section>
    </div>
  );
}
