import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.portfolio.title}`,
  description: copy.portfolio.description,
};

export default function StudentPortfolioPage() {
  const p = copy.portfolio;

  return (
    <div className={styles.studentDashboard}>
      <header className={styles.heroCard} aria-labelledby="portfolio-title">
        <h1 id="portfolio-title" className={styles.heroTitle}>
          {p.title}
        </h1>
        <p className={styles.heroWelcome}>{p.description}</p>
        <p className={styles.cardText} style={{ color: "var(--cs-color-text-muted)" }}>
          {p.privacyNote}
        </p>
      </header>

      <section className={styles.stateCard} aria-labelledby="projects-title">
        <h2 id="projects-title" className={styles.cardHeading}>
          {copy.dashboard.activeLearningTitle}
        </h2>
        <div className={styles.listItem}>
          <div>
            <p className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
              {p.project1Title}
            </p>
            <Badge variant="success">{p.project1Status}</Badge>
          </div>
          <div className={styles.badgeRow}>
            <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
              {p.actionView}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
