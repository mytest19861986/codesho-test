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
  const ic = copy.icons;
  const cl = copy.commonLabels;

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Large Hero Banner matching Benchmark architecture */}
      <section className={styles.heroBanner} aria-labelledby="portfolio-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-2)", marginBlockEnd: "var(--cs-space-1)" }}>
              <Badge variant="info">{p.heroBadge}</Badge>
              <Badge variant="outline">{p.privacyBadge}</Badge>
            </div>
            <h1 id="portfolio-hero-heading" className={styles.heroHeading}>
              {p.title}
            </h1>
            <p className={styles.heroSubtitle}>
              {p.description}
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button type="button" className={styles.heroPrimaryBtn}>
              <span aria-hidden="true">{ic.sparkles}</span>
              <span>{p.heroActionPrimary}</span>
            </button>
            <button type="button" className={styles.heroSecondaryBtn}>
              <span aria-hidden="true">{ic.document}</span>
              <span>{p.heroActionSecondary}</span>
            </button>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{cl.quotePortfolio}</p>
            <span className={styles.heroBrandMini}>{p.privacyNote}</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <span aria-hidden="true">{copy.indicators.check}</span>
                <span>{p.project1Status}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <span aria-hidden="true">{copy.indicators.check}</span>
                <span>{p.project2Status}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <span aria-hidden="true">{copy.indicators.check}</span>
                <span>{p.project3Status}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <span aria-hidden="true">{copy.indicators.check}</span>
                <span>{p.project4Status}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI / Metric Cards Row */}
      <section className={styles.kpiGrid} aria-label={p.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{p.kpi1Title}</span>
            <span className={styles.kpiValue}>{p.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.arrowUp}</span>
              <span>{p.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <span aria-hidden="true">{ic.laptop}</span>
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{p.kpi2Title}</span>
            <span className={styles.kpiValue}>{p.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.clock}</span>
              <span>{p.kpi2Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <span aria-hidden="true">{ic.gear}</span>
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{p.kpi3Title}</span>
            <span className={styles.kpiValue}>{p.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.star}</span>
              <span>{p.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <span aria-hidden="true">{ic.document}</span>
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{p.kpi4Title}</span>
            <span className={styles.kpiValue}>{p.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.trending}</span>
              <span>{p.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <span aria-hidden="true">{ic.trophy}</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Portfolio Projects Showcase Grid (4 Rich Cards) */}
      <section aria-labelledby="showcase-heading" style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-4)" }}>
        <div className={styles.panelHeader}>
          <h2 id="showcase-heading" className={styles.panelTitle}>
            <span aria-hidden="true">{ic.laptop}</span>
            <span>{cl.activeShowcaseTitle}</span>
          </h2>
          <span className={styles.panelFilter}>{cl.activeProjectsBadge}</span>
        </div>

        <div className={styles.twoColumnGrid}>
          {/* Project 1 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <span aria-hidden="true">{ic.laptop}</span>
                <span>{p.project1Title}</span>
              </h3>
              <Badge variant="success">{p.project1Status}</Badge>
            </div>
            <p className={styles.cardText}>{p.project1Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{p.project1Tags}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-brand-primary)" }}>
                {p.project1Metrics}
              </span>
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
                {p.actionEdit}
              </button>
              <button className={styles.actionButton} type="button">
                {p.actionView}
              </button>
            </div>
          </div>

          {/* Project 2 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <span aria-hidden="true">{ic.gear}</span>
                <span>{p.project2Title}</span>
              </h3>
              <Badge variant="warning">{p.project2Status}</Badge>
            </div>
            <p className={styles.cardText}>{p.project2Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{p.project2Tags}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-warning-foreground)" }}>
                {p.project2Metrics}
              </span>
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
                {p.actionEdit}
              </button>
              <button className={styles.actionButton} type="button">
                {p.actionView}
              </button>
            </div>
          </div>

          {/* Project 3 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <span aria-hidden="true">{ic.chart}</span>
                <span>{p.project3Title}</span>
              </h3>
              <Badge variant="info">{p.project3Status}</Badge>
            </div>
            <p className={styles.cardText}>{p.project3Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{p.project3Tags}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-info-foreground)" }}>
                {p.project3Metrics}
              </span>
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
                {p.actionEdit}
              </button>
              <button className={styles.actionButton} type="button">
                {p.actionView}
              </button>
            </div>
          </div>

          {/* Project 4 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <span aria-hidden="true">{ic.target}</span>
                <span>{p.project4Title}</span>
              </h3>
              <Badge variant="outline">{p.project4Status}</Badge>
            </div>
            <p className={styles.cardText}>{p.project4Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{p.project4Tags}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-text-secondary)" }}>
                {p.project4Metrics}
              </span>
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
                {p.actionEdit}
              </button>
              <button className={styles.actionButton} type="button">
                {p.actionView}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Bottom Operational & Readiness Grid (3 Columns matching Benchmark) */}
      <section className={styles.bottomGrid} aria-label={cl.ariaPortfolioAnalytics}>
        {/* Recent Submissions */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.history}</span>
              <span>{p.recentSubmissionsTitle}</span>
            </h3>
          </div>
          <div className={styles.activityList}>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle1}`}>
                <span aria-hidden="true">{ic.file}</span>
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{p.sub1Title}</p>
                <span className={styles.activityTime}>{p.sub1Time}</span>
              </div>
            </div>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle2}`}>
                <span aria-hidden="true">{ic.document}</span>
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{p.sub2Title}</p>
                <span className={styles.activityTime}>{p.sub2Time}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Mentor Feedback Highlights */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.chat}</span>
              <span>{p.feedbackSummaryTitle}</span>
            </h3>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-3)" }}>
            <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
              <p style={{ margin: 0, fontSize: "0.75rem", fontStyle: "italic", color: "var(--cs-color-text-secondary)" }}>
                {p.feedback1}
              </p>
            </div>
            <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-3)", borderRadius: "var(--cs-radius-control)" }}>
              <p style={{ margin: 0, fontSize: "0.75rem", fontStyle: "italic", color: "var(--cs-color-text-secondary)" }}>
                {p.feedback2}
              </p>
            </div>
          </div>
        </div>

        {/* Portfolio Market Readiness Panel */}
        <div className={styles.milestonePanel}>
          <div className={styles.milestoneHeader}>
            <div>
              <h3 className={styles.milestoneTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                {p.readinessTitle}
              </h3>
              <p className={styles.milestoneDesc}>{p.readinessScore}</p>
            </div>
            <span aria-hidden="true" style={{ fontSize: "1.75rem" }}>{ic.trophy}</span>
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--cs-color-text-secondary)", margin: 0 }}>
            {p.readinessDetail}
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Link href="/student/learning" className={styles.actionButton} style={{ textDecoration: "none" }}>
              {p.actionAdd}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
