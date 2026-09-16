import type { Metadata } from "next";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import { Badge } from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.portfolio.title}`,
  description: copy.portfolio.description,
};

export default function StudentPortfolioPage() {
  const p = copy.portfolio;
  const ic = copy.icons;

  return (
    <div className={styles.studentDashboard}>
      {/* Portfolio Header with Tenant Privacy Note */}
      <header className={styles.heroCard} aria-labelledby="portfolio-title">
        <div className={styles.heroHeader}>
          <h1 id="portfolio-title" className={styles.heroTitle}>
            {p.title}
          </h1>
          <Badge variant="info">{p.privacyBadge}</Badge>
        </div>
        <p className={styles.heroWelcome}>{p.description}</p>
        <p className={styles.cardText} style={{ color: "var(--cs-color-text-muted)" }}>
          {p.privacyNote}
        </p>
      </header>

      {/* Projects Showcase Grid */}
      <div className={styles.twoColumnGrid}>
        {/* Project Card 1 */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.laptop}</span>
              <span>{p.project1Title}</span>
            </h2>
            <Badge variant="success">{p.project1Status}</Badge>
          </div>
          <span className={styles.activityTime}>{p.project1Tags}</span>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
              {p.actionView}
            </button>
          </div>
        </div>

        {/* Project Card 2 */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.gear}</span>
              <span>{p.project2Title}</span>
            </h2>
            <Badge variant="warning">{p.project2Status}</Badge>
          </div>
          <span className={styles.activityTime}>{p.project2Tags}</span>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
              {p.actionView}
            </button>
          </div>
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "center", marginBlockStart: "var(--cs-space-4)" }}>
        <button className={styles.actionButton} type="button">
          {p.actionAdd}
        </button>
      </div>
    </div>
  );
}
