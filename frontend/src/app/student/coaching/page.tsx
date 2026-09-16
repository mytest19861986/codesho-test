import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.coaching.title}`,
  description: copy.coaching.description,
};

export default function StudentCoachingPage() {
  const c = copy.coaching;
  const ic = copy.icons;

  return (
    <div className={styles.studentDashboard}>
      {/* Coaching Hero Banner */}
      <header className={styles.heroCard} aria-labelledby="coaching-title">
        <div className={styles.heroHeader}>
          <h1 id="coaching-title" className={styles.heroTitle}>
            {c.title}
          </h1>
          <Badge variant="info">{c.sourceLabel}</Badge>
        </div>
        <p className={styles.heroWelcome}>{c.description}</p>
      </header>

      <div className={styles.twoColumnGrid}>
        {/* Latest Advice & Guidance Card */}
        <section className={styles.cardPanel} aria-labelledby="advice-title">
          <div className={styles.panelHeader}>
            <h2 id="advice-title" className={styles.panelTitle}>
              <span aria-hidden="true">{ic.lightbulb}</span>
              <span>{c.adviceTitle}</span>
            </h2>
          </div>
          <p className={styles.cardText} style={{ lineHeight: "var(--cs-line-height-relaxed)" }}>
            {c.adviceText}
          </p>

          <div style={{ marginBlockStart: "var(--cs-space-4)" }}>
            <Link href="/student" className={styles.actionButton}>
              {c.actionPrompt}
            </Link>
          </div>
        </section>

        {/* Recommended Questions & History */}
        <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-4)" }}>
          <section className={styles.cardPanel} aria-labelledby="rec-questions-title">
            <div className={styles.panelHeader}>
              <h2 id="rec-questions-title" className={styles.panelTitle}>
                <span aria-hidden="true">{ic.question}</span>
                <span>{c.recommendedQuestionsTitle}</span>
              </h2>
            </div>
            <ul className={styles.listGroup}>
              <li className={styles.listItem}>
                <span className={styles.recTitle}>{c.q1}</span>
              </li>
              <li className={styles.listItem}>
                <span className={styles.recTitle}>{c.q2}</span>
              </li>
              <li className={styles.listItem}>
                <span className={styles.recTitle}>{c.q3}</span>
              </li>
            </ul>
          </section>

          <section className={styles.cardPanel} aria-labelledby="history-title">
            <div className={styles.panelHeader}>
              <h2 id="history-title" className={styles.panelTitle}>
                <span aria-hidden="true">{ic.history}</span>
                <span>{c.historyTitle}</span>
              </h2>
              <span className={styles.activityTime}>{c.h1Date}</span>
            </div>
            <p className={styles.activityDesc}>{c.h1Content}</p>
          </section>
        </div>
      </div>
    </div>
  );
}
