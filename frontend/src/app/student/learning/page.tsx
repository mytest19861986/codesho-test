import type { Metadata } from "next";
import Link from "next/link";
import {
  Badge,
  Progress,
  IconSparkles,
  IconMap,
  IconCheck,
  IconArrowUp,
  IconGraduate,
  IconClock,
  IconStar,
  IconDocument,
  IconTrending,
  IconFire,
  IconLaptop,
  IconGear,
  IconChart,
  IconTarget,
  IconFile,
} from "@/components/ui";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.learning.title}`,
  description: copy.learning.description,
};

export default function StudentLearningPage() {
  const l = copy.learning;
  const cl = copy.commonLabels;

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Large Hero Banner matching Benchmark */}
      <section className={styles.heroBanner} aria-labelledby="learning-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-2)", marginBlockEnd: "var(--cs-space-1)" }}>
              <Badge variant="primary">{l.heroBadge}</Badge>
              <Badge variant="outline">{l.currentPath}</Badge>
            </div>
            <h1 id="learning-hero-heading" className={styles.heroHeading}>
              {l.title}
            </h1>
            <p className={styles.heroSubtitle}>
              {l.description}
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button type="button" className={styles.heroPrimaryBtn}>
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{l.heroActionPrimary}</span>
            </button>
            <button type="button" className={styles.heroSecondaryBtn}>
              <IconMap aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{l.heroActionSecondary}</span>
            </button>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{cl.quoteLearning}</p>
            <span className={styles.heroBrandMini}>{l.progressRatio}</span>
            <div style={{ marginBlock: "var(--cs-space-2)" }}>
              <Progress value={68} label={l.progressRatio} />
            </div>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{l.module1Status}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{l.module2Status}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI Metric Cards */}
      <section className={styles.kpiGrid} aria-label={l.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{l.kpi1Title}</span>
            <span className={styles.kpiValue}>{l.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{l.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconGraduate aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{l.kpi2Title}</span>
            <span className={styles.kpiValue}>{l.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <IconClock aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{l.kpi2Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <IconClock aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{l.kpi3Title}</span>
            <span className={styles.kpiValue}>{l.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <IconStar aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{l.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{l.kpi4Title}</span>
            <span className={styles.kpiValue}>{l.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <IconTrending aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{l.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconFire aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Detailed Modules Roadmap (4 Rich Cards Grid) */}
      <section aria-labelledby="modules-roadmap-heading" style={{ display: "flex", flexDirection: "column", gap: "var(--cs-space-4)" }}>
        <div className={styles.panelHeader}>
          <h2 id="modules-roadmap-heading" className={styles.panelTitle}>
            <IconMap aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem", color: "var(--cs-color-brand-primary)" }} />
            <span>{l.roadmapHeader}</span>
          </h2>
          <span className={styles.panelFilter}>{l.progressRatio}</span>
        </div>

        <div className={styles.twoColumnGrid}>
          {/* Module 1 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <IconLaptop aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
                <span>{l.module1Title}</span>
              </h3>
              <Badge variant="success">{l.module1Status}</Badge>
            </div>
            <p className={styles.cardText}>{l.module1Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{l.module1Time}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-success)" }}>
                {cl.progress100}
              </span>
            </div>
            <div className={styles.skillBarBackground}>
              <div className={styles.skillBarFill} style={{ inlineSize: "100%", background: "var(--cs-color-success)" }} />
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button">
                {l.actionDetails}
              </button>
            </div>
          </div>

          {/* Module 2 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <IconGear aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
                <span>{l.module2Title}</span>
              </h3>
              <Badge variant="warning">{l.module2Status}</Badge>
            </div>
            <p className={styles.cardText}>{l.module2Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{l.module2Time}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-warning)" }}>
                {cl.progress65}
              </span>
            </div>
            <div className={styles.skillBarBackground}>
              <div className={styles.skillBarFill} style={{ inlineSize: "65%", background: "var(--cs-color-warning)" }} />
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={styles.actionButton} type="button">
                {l.actionContinue}
              </button>
            </div>
          </div>

          {/* Module 3 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <IconChart aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
                <span>{l.module3Title}</span>
              </h3>
              <Badge variant="info">{l.module3Status}</Badge>
            </div>
            <p className={styles.cardText}>{l.module3Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{l.module3Time}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-info-foreground)" }}>
                {cl.pendingModule2}
              </span>
            </div>
            <div className={styles.skillBarBackground}>
              <div className={styles.skillBarFill} style={{ inlineSize: "0%", background: "var(--cs-color-border-subtle)" }} />
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button" disabled>
                {l.actionDetails}
              </button>
            </div>
          </div>

          {/* Module 4 */}
          <div className={styles.cardPanel}>
            <div className={styles.panelHeader}>
              <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                <IconTarget aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
                <span>{l.module4Title}</span>
              </h3>
              <Badge variant="outline">{l.module4Status}</Badge>
            </div>
            <p className={styles.cardText}>{l.module4Desc}</p>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <span className={styles.activityTime}>{l.module4Time}</span>
              <span style={{ fontSize: "0.75rem", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-text-secondary)" }}>
                {cl.complementaryPhase}
              </span>
            </div>
            <div className={styles.skillBarBackground}>
              <div className={styles.skillBarFill} style={{ inlineSize: "0%", background: "var(--cs-color-border-subtle)" }} />
            </div>
            <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
              <button className={`${styles.actionButton} ${styles.secondaryAction}`} type="button" disabled>
                {l.actionDetails}
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* 4. Bottom Operational & Resources Row */}
      <section className={styles.bottomGrid} aria-label={cl.ariaLearningResources}>
        {/* Weekly Analytics Card */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconChart aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{l.analyticsTitle}</span>
            </h3>
          </div>
          <p className={styles.cardText}>{l.analyticsSub}</p>
          <div className={styles.chartSvgWrapper}>
            <svg viewBox="0 0 400 120" width="100%" height="100%" preserveAspectRatio="none" aria-hidden="true">
              <defs>
                <linearGradient id="learnGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="var(--cs-color-brand-primary)" stopOpacity="0.25" />
                  <stop offset="100%" stopColor="var(--cs-color-brand-primary)" stopOpacity="0.0" />
                </linearGradient>
              </defs>
              <path
                d="M 10 90 Q 70 60, 130 75 T 250 45 T 320 30 T 390 15 L 390 120 L 10 120 Z"
                fill="url(#learnGradient)"
              />
              <path
                d="M 10 90 Q 70 60, 130 75 T 250 45 T 320 30 T 390 15"
                fill="none"
                stroke="var(--cs-color-brand-primary)"
                strokeWidth="3"
              />
            </svg>
          </div>
        </div>

        {/* Prerequisites and Materials */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{l.prerequisitesTitle}</span>
            </h3>
          </div>
          <div className={styles.activityList}>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle1}`}>
                <IconFile aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{l.prereq1}</p>
                <span className={styles.activityTime}>{cl.refStandard}</span>
              </div>
            </div>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle2}`}>
                <IconLaptop aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{l.prereq2}</p>
                <span className={styles.activityTime}>{cl.officialGuide}</span>
              </div>
            </div>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle3}`}>
                <IconGear aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{l.prereq3}</p>
                <span className={styles.activityTime}>{cl.safetyRules}</span>
              </div>
            </div>
          </div>
        </div>

        {/* Coaching Connect CTA */}
        <div className={styles.milestonePanel}>
          <div className={styles.milestoneHeader}>
            <div>
              <h3 className={styles.milestoneTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                {copy.coaching.title}
              </h3>
              <p className={styles.milestoneDesc}>{cl.learningGuideSub}</p>
            </div>
            <IconSparkles aria-hidden="true" style={{ inlineSize: "2rem", blockSize: "2rem", color: "var(--cs-color-brand-primary)" }} />
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--cs-color-text-secondary)", margin: 0 }}>
            {copy.coaching.adviceText}
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Link href="/student/coaching" className={styles.actionButton} style={{ textDecoration: "none" }}>
              {copy.coaching.actionPrompt}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
