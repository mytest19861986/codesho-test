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
  const cl = copy.commonLabels;

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Large Hero Banner matching Benchmark */}
      <section className={styles.heroBanner} aria-labelledby="coaching-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div style={{ display: "flex", alignItems: "center", gap: "var(--cs-space-2)", marginBlockEnd: "var(--cs-space-1)" }}>
              <Badge variant="info">{c.heroBadge}</Badge>
              <Badge variant="outline">{c.sourceLabel}</Badge>
            </div>
            <h1 id="coaching-hero-heading" className={styles.heroHeading}>
              {c.title}
            </h1>
            <p className={styles.heroSubtitle}>
              {c.description}
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button type="button" className={styles.heroPrimaryBtn}>
              <span aria-hidden="true">{ic.sparkles}</span>
              <span>{c.heroActionPrimary}</span>
            </button>
            <button type="button" className={styles.heroSecondaryBtn}>
              <span aria-hidden="true">{ic.calendar}</span>
              <span>{c.heroActionSecondary}</span>
            </button>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{cl.quoteCoaching}</p>
            <span className={styles.heroBrandMini}>{c.mentorStatus}</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <span aria-hidden="true">{copy.indicators.check}</span>
                <span>{cl.fastResponseBadge}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <span aria-hidden="true">{copy.indicators.check}</span>
                <span>{cl.architectureAnalysisBadge}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI Metric Cards */}
      <section className={styles.kpiGrid} aria-label={c.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{c.kpi1Title}</span>
            <span className={styles.kpiValue}>{c.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.arrowUp}</span>
              <span>{c.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <span aria-hidden="true">{ic.chat}</span>
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{c.kpi2Title}</span>
            <span className={styles.kpiValue}>{c.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.check}</span>
              <span>{c.kpi2Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <span aria-hidden="true">{ic.lightbulb}</span>
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{c.kpi3Title}</span>
            <span className={styles.kpiValue}>{c.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.star}</span>
              <span>{c.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <span aria-hidden="true">{ic.star}</span>
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{c.kpi4Title}</span>
            <span className={styles.kpiValue}>{c.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <span aria-hidden="true">{ic.trending}</span>
              <span>{c.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <span aria-hidden="true">{ic.fire}</span>
            </div>
          </div>
        </div>
      </section>

      {/* 3. Middle Grid: Dedicated Mentor & Advice + Recommended Questions */}
      <section className={styles.twoColumnGrid} aria-label={cl.ariaCoachingQuestions}>
        {/* Mentor & Recent Guidance */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.lightbulb}</span>
              <span>{c.adviceTitle}</span>
            </h2>
            <Badge variant="success">{cl.verifiedAnalysis}</Badge>
          </div>
          <p className={styles.cardText} style={{ lineHeight: "var(--cs-line-height-relaxed)" }}>
            {c.adviceText}
          </p>

          <div style={{ background: "var(--cs-color-bg-base)", padding: "var(--cs-space-4)", borderRadius: "var(--cs-radius-control)", display: "flex", alignItems: "center", gap: "var(--cs-space-3)" }}>
            <div className={styles.userAvatar} aria-hidden="true">
              <span>{cl.mentorAvatarInitial}</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column" }}>
              <span style={{ fontWeight: "var(--cs-font-weight-bold)", fontSize: "var(--cs-font-size-body)" }}>{c.mentorName}</span>
              <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>{c.mentorRole}</span>
            </div>
            <div style={{ marginInlineStart: "auto" }}>
              <Badge variant="info">{c.mentorStatus}</Badge>
            </div>
          </div>

          <div style={{ marginBlockStart: "auto", display: "flex", gap: "var(--cs-space-2)", justifyContent: "flex-end" }}>
            <button type="button" className={styles.actionButton}>
              {c.actionPrompt}
            </button>
          </div>
        </div>

        {/* Recommended Questions List */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.question}</span>
              <span>{c.recommendedQuestionsTitle}</span>
            </h2>
            <span className={styles.panelFilter}>{cl.analyticSuggestion}</span>
          </div>
          <ul className={styles.listGroup}>
            <li className={styles.listItem}>
              <span className={styles.recTitle}>{c.q1}</span>
              <button type="button" className={styles.recAction}>
                {cl.askQuestionBtn}
              </button>
            </li>
            <li className={styles.listItem}>
              <span className={styles.recTitle}>{c.q2}</span>
              <button type="button" className={styles.recAction}>
                {cl.askQuestionBtn}
              </button>
            </li>
            <li className={styles.listItem}>
              <span className={styles.recTitle}>{c.q3}</span>
              <button type="button" className={styles.recAction}>
                {cl.askQuestionBtn}
              </button>
            </li>
          </ul>
        </div>
      </section>

      {/* 4. Bottom Row: History Cards (3 Columns) */}
      <section className={styles.bottomGrid} aria-label={cl.ariaCoachingHistory}>
        {/* History Item 1 */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.document}</span>
              <span>{c.h1Title}</span>
            </h3>
            <span className={styles.activityTime}>{c.h1Date}</span>
          </div>
          <p className={styles.activityDesc}>{c.h1Content}</p>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "0.6875rem", color: "var(--cs-color-brand-primary)", fontWeight: "var(--cs-font-weight-bold)" }}>
              {c.actionViewHistory}
            </span>
          </div>
        </div>

        {/* History Item 2 */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h3 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <span aria-hidden="true">{ic.laptop}</span>
              <span>{c.h2Title}</span>
            </h3>
            <span className={styles.activityTime}>{c.h2Date}</span>
          </div>
          <p className={styles.activityDesc}>{c.h2Content}</p>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <span style={{ fontSize: "0.6875rem", color: "var(--cs-color-brand-primary)", fontWeight: "var(--cs-font-weight-bold)" }}>
              {c.actionViewHistory}
            </span>
          </div>
        </div>

        {/* History Item 3 */}
        <div className={styles.milestonePanel}>
          <div className={styles.milestoneHeader}>
            <div>
              <h3 className={styles.milestoneTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
                {c.h3Title}
              </h3>
              <p className={styles.milestoneDesc}>{c.h3Date}</p>
            </div>
            <span aria-hidden="true" style={{ fontSize: "1.75rem" }}>{ic.flag}</span>
          </div>
          <p style={{ fontSize: "0.75rem", color: "var(--cs-color-text-secondary)", margin: 0 }}>
            {c.h3Content}
          </p>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Link href="/student/learning" className={styles.actionButton} style={{ textDecoration: "none" }}>
              {cl.viewRelatedModule}
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
