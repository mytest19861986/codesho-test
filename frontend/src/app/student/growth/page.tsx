import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.growth.title}`,
  description: copy.growth.description,
};

export default function StudentGrowthPage() {
  const g = copy.growth;
  const ic = copy.icons;

  return (
    <div className={styles.studentDashboard}>
      {/* Growth Hero Header */}
      <header className={styles.heroCard} aria-labelledby="growth-title">
        <div className={styles.heroHeader}>
          <h1 id="growth-title" className={styles.heroTitle}>
            {g.title}
          </h1>
          <Badge variant="success">{g.invariantBadge}</Badge>
        </div>
        <p className={styles.heroWelcome}>{g.description}</p>
        <p className={styles.cardText} style={{ color: "var(--cs-color-brand-primary)" }}>
          {g.selfSummaryText}
        </p>
      </header>

      <div className={styles.twoColumnGrid}>
        {/* Individual Mastery Skills Panel */}
        <section className={styles.cardPanel} aria-labelledby="skills-heading">
          <div className={styles.panelHeader}>
            <h2 id="skills-heading" className={styles.panelTitle}>
              <span aria-hidden="true">{ic.trending}</span>
              <span>{g.skillsTitle}</span>
            </h2>
          </div>
          <div className={styles.skillsList}>
            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{g.skill1}</span>
                <span>{g.skill1Rate}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "90%", background: "var(--cs-color-brand-primary)" }} />
              </div>
            </div>

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{g.skill2}</span>
                <span>{g.skill2Rate}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "85%", background: "var(--cs-color-success)" }} />
              </div>
            </div>

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{g.skill3}</span>
                <span>{g.skill3Rate}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "92%", background: "var(--cs-color-info)" }} />
              </div>
            </div>
          </div>
        </section>

        {/* Stable Milestones Panel */}
        <section className={styles.cardPanel} aria-labelledby="milestones-heading">
          <div className={styles.panelHeader}>
            <h2 id="milestones-heading" className={styles.panelTitle}>
              <span aria-hidden="true">{ic.flag}</span>
              <span>{g.milestoneTitle}</span>
            </h2>
          </div>
          <ul className={styles.listGroup}>
            <li className={styles.listItem} style={{ flexDirection: "column", alignItems: "stretch", gap: "0.25rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
                  {g.milestone1}
                </span>
                <Badge variant="success">{copy.indicators.check}</Badge>
              </div>
              <span className={styles.activityTime}>{g.milestone1Date}</span>
            </li>

            <li className={styles.listItem} style={{ flexDirection: "column", alignItems: "stretch", gap: "0.25rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
                  {g.milestone2}
                </span>
                <Badge variant="warning">{copy.indicators.bullet}</Badge>
              </div>
              <span className={styles.activityTime}>{g.milestone2Date}</span>
            </li>
          </ul>

          <div style={{ marginBlockStart: "var(--cs-space-4)" }}>
            <Link href="/student" className={`${styles.actionButton} ${styles.secondaryAction}`}>
              {copy.learning.actionContinue}
            </Link>
          </div>
        </section>
      </div>
    </div>
  );
}
