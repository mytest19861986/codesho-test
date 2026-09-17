import type { Metadata } from "next";
import Link from "next/link";
import { parentAlphaContent as copy } from "@/content/fa/parent.alpha";
import {
  Badge,
  IconSparkles,
  IconChat,
  IconCheck,
  IconArrowUp,
  IconClock,
  IconDocument,
  IconFire,
  IconCalendar,
  IconShield,
  IconLaptop,
  IconChart,
} from "@/components/ui";
import styles from "../student/student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.overview.title}`,
  description: copy.overview.heroSubtitle,
};

export default function ParentOverviewPage() {
  const o = copy.overview;

  return (
    <div className={styles.studentDashboard}>
      {/* 0. Multi-Child Selector Banner (Explicit Context Switching as required by Commander) */}
      <div className={styles.childSelectorBanner}>
        <div className={styles.childSelectorInfo}>
          <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)", fontWeight: "var(--cs-font-weight-medium)" }}>
            {o.childSelectLabel}
          </span>
          <span style={{ fontSize: "var(--cs-font-size-body)", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-text-primary)" }}>
            {o.selectedChildName}
          </span>
        </div>
        <Badge variant="primary" className={styles.childSelectorBadge}>
          {o.selectedChildBadge}
        </Badge>
      </div>

      {/* 1. Contextual Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="parent-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>{o.heroBadge}</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>حریم خصوصی تضمین‌شده</Badge>
            </div>
            <h1 id="parent-hero-heading" className={styles.heroHeading}>
              {o.heroHeading}
            </h1>
            <p className={styles.heroSubtitle}>
              {o.heroSubtitle}
            </p>
          </div>
          <div className={styles.heroButtons}>
            <button type="button" className={styles.heroPrimaryBtn}>
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{o.heroActionPrimary}</span>
            </button>
            <button type="button" className={styles.heroSecondaryBtn}>
              <IconChat aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{o.heroActionSecondary}</span>
            </button>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{o.oversightQuote}</p>
            <span className={styles.heroBrandMini}>{o.oversightNote}</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check1}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check2}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check3}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{o.check4}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI Metrics Grid for Parent Oversight */}
      <section className={styles.kpiGrid} aria-label={o.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi1Title}</span>
            <span className={styles.kpiValue}>{o.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi1Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle1}`}>
              <IconClock aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi2Title}</span>
            <span className={styles.kpiValue}>{o.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi2Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle2}`}>
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi3Title}</span>
            <span className={styles.kpiValue}>{o.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <IconFire aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconCalendar aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi4Title}</span>
            <span className={styles.kpiValue}>{o.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconShield aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Operational Workflow & Oversight Grid */}
      <section className={styles.twoColumnGrid} aria-label="روند و دستاوردها">
        {/* Recent Milestones & Projects Completed */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconLaptop aria-hidden="true" />
              <span>{o.recentMilestonesTitle}</span>
            </h2>
            <Badge variant="success">تأییدشده</Badge>
          </div>
          <div className={styles.activityList}>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle1}`}>
                <IconCheck aria-hidden="true" />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{o.milestone1Title}</p>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className={styles.activityTime}>{o.milestone1Date}</span>
                  <Badge variant="outline">{o.milestone1Status}</Badge>
                </div>
              </div>
            </div>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle2}`}>
                <IconCheck aria-hidden="true" />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{o.milestone2Title}</p>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className={styles.activityTime}>{o.milestone2Date}</span>
                  <Badge variant="outline">{o.milestone2Status}</Badge>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Consent & Oversight Management */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconShield aria-hidden="true" />
              <span>{o.safetyTitle}</span>
            </h2>
            <Badge variant="primary">سیاست حاکمیتی</Badge>
          </div>
          <p className={styles.cardText}>{o.safetyDescription}</p>
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-3) var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
              {o.consentStatusLabel}
            </span>
            <span style={{ fontSize: "var(--cs-font-size-caption)", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-success-foreground)" }}>
              {o.consentStatusValue}
            </span>
          </div>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <button className={`${styles.actionButton} ${styles.primaryActionButton}`} type="button">
              {o.actionManageConsent}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
