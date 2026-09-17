import type { Metadata } from "next";
import Link from "next/link";
import { mentorAlphaContent as copy } from "@/content/fa/mentor.alpha";
import {
  Badge,
  IconSparkles,
  IconChat,
  IconCheck,
  IconArrowUp,
  IconClock,
  IconDocument,
  IconLaptop,
  IconShield,
} from "@/components/ui";
import styles from "../student/student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.overview.title}`,
  description: copy.overview.heroSubtitle,
};

export default function MentorOverviewPage() {
  const o = copy.overview;

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Contextual Hero Banner */}
      <section className={styles.heroBanner} aria-labelledby="mentor-hero-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <div className={styles.heroBadgeRow}>
              <Badge variant="primary" className={styles.heroBadgeTranslucent}>{o.heroBadge}</Badge>
              <Badge variant="outline" className={styles.heroBadgeDark}>{o.heroBadgeSecondary}</Badge>
            </div>
            <h1 id="mentor-hero-heading" className={styles.heroHeading}>
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
            <p className={styles.heroQuoteText}>{o.reviewConsoleTitle}</p>
            <span className={styles.heroBrandMini}>{o.reviewConsoleSubtitle}</span>
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

      {/* 2. 4 KPI Metrics Grid for Mentor Review Workload */}
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
              <IconDocument aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
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
              <IconClock aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{o.kpi3Title}</span>
            <span className={styles.kpiValue}>{o.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <IconCheck aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{o.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconLaptop aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
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

      {/* 3. Operational Workflow & Review Queue Grid */}
      <section className={styles.twoColumnGrid} aria-label="صف بررسی و تعهدات مربیگری">
        {/* Pending Reviews Queue */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconDocument aria-hidden="true" />
              <span>{o.pendingQueueTitle}</span>
            </h2>
            <Badge variant="warning">در انتظار بازخورد</Badge>
          </div>
          <div className={styles.activityList}>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle1}`}>
                <IconLaptop aria-hidden="true" />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{o.pendingItem1Title}</p>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className={styles.activityTime}>{o.pendingItem1Student} • {o.pendingItem1Time}</span>
                  <Badge variant="outline">{o.pendingItem1Status}</Badge>
                </div>
              </div>
            </div>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle2}`}>
                <IconDocument aria-hidden="true" />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{o.pendingItem2Title}</p>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span className={styles.activityTime}>{o.pendingItem2Student} • {o.pendingItem2Time}</span>
                  <Badge variant="outline">{o.pendingItem2Status}</Badge>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Mentor Governance & Review Environment Focus */}
        <div className={styles.cardPanel}>
          <div className={styles.panelHeader}>
            <h2 className={styles.panelTitle} style={{ fontSize: "var(--cs-font-size-body)" }}>
              <IconShield aria-hidden="true" />
              <span>{o.feedbackFocusTitle}</span>
            </h2>
            <Badge variant="primary">استاندارد راهبری</Badge>
          </div>
          <p className={styles.cardText}>{o.feedbackFocusDesc}</p>
          <div style={{
            background: "var(--cs-color-bg-base)",
            padding: "var(--cs-space-3) var(--cs-space-4)",
            borderRadius: "var(--cs-radius-control)",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between"
          }}>
            <span style={{ fontSize: "var(--cs-font-size-caption)", color: "var(--cs-color-text-secondary)" }}>
              {o.feedbackComplianceLabel}
            </span>
            <span style={{ fontSize: "var(--cs-font-size-caption)", fontWeight: "var(--cs-font-weight-bold)", color: "var(--cs-color-success-foreground)" }}>
              {o.feedbackComplianceValue}
            </span>
          </div>
          <div style={{ marginBlockStart: "auto", display: "flex", justifyContent: "flex-end" }}>
            <button className={`${styles.actionButton} ${styles.primaryActionButton}`} type="button">
              {o.actionStartReview}
            </button>
          </div>
        </div>
      </section>
    </div>
  );
}
