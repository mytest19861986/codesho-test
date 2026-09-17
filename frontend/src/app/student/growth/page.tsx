import type { Metadata } from "next";
import Link from "next/link";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import {
  Badge,
  IconSparkles,
  IconChart,
  IconCheck,
  IconArrowUp,
  IconTrending,
  IconStar,
  IconGraduate,
  IconTrophy,
  IconFlag,
  IconFire,
  IconClock,
  IconTarget,
  IconGear,
} from "@/components/ui";
import styles from "../student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.growth.title}`,
  description: copy.growth.description,
};

export default function StudentGrowthPage() {
  const g = copy.growth;
  const cl = copy.commonLabels;

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Large Hero Banner matching Benchmark */}
      <section className={styles.heroBanner} aria-labelledby="growth-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-2)", marginBlockEnd: "var(--cs-space-1)" }}>
              <Badge variant="success">{g.invariantBadge}</Badge>
              <Badge variant="outline">{g.heroBadge}</Badge>
            </div>
            <h1 id="growth-hero-heading" className={styles.heroHeading}>
              {g.title}
            </h1>
            <p className={styles.heroSubtitle}>
              {g.description}
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button type="button" className={styles.heroPrimaryBtn}>
              <IconSparkles aria-hidden="true" />
              <span>{g.heroActionPrimary}</span>
            </button>
            <button type="button" className={styles.heroSecondaryBtn}>
              <IconChart aria-hidden="true" />
              <span>{g.heroActionSecondary}</span>
            </button>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{cl.quoteGrowth}</p>
            <span className={styles.heroBrandMini}>{g.selfSummaryText}</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" />
                <span>{cl.noRankingBadge}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" />
                <span>{cl.personalContinuityBadge}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI Metric Cards */}
      <section className={styles.kpiGrid} aria-label={g.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{g.kpi1Title}</span>
            <span className={styles.kpiValue}>{g.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" />
              <span>{g.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconTrending aria-hidden="true" />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{g.kpi2Title}</span>
            <span className={styles.kpiValue}>{g.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <IconStar aria-hidden="true" />
              <span>{g.kpi2Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <IconGraduate aria-hidden="true" />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{g.kpi3Title}</span>
            <span className={styles.kpiValue}>{g.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <IconTrophy aria-hidden="true" />
              <span>{g.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconFlag aria-hidden="true" />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{g.kpi4Title}</span>
            <span className={styles.kpiValue}>{g.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <IconFire aria-hidden="true" />
              <span>{g.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconClock aria-hidden="true" />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Middle 2-Column Grid: Mastery Skills + Growth Roadmap */}
      <section className={styles.twoColumnGrid} aria-label={cl.ariaGrowthSkills}>
        {/* Individual Mastery Skills Panel */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconTrending aria-hidden="true" />
              <span>{g.skillsTitle}</span>
            </h2>
            <Badge variant="success">{cl.personalContinuity}</Badge>
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

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{g.skill4}</span>
                <span>{g.skill4Rate}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "88%", background: "var(--cs-color-warning)" }} />
              </div>
            </div>

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{g.skill5}</span>
                <span>{g.skill5Rate}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "82%", background: "var(--cs-color-brand-indigo)" }} />
              </div>
            </div>
          </div>
        </div>

        {/* Stable Milestones Panel */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconFlag aria-hidden="true" />
              <span>{g.milestoneTitle}</span>
            </h2>
            <span className={styles.panelFilter}>{cl.establishedRecords}</span>
          </div>
          <ul className={styles.listGroup}>
            <li className={styles.listItem} style={{ flexDirection: "column", alignItems: "stretch", gap: "0.25rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
                  {g.milestone1}
                </span>
                <Badge variant="success"><IconCheck aria-hidden="true" style={{ fontSize: "0.75rem" }} /></Badge>
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

            <li className={styles.listItem} style={{ flexDirection: "column", alignItems: "stretch", gap: "0.25rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className={styles.cardHeading} style={{ fontSize: "var(--cs-font-size-body)" }}>
                  {g.milestone3}
                </span>
                <Badge variant="success"><IconCheck aria-hidden="true" style={{ fontSize: "0.75rem" }} /></Badge>
              </div>
              <span className={styles.activityTime}>{g.milestone3Date}</span>
            </li>
          </ul>
        </div>
      </section>

      {/* 4. Bottom Row: Personal Growth Plan & Milestones (3 Columns) */}
      <section className={styles.bottomGrid} aria-label={cl.ariaGrowthRoadmap}>
        {/* Step 1 */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconTarget aria-hidden="true" />
              <span>{cl.step1Growth}</span>
            </h3>
            <span className={styles.activityTime}>{cl.nearGoal}</span>
          </div>
          <p className={styles.activityDesc}>{g.planStep1}</p>
        </div>

        {/* Step 2 */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconGear aria-hidden="true" />
              <span>{cl.step2Growth}</span>
            </h3>
            <span className={styles.activityTime}>{cl.midGoal}</span>
          </div>
          <p className={styles.activityDesc}>{g.planStep2}</p>
        </div>

        {/* Final Goal Banner */}
        <div className={styles.milestonePanel}>
          <div className={styles.milestoneHeader}>
            <div>
              <h3 className={styles.milestoneTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                {cl.step3Growth}
              </h3>
              <p className={styles.milestoneDesc}>{cl.proShowcase}</p>
            </div>
            <div style={{ fontSize: "1.75rem", color: "var(--cs-color-brand-primary)" }}>
              <IconTrophy aria-hidden="true" />
            </div>
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--cs-color-text-secondary)", margin: 0 }}>
            {g.planStep3}
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Link href="/student/portfolio" className={styles.actionButton} style={{ textDecoration: "none" }}>
              {cl.viewPortfolioLink}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
