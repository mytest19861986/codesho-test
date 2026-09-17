import type { Metadata } from "next";
import Link from "next/link";
import {
  IconSparkles,
  IconCalendar,
  IconCheck,
  IconGraduate,
  IconDocument,
  IconFire,
  IconStar,
  IconChart,
  IconTarget,
  IconTrending,
  IconTrophy,
  IconArrowUp,
  IconLaptop,
  IconClock,
  IconFile,
  IconChat,
} from "@/components/ui";
import { studentAlphaContent as copy } from "@/content/fa/student.alpha";
import styles from "./student.module.css";

export const metadata: Metadata = {
  title: `${copy.brand} | ${copy.dashboard.title}`,
  description: copy.dashboard.welcome,
};

export default function StudentDashboardPage() {
  const d = copy.dashboard;

  return (
    <div className={styles.studentDashboard}>
      {/* 1. Large Hero Welcome Banner matching benchmark */}
      <section className={styles.heroBanner} aria-labelledby="hero-welcome-heading">
        <div className={styles.heroContent}>
          <div className={styles.heroGreeting}>
            <h1 id="hero-welcome-heading" className={styles.heroHeading}>
              {d.welcome}
            </h1>
            <p className={styles.heroSubtitle}>
              {d.welcomeSubtitle}
            </p>
          </div>
          <div className={styles.heroButtons}>
            <Link href="/student/coaching" className={styles.heroPrimaryBtn}>
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{d.askMentorAction}</span>
            </Link>
            <Link href="/student/learning" className={styles.heroSecondaryBtn}>
              <IconCalendar aria-hidden="true" style={{ inlineSize: "1.125rem", blockSize: "1.125rem" }} />
              <span>{d.personalPlanAction}</span>
            </Link>
          </div>
        </div>

        <div className={styles.heroGraphicWrapper}>
          <div className={styles.heroGlassPanel}>
            <p className={styles.heroQuoteText}>{d.heroQuote}</p>
            <span className={styles.heroBrandMini}>{d.heroBrandTag}</span>
            <div className={styles.heroChecklist}>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{d.step1}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{d.step2}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{d.step3}</span>
              </div>
              <div className={styles.heroCheckItem}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem", color: "var(--cs-color-success)" }} />
                <span>{d.step4}</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* 2. 4 KPI / Stat Cards matching benchmark */}
      <section className={styles.kpiGrid} aria-label={d.title}>
        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{d.kpi1Title}</span>
            <span className={styles.kpiValue}>{d.kpi1Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{d.kpi1Sub}</span>
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
            <span className={styles.kpiLabel}>{d.kpi2Title}</span>
            <span className={styles.kpiValue}>{d.kpi2Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{d.kpi2Sub}</span>
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
            <span className={styles.kpiLabel}>{d.kpi3Title}</span>
            <span className={styles.kpiValue}>{d.kpi3Value}</span>
            <span className={styles.kpiSub}>
              <span>{d.kpi3Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle3}`}>
              <IconFire aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>

        <div className={styles.kpiCard}>
          <div className={styles.kpiContent}>
            <span className={styles.kpiLabel}>{d.kpi4Title}</span>
            <span className={styles.kpiValue}>{d.kpi4Value}</span>
            <span className={styles.kpiSub}>
              <IconArrowUp aria-hidden="true" style={{ inlineSize: "0.75rem", blockSize: "0.75rem" }} />
              <span>{d.kpi4Sub}</span>
            </span>
          </div>
          <div className={styles.kpiVisual}>
            <div className={`${styles.kpiIconCircle} ${styles.kpiCircle4}`}>
              <IconStar aria-hidden="true" style={{ inlineSize: "1.5rem", blockSize: "1.5rem" }} />
            </div>
          </div>
        </div>
      </section>

      {/* 3. Middle Row: Performance Chart, Learning Goal Ring, Skill Growth */}
      <div className={styles.middleGrid}>
        {/* Performance Chart Simulation */}
        <section className={styles.cardPanel} aria-labelledby="chart-title">
          <header className={styles.panelHeader}>
            <h2 id="chart-title" className={styles.panelTitle}>
              <IconChart aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem", color: "var(--cs-color-brand-primary)" }} />
              <span>{d.chartTitle}</span>
            </h2>
            <span className={styles.panelFilter}>{d.chartPeriod}</span>
          </header>
          <div className={styles.chartContainer}>
            <div className={styles.chartTooltip}>
              <div>{d.chartTodayBadge}</div>
              <div>{d.chartTodayStat}</div>
            </div>
            <div className={styles.chartSvgWrapper}>
              <svg viewBox="0 0 400 120" width="100%" height="100%" preserveAspectRatio="none" aria-hidden="true">
                <defs>
                  <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="var(--cs-color-brand-primary)" stopOpacity="0.25" />
                    <stop offset="100%" stopColor="var(--cs-color-brand-primary)" stopOpacity="0.0" />
                  </linearGradient>
                </defs>
                <path
                  d="M 10 90 Q 70 70, 130 80 T 250 60 T 320 40 T 390 20 L 390 120 L 10 120 Z"
                  fill="url(#chartGradient)"
                />
                <path
                  d="M 10 90 Q 70 70, 130 80 T 250 60 T 320 40 T 390 20"
                  fill="none"
                  stroke="var(--cs-color-brand-primary)"
                  strokeWidth="3"
                />
                <circle cx="10" cy="90" r="4" fill="var(--cs-color-brand-primary)" />
                <circle cx="90" cy="73" r="4" fill="var(--cs-color-brand-primary)" />
                <circle cx="170" cy="78" r="4" fill="var(--cs-color-brand-primary)" />
                <circle cx="250" cy="60" r="4" fill="var(--cs-color-brand-primary)" />
                <circle cx="320" cy="40" r="4" fill="var(--cs-color-brand-primary)" />
                <circle cx="390" cy="20" r="5" fill="var(--cs-color-brand-primary)" stroke="var(--cs-color-bg-surface)" strokeWidth="2" />
              </svg>
            </div>
            <div className={styles.chartLabelsRow}>
              <span>{d.chartW1}</span>
              <span>{d.chartW2}</span>
              <span>{d.chartW3}</span>
              <span>{d.chartW4}</span>
              <span>{d.chartW5}</span>
              <span>{d.chartW6}</span>
            </div>
          </div>
        </section>

        {/* Learning Goal Circular Progress */}
        <section className={styles.cardPanel} aria-labelledby="goal-title">
          <header className={styles.panelHeader}>
            <h2 id="goal-title" className={styles.panelTitle}>
              <IconTarget aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem", color: "var(--cs-color-brand-primary)" }} />
              <span>{d.goalTitle}</span>
            </h2>
            <span className={styles.panelFilter}>{d.goalFilter}</span>
          </header>
          <div className={styles.goalContainer}>
            <div className={styles.goalSvgWrapper}>
              <svg viewBox="0 0 100 100" width="100%" height="100%" aria-hidden="true">
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="var(--cs-color-bg-base)"
                  strokeWidth="10"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="none"
                  stroke="var(--cs-color-brand-primary)"
                  strokeWidth="10"
                  strokeDasharray="251.2"
                  strokeDashoffset="80.38"
                  strokeLinecap="round"
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className={styles.goalCenterText}>
                <span className={styles.goalCenterVal}>{d.goalValue}</span>
                <span className={styles.goalCenterStatus}>{d.goalStatus}</span>
              </div>
            </div>
            <h3 className={styles.goalCourseName}>{d.goalCourseName}</h3>
            <p className={styles.goalModulesDetail}>{d.goalModulesCompleted}</p>
          </div>
        </section>

        {/* Skill Growth Bars */}
        <section className={styles.cardPanel} aria-labelledby="skills-growth-title">
          <header className={styles.panelHeader}>
            <h2 id="skills-growth-title" className={styles.panelTitle}>
              <IconTrending aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem", color: "var(--cs-color-brand-primary)" }} />
              <span>{d.skillsTitle}</span>
            </h2>
            <Link href="/student/growth" className={styles.panelFilter}>
              {d.skillsViewAll}
            </Link>
          </header>
          <div className={styles.skillsList}>
            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{d.skill1Name}</span>
                <span>{d.skill1Val}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "90%", background: "var(--cs-color-brand-primary)" }} />
              </div>
            </div>

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{d.skill2Name}</span>
                <span>{d.skill2Val}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "75%", background: "var(--cs-color-warning)" }} />
              </div>
            </div>

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{d.skill3Name}</span>
                <span>{d.skill3Val}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "60%", background: "var(--cs-color-info)" }} />
              </div>
            </div>

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{d.skill4Name}</span>
                <span>{d.skill4Val}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "55%", background: "var(--cs-color-success)" }} />
              </div>
            </div>

            <div className={styles.skillItem}>
              <div className={styles.skillInfoRow}>
                <span>{d.skill5Name}</span>
                <span>{d.skill5Val}</span>
              </div>
              <div className={styles.skillBarBackground}>
                <div className={styles.skillBarFill} style={{ inlineSize: "70%", background: "var(--cs-color-brand-indigo)" }} />
              </div>
            </div>
          </div>
        </section>
      </div>

      {/* 4. Bottom Row: Recent Activities, Smart Recommendations, Milestone Roadmap */}
      <div className={styles.bottomGrid}>
        {/* Recent Activities */}
        <section className={styles.cardPanel} aria-labelledby="recent-activities-title">
          <header className={styles.panelHeader}>
            <h2 id="recent-activities-title" className={styles.panelTitle}>
              <IconClock aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem", color: "var(--cs-color-brand-primary)" }} />
              <span>{d.recentTitle}</span>
            </h2>
            <Link href="/student/learning" className={styles.panelFilter}>
              {d.recentViewAll}
            </Link>
          </header>
          <div className={styles.activityList}>
            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle2}`}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{d.act1Desc}</p>
                <span className={styles.activityTime}>{d.act1Time}</span>
              </div>
            </div>

            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle1}`}>
                <IconFile aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{d.act2Desc}</p>
                <span className={styles.activityTime}>{d.act2Time}</span>
              </div>
            </div>

            <div className={styles.activityItem}>
              <div className={`${styles.activityIconCircle} ${styles.kpiCircle4}`}>
                <IconChat aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <div className={styles.activityContent}>
                <p className={styles.activityDesc}>{d.act3Desc}</p>
                <span className={styles.activityTime}>{d.act3Time}</span>
              </div>
            </div>
          </div>
        </section>

        {/* Smart Recommendations */}
        <section className={styles.cardPanel} aria-labelledby="recommendations-title">
          <header className={styles.panelHeader}>
            <h2 id="recommendations-title" className={styles.panelTitle}>
              <IconSparkles aria-hidden="true" style={{ inlineSize: "1.25rem", blockSize: "1.25rem", color: "var(--cs-color-brand-primary)" }} />
              <span>{d.recsTitle}</span>
            </h2>
            <span className={styles.panelFilter}>{d.recsBadge}</span>
          </header>
          <div className={styles.recList}>
            <div className={styles.recItem}>
              <div>
                <p className={styles.recTitle}>{d.rec1Title}</p>
              </div>
              <Link href="/student/learning" className={styles.recAction}>
                {d.rec1Time}
              </Link>
            </div>

            <div className={styles.recItem}>
              <div>
                <p className={styles.recTitle}>{d.rec2Title}</p>
              </div>
              <Link href="/student/portfolio" className={styles.recAction}>
                {d.rec2Level}
              </Link>
            </div>

            <div className={styles.recItem}>
              <div>
                <p className={styles.recTitle}>{d.rec3Title}</p>
              </div>
              <Link href="/student/coaching" className={styles.recAction}>
                {d.rec3Action}
              </Link>
            </div>
          </div>
        </section>

        {/* Milestone Success Roadmap */}
        <section className={styles.milestonePanel} aria-labelledby="milestone-roadmap-title">
          <div className={styles.milestoneHeader}>
            <div>
              <h2 id="milestone-roadmap-title" className={styles.milestoneTitle}>
                {d.milestoneBannerTitle}
              </h2>
              <p className={styles.milestoneDesc}>{d.milestoneBannerDesc}</p>
            </div>
            <IconTrophy aria-hidden="true" style={{ inlineSize: "2.25rem", blockSize: "2.25rem", color: "var(--cs-color-brand-primary)" }} />
          </div>

          <div className={styles.milestoneStepsRow}>
            <div className={styles.milestoneStepNode}>
              <div className={styles.milestoneCircle}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <span className={styles.milestoneStepLabel}>{d.step1}</span>
            </div>

            <div className={styles.milestoneStepNode}>
              <div className={styles.milestoneCircle}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <span className={styles.milestoneStepLabel}>{d.step2}</span>
            </div>

            <div className={styles.milestoneStepNode}>
              <div className={styles.milestoneCircle}>
                <IconCheck aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <span className={styles.milestoneStepLabel}>{d.step3}</span>
            </div>

            <div className={styles.milestoneStepNode}>
              <div className={styles.milestoneCircle}>
                <IconTarget aria-hidden="true" style={{ inlineSize: "0.875rem", blockSize: "0.875rem" }} />
              </div>
              <span className={styles.milestoneStepLabel}>{d.step4}</span>
            </div>
          </div>

          <p className={styles.milestoneQuote}>{d.milestoneFooter}</p>
        </section>
      </div>
    </div>
  );
}
