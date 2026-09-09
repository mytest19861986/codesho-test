"use client";

import React from "react";
import styles from "./growth.module.css";

export interface GrowthMetricItem {
  key: string;
  label: string;
  value: number;
  delta: number;
}

export interface GrowthTrendData {
  domain: string;
  direction: "ACCELERATING" | "STEADY" | "DEVELOPING" | "NEEDS_SUPPORT";
  score: number;
  velocity: number;
  totalMilestones: number;
}

export interface GrowthInsightItem {
  id: string;
  type: string;
  title: string;
  description: string;
  confidence: "HIGH" | "MEDIUM" | "LOW";
}

export interface FormativeMilestoneItem {
  id: string;
  code: string;
  title: string;
  achievedAt: string;
}

interface GrowthJourneyDashboardProps {
  studentName?: string;
  metrics: GrowthMetricItem[];
  trend: GrowthTrendData;
  insights: GrowthInsightItem[];
  milestones: FormativeMilestoneItem[];
}

export const GrowthJourneyDashboard: React.FC<GrowthJourneyDashboardProps> = ({
  studentName = "دانش‌آموز کوشای کدشو",
  metrics,
  trend,
  insights,
  milestones,
}) => {
  return (
    <div className={styles.container} data-testid="p3-vs13-growth-dashboard">
      <header className={styles.header}>
        <h1 className={styles.title}>مسیر و بینش‌های هوشمند رشد یادگیری</h1>
        <p className={styles.subtitle}>
          تحلیل پیشرفت فردی و تحلیلی مستمر {studentName} بدون مقایسه یا رتبه‌بندی کلاسی؛ تمرکز ۱۰۰٪ بر تسلط و انگیزه یادگیری فردی.
        </p>
      </header>

      <div className={styles.gridTwoCol}>
        {/* Competency & Longitudinal Trends */}
        <section className={styles.card} aria-label="روند رشد و شاخص‌های شایستگی">
          <h2 className={styles.cardTitle}>
            <span>📊</span> شاخص‌های پیشرفت و تسلط مهارتی
          </h2>

          <div className={styles.metricRow}>
            <span className={styles.metricLabel}>وضعیت کلی حرکت و شتاب یادگیری:</span>
            <span
              className={
                trend.direction === "ACCELERATING"
                  ? styles.badgeAccelerating
                  : styles.badgeDeveloping
              }
            >
              {trend.direction === "ACCELERATING" ? "🚀 پرشتاب و پیوسته" : "🌱 در حال توسعه"}
            </span>
          </div>

          <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
            {metrics.map((m) => (
              <div key={m.key} className={styles.metricRow}>
                <span className={styles.metricLabel}>{m.label}</span>
                <span className={styles.metricValue}>
                  <bdi className={styles.bdiWrapper} dir="ltr">
                    {m.value}%
                  </bdi>
                  {m.delta > 0 && (
                    <span style={{ fontSize: "0.8rem", color: "#10b981", marginRight: "0.5rem" }}>
                      (+{m.delta}%)
                    </span>
                  )}
                </span>
              </div>
            ))}
          </div>
        </section>

        {/* Qualitative Formative Insights Feed */}
        <section className={styles.card} aria-label="بینش‌های کیفی یادگیری">
          <h2 className={styles.cardTitle}>
            <span>💡</span> تحلیل‌های کیفی و شخصی‌سازی‌شده
          </h2>

          <div className={styles.insightFeed}>
            {insights.map((ins) => (
              <article key={ins.id} className={styles.insightCard}>
                <h3 className={styles.insightTitle}>{ins.title}</h3>
                <p className={styles.insightDesc}>{ins.description}</p>
                <div style={{ fontSize: "0.75rem", color: "#0284c7", fontWeight: 600 }}>
                  سطح اطمینان تحلیلی: {ins.confidence === "HIGH" ? "بسیار بالا" : "معمولی"}
                </div>
              </article>
            ))}
          </div>
        </section>
      </div>

      {/* Formative Milestone Milestones */}
      <section className={styles.card} aria-label="دستاوردهای مهارتی ثبت‌شده">
        <h2 className={styles.cardTitle}>
          <span>🏆</span> نقاط عطف مهارتی پایدار
        </h2>

        <div className={styles.milestoneTimeline}>
          {milestones.map((ms) => (
            <div key={ms.id} className={styles.milestoneItem}>
              <h3 className={styles.milestoneTitle}>{ms.title}</h3>
              <span className={styles.milestoneDate}>
                تاریخ دستیابی: <bdi className={styles.bdiWrapper} dir="ltr">{ms.achievedAt}</bdi>
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};
